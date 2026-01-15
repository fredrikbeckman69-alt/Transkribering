import time
import os
import subprocess
from datetime import datetime

WATCH_DIR = "."
POLL_INTERVAL = 10  # Check every 10 seconds

def get_last_modified_time():
    last_mtime = 0
    for root, dirs, files in os.walk(WATCH_DIR):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            path = os.path.join(root, f)
            try:
                mtime = os.path.getmtime(path)
                if mtime > last_mtime:
                    last_mtime = mtime
            except OSError:
                continue
    return last_mtime

def git_push():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Changes detected. Syncing...")
    
    # Git commands
    commands = [
        ['git', 'add', '.'],
        ['git', 'commit', '-m', f"Auto-sync: {timestamp}"],
        ['git', 'push', 'origin', 'main']
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            pass # Ignore errors (e.g. nothing to commit)

print("Starting Auto-Sync Watcher...")
last_known_mtime = get_last_modified_time()

while True:
    time.sleep(POLL_INTERVAL)
    current_mtime = get_last_modified_time()
    
    if current_mtime > last_known_mtime:
        # Wait a bit more to ensure writes are finished
        time.sleep(2)
        git_push()
        last_known_mtime = get_last_modified_time()
