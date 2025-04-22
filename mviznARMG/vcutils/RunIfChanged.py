try:
    from .helperfun import *
    #print('from .helperfun import *')
except:
    try:
        from vcutils.helperfun import *        
        #print('from vcutils.helperfun import *')
    except:
        raise

class RunIfChanged:
    def __init__(self, pyfile):
        self.pyfile = pyfile
        self.trackedfiles = {pyfile}
        self.lastmtimes = {}
        for f in self.trackedfiles:
            self.lastmtimes[f] = os.path.getmtime(f) if os.path.exists(f) else 0

    def add(self, filepath):
        """Add a new file to track."""
        self.trackedfiles.add(filepath)
        self.lastmtimes[filepath] = os.path.getmtime(filepath) if os.path.exists(filepath) else 0

    def runifchanged(self, env=None):
        changed = False
        for f in self.trackedfiles:
            try:
                current_mtime = os.path.getmtime(f)
                if current_mtime != self.lastmtimes.get(f, 0):
                    changed = True
                    self.lastmtimes[f] = current_mtime
            except FileNotFoundError:
                continue
        if changed:
            print(f"Change detected in tracked files. Re-running {self.pyfile}...")
            ipyrun(self.pyfile,env)
    def checkchange(self):
        changed = False
        for f in self.trackedfiles:
            try:
                current_mtime = os.path.getmtime(f)
                if current_mtime != self.lastmtimes.get(f, 0):
                    changed = True                    
            except FileNotFoundError:
                continue
        return changed