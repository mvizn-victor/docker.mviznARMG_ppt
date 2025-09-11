#!/usr/bin/env bash
# setupraid.sh - Create /dev/md0 RAID1 from two ~3.7T disks and mount at /opt.
# Usage: sudo bash setupraid.sh -y
set -euo pipefail

# -------- Config (tweak if needed) --------
MOUNT_POINT="/opt"
ARRAY_DEV="/dev/md0"
RAID_LEVEL="1"
FSTYPE="ext4"
FSTAB_OPTS="defaults,nofail,discard"
NAME_SUFFIX=":0"  # mdadm --name will be "$(hostname)${NAME_SUFFIX}"

# -------- Helpers --------
die() { echo "ERROR: $*" >&2; exit 1; }
need_root() { [[ "${EUID:-$(id -u)}" -eq 0 ]] || die "Run as root (use sudo)."; }

confirm_flag=false
if [[ "${1:-}" == "-y" ]]; then
  confirm_flag=true
fi

need_root

# Ensure required tools
if ! command -v mdadm >/dev/null 2>&1; then
  echo "mdadm not found. Installing..."
  if command -v apt-get >/dev/null 2>&1; then
    DEBIAN_FRONTEND=noninteractive apt-get update -y
    DEBIAN_FRONTEND=noninteractive apt-get install -y mdadm
  else
    die "mdadm is required. Please install it and re-run."
  fi
fi

command -v lsblk >/dev/null 2>&1 || die "lsblk is required."
command -v blkid >/dev/null 2>&1 || die "blkid is required."
command -v findmnt >/dev/null 2>&1 || die "findmnt is required."

# Detect the OS/root base disk to exclude it
root_src="$(findmnt -no SOURCE / || true)"  # e.g., /dev/sdc2
root_base=""
if [[ -n "$root_src" && "$root_src" =~ ^/dev/ ]]; then
  # Strip partition number (e.g., /dev/sdc2 -> sdc)
  root_base="$(basename "$root_src" | sed -E 's/p?[0-9]+$//')"
fi

# Gather candidate disks (~3.7T). Use bytes for robust filtering: >= 3.5T (3.5 * 10^12)
# Only TYPE=disk and without current mounts.
mapfile -t disks < <(
  lsblk -bdn -o NAME,SIZE,TYPE | awk '
    $3=="disk" && $2>=3500000000000 {print $1" "$2}
  ' | sort -k2,2nr | awk '{print $1}'
)

# Exclude the root base disk if present
if [[ -n "$root_base" ]]; then
  disks=( "${disks[@]/$root_base}" )
fi

# Further ensure these disks are not currently mounted and have no partitions in use
eligible=()
for d in "${disks[@]}"; do
  [[ -z "$d" ]] && continue
  # If the disk has partitions, we still *can* use whole-disk with mdadm,
  # but it's safer to skip disks that have existing mounted partitions.
  # Check if any child is mounted:
  have_mounted_child=false
  while IFS= read -r line; do
    part="$(awk '{print $1}' <<<"$line")"
    mnt="$(awk '{print $2}' <<<"$line")"
    if [[ -n "$mnt" && "$mnt" != "-" ]]; then
      have_mounted_child=true
      break
    fi
  done < <(lsblk -nr -o NAME,MOUNTPOINT "/dev/$d")

  $have_mounted_child && continue
  eligible+=("$d")
done

if (( ${#eligible[@]} < 2 )); then
  echo "Detected disks (bytes >= 3.5T, excluding root): ${eligible[*]:-<none>}"
  die "Need at least two eligible ~3.7T disks."
fi

# Pick the top two by size (already sorted above); keep order stable
DISK1="/dev/${eligible[0]}"
DISK2="/dev/${eligible[1]}"

echo "Selected disks for RAID1:"
echo "  DISK1: $DISK1"
echo "  DISK2: $DISK2"

# Safety: require explicit -y
if ! $confirm_flag; then
  echo
  echo "Dry-run summary (no changes made). To proceed, run: sudo bash $0 -y"
  exit 0
fi

# Check if array already exists
if [[ -e "$ARRAY_DEV" ]]; then
  die "$ARRAY_DEV already exists. Aborting to avoid clobbering."
fi

# Create the array
ARRAY_NAME="raid1"
echo "Creating RAID${RAID_LEVEL} array $ARRAY_DEV from $DISK1 and $DISK2..."
mdadm --create --verbose "$ARRAY_DEV" \
  --level="$RAID_LEVEL" \
  --raid-devices=2 \
  --metadata=1.2 \
  --name "$ARRAY_NAME" \
  "$DISK1" "$DISK2"

# Wait for md device to appear and start
udevadm settle || true
sleep 2

# Make filesystem
echo "Formatting $ARRAY_DEV as $FSTYPE..."
mkfs."$FSTYPE" -F "$ARRAY_DEV"

# Create mount point
mkdir -p "$MOUNT_POINT"

# Get UUID and write /etc/fstab (idempotent)
UUID="$(blkid -s UUID -o value "$ARRAY_DEV")"
[[ -z "$UUID" ]] && die "Failed to read UUID from $ARRAY_DEV"

FSTAB_LINE="UUID=$UUID $MOUNT_POINT $FSTYPE $FSTAB_OPTS 0 0"

echo "Backing up /etc/fstab to /etc/fstab.bak.$(date +%s)"
cp -a /etc/fstab "/etc/fstab.bak.$(date +%s)"

if grep -qE "^[^#]*[[:space:]]$MOUNT_POINT[[:space:]]" /etc/fstab; then
  echo "An fstab entry for $MOUNT_POINT already exists. Leaving it unchanged."
else
  echo "$FSTAB_LINE" >> /etc/fstab
  echo "Added to /etc/fstab:"
  echo "  $FSTAB_LINE"
fi

# Mount all
echo "Mounting $MOUNT_POINT..."
mount -a

# Persist mdadm scan (idempotent)
MDADM_CONF="/etc/mdadm/mdadm.conf"
mkdir -p "$(dirname "$MDADM_CONF")"
echo "Recording array in $MDADM_CONF (if not present)..."
SCAN_LINE="$(mdadm --detail --scan | grep -E "^ARRAY[[:space:]]+$ARRAY_DEV[[:space:]]")" || true

if [[ -n "$SCAN_LINE" ]]; then
  if ! grep -qF "$SCAN_LINE" "$MDADM_CONF" 2>/dev/null; then
    echo "Backing up $MDADM_CONF to ${MDADM_CONF}.bak.$(date +%s)"
    cp -a "$MDADM_CONF" "${MDADM_CONF}.bak.$(date +%s)" 2>/dev/null || true
    echo "$SCAN_LINE" >> "$MDADM_CONF"
    echo "Appended:"
    echo "  $SCAN_LINE"
  else
    echo "ARRAY entry already present."
  fi
else
  echo "Warning: mdadm --detail --scan did not return ARRAY line for $ARRAY_DEV."
fi

# Update initramfs if available (Debian/Ubuntu)
if command -v update-initramfs >/dev/null 2>&1; then
  echo "Updating initramfs..."
  update-initramfs -u
else
  echo "Skipping initramfs update (tool not found)."
fi

echo
echo "=== Done. Verification ==="
echo "df -hx tmpfs | grep -v loop"
df -hx tmpfs | grep -v loop || true

echo
echo "mdadm --detail $ARRAY_DEV"
mdadm --detail "$ARRAY_DEV" || true

echo
echo "lsblk -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINT"
lsblk -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINT

echo
echo "If / is nearly full, consider moving large data into $MOUNT_POINT."

