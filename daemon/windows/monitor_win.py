import os
import time
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Standard path for the Chrome cookies database on Windows
CHROME_NETWORK_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network")
TARGET_FILE = "Cookies"
# FIX: Define the exact absolute path to prevent killing other Electron apps
EXACT_TARGET_PATH = os.path.join(CHROME_NETWORK_DIR, TARGET_FILE)

AUTHORIZED_PROCS = ["chrome.exe", "msedge.exe"]

class CookieMonitorHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == EXACT_TARGET_PATH:
            self.detect_unauthorized_access()

    def on_accessed(self, event):
        if event.src_path == EXACT_TARGET_PATH:
            self.detect_unauthorized_access()

    def detect_unauthorized_access(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() in AUTHORIZED_PROCS:
                    continue
                    
                open_files = proc.open_files()
                for f in open_files:
                    # FIX: Match the precise file path, not just the string "Cookies"
                    if f.path == EXACT_TARGET_PATH:
                        print(f"\n[ALERT] Unauthorized infostealer read detected!")
                        print(f" -> Process: {proc.info['name']} (PID: {proc.info['pid']})")
                        print(f" -> Action: Attempting to terminate rogue process...")
                        
                        proc.kill()
                        
                        print(f" -> Status: Process terminated successfully.\n")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

if __name__ == "__main__":
    print(f"[*] SessionSentinel OS Daemon (Windows) started.")
    print(f"[*] Monitoring exact target: {EXACT_TARGET_PATH}")
    
    if not os.path.exists(CHROME_NETWORK_DIR):
        print("[-] Target directory not found. Is Chrome installed?")
        exit(1)

    event_handler = CookieMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, CHROME_NETWORK_DIR, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Shutting down daemon.")
    
    observer.join()