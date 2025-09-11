
# ============ SETTINGS ============
# Set to "true" to also WIPE WHOLE DISKS that were array members (partition table & all).
FULL_DISK_ZAP="false"

# Require explicit confirmation by setting env var:
: "${I_UNDERSTAND_THIS_WILL_ERASE_DATA:=}"

I_UNDERSTAND_THIS_WILL_ERASE_DATA=YES

if [[ -z "${I_UNDERSTAND_THIS_WILL_ERASE_DATA}" ]]; then
  echo "Refusing to run: set I_UNDERSTAND_THIS_WILL_ERASE_DATA=YES to proceed."
  exit 1
fi

need_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "Missing $1. Install it."; exit 1; }; }

need_cmd mdadm
need_cmd awk
need_cmd sed
need_cmd lsblk
need_cmd wipefs
# sgdisk is optional if FULL_DISK_ZAP=true
if [[ "$FULL_DISK_ZAP" == "true" ]]; then need_cmd sgdisk; fi

echo "=== BEFORE ==="
cat /proc/mdstat || true
echo
lsblk -o NAME,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINT | sed 's/^/  /'

# 1) Enumerate md arrays
mapfile -t MD_DEVS < <(ls /dev/md* 2>/dev/null | grep -E '/dev/md[0-9]+$|/dev/md/' || true)

if (( ${#MD_DEVS[@]} == 0 )); then
  echo "No /dev/md* arrays found. Nothing to stop."
else
  echo "Found md arrays: ${MD_DEVS[*]}"
fi

# 2) Collect member devices from mdadm --detail
declare -A MEMBER_SET=()

for md in "${MD_DEVS[@]}"; do
  if [[ -b "$md" ]]; then
    echo "Inspecting $md"
    # Grab any /dev/* tokens in 'mdadm --detail' output on lines that list devices
    while read -r dev; do
      [[ -b "$dev" ]] && MEMBER_SET["$dev"]=1
    done < <(mdadm --detail "$md" 2>/dev/null | awk '{for(i=1;i<=NF;i++) if ($i ~ "^/dev/") print $i}' | sort -u)
  fi
done

# 3) Stop all md arrays (best-effort)
echo "Stopping all md arrays..."
mdadm --stop --scan || true

# 4) Zero superblocks & wipe signatures on member devices
if (( ${#MEMBER_SET[@]} > 0 )); then
  echo "Member devices to clean: ${!MEMBER_SET[*]}"
else
  echo "No member devices detected from md arrays."
fi

for dev in "${!MEMBER_SET[@]}"; do
  echo "Zeroing RAID superblock on $dev"
  mdadm --zero-superblock --force "$dev" || true

  echo "Wiping filesystem signatures on $dev"
  wipefs -a "$dev" || true
done

# 5) Optional: Zap WHOLE disks that hosted members (e.g., /dev/sdX from /dev/sdXN)
if [[ "$FULL_DISK_ZAP" == "true" && ${#MEMBER_SET[@]} -gt 0 ]]; then
  echo "FULL_DISK_ZAP=true: zapping whole disks that contain member partitions"
  declare -A WHOLE_DISKS=()
  for dev in "${!MEMBER_SET[@]}"; do
    # Get the parent disk (e.g., /dev/sda for /dev/sda1)
    parent="$(lsblk -no PKNAME "$dev" 2>/dev/null || true)"
    if [[ -n "$parent" && -b "/dev/$parent" ]]; then
      WHOLE_DISKS["/dev/$parent"]=1
    fi
  done
  if (( ${#WHOLE_DISKS[@]} > 0 )); then
    echo "Disks to zap: ${!WHOLE_DISKS[*]}"
    for disk in "${!WHOLE_DISKS[@]}"; do
      echo "Zapping partition table on $disk"
      sgdisk --zap-all "$disk" || true
      # Also wipefs just in case any stray sigs
      wipefs -a "$disk" || true
    done
  fi
fi

# 6) Remove mdadm ARRAY stanzas & rebuild initramfs
if [[ -f /etc/mdadm/mdadm.conf ]]; then
  echo "Cleaning /etc/mdadm/mdadm.conf (backing up first)"
  cp /etc/mdadm/mdadm.conf /etc/mdadm/mdadm.conf.bak.$(date +%s) || true
  sed -i '/^ARRAY /d' /etc/mdadm/mdadm.conf || true
fi

echo "Updating initramfs..."
update-initramfs -u || true

# 7) Final verification
echo "=== AFTER ==="
cat /proc/mdstat || true
echo
lsblk -o NAME,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINT | sed 's/^/  /'

echo "Done."

