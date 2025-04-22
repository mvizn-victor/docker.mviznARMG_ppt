import os
import pickle
import fcntl
import time
from contextlib import contextmanager

class PersistentDict:
    def __init__(self, filename):
        self.filename = filename
        self._data = {}
        self._updatetime = {}
        self._deleted = {}  # key: timestamp of deletion
        self._ensure_file_exists()
        self.sync_down()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            with open(self.filename, 'wb') as f:
                pickle.dump({'data': {}, 'updatetime': {}, 'deleted': {}}, f)

    @contextmanager
    def _file_lock(self):
        with open(self.filename, 'rb+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            yield f
            fcntl.flock(f, fcntl.LOCK_UN)

    def sync_down(self):
        with self._file_lock() as f:
            try:
                saved = pickle.load(f)
                disk_data = saved.get('data', {})
                disk_time = saved.get('updatetime', {})
                disk_deleted = saved.get('deleted', {})

                # Handle deletes
                for k, t_del in disk_deleted.items():
                    t_local = self._updatetime.get(k, 0)
                    if t_del > t_local:
                        self._data.pop(k, None)
                        self._updatetime[k] = t_del
                        self._deleted[k] = t_del

                # Handle additions/updates
                for k, v in disk_data.items():
                    t_disk = disk_time.get(k, 0)
                    t_local = self._updatetime.get(k, 0)
                    t_del = self._deleted.get(k, 0)
                    if t_disk > max(t_local, t_del):
                        self._data[k] = v
                        self._updatetime[k] = t_disk
                        self._deleted.pop(k, None)

            except Exception as e:
                print(f"[sync_down error] {e}")

    def sync_up(self):
        self.sync_down()
        with self._file_lock() as f:
            f.seek(0)
            pickle.dump({
                'data': self._data,
                'updatetime': self._updatetime,
                'deleted': self._deleted
            }, f)
            f.truncate()

    def __setitem__(self, key, value):
        self._data[key] = value
        t = time.time()
        self._updatetime[key] = t
        self._deleted.pop(key, None)

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        if key in self._data:
            t = time.time()
            del self._data[key]
            self._deleted[key] = t
            self._updatetime[key] = t

    def get(self, key, default=None):
        return self._data.get(key, default)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def last_updated(self, key):
        return self._updatetime.get(key)

    def __contains__(self, key):
        return key in self._data

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"PersistentDict({self._data})"

    def clear(self):
        """Remove all keys and record their deletion."""
        now = time.time()
        for key in list(self._data.keys()):
            self._deleted[key] = now
            self._updatetime[key] = now
        self._data.clear()

    def touch(self, key):
        """Update timestamp without changing the value."""
        if key in self._data:
            self._updatetime[key] = time.time()
        else:
            raise KeyError(f"Cannot touch missing key: {key}")

    def purge_deleted(self, older_than_secs=3600):
        """Clear deleted keys that were removed more than `older_than_secs` ago."""
        now = time.time()
        keys_to_purge = [k for k, t in self._deleted.items() if now - t > older_than_secs]
        for k in keys_to_purge:
            self._deleted.pop(k, None)
            self._updatetime.pop(k, None)
