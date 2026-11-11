import os
import sys
import time
import signal
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Standard paths for Chrome/Chromium cookies database on Linux
CHROME_PATHS = [
    os.path.expanduser("~/.config/google-chrome/Default/Cookies"),
    os.path.expanduser("~/.config/google-chrome/Default/Network/Cookies"),
    os.path.expanduser("~/.config/chromium/Default/Cookies")
]

EXACT_TARGET_PATH = next((os.path.abspath(p) for p in CHROME_PATHS if os.path.exists(p)), os.path.abspath(CHROME_PATHS[0]))
CHROME_DIR = os.path.dirname(EXACT_TARGET_PATH)

# Authorized Linux browser binaries
AUTHORIZED_PROCS = {"chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"}

def scan_and_kill_rogue_processes():
    """Sweeps /proc via psutil for unauthorized file descriptors pointing to the Cookies DB."""
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pid = proc.info['pid']
            if pid == current_pid:
                continue

            proc_name = (proc.info['name'] or "").lower()
            if proc_name in AUTHORIZED_PROCS:
                continue

            for f in proc.open_files():
                if os.path.abspath(f.path) == EXACT_TARGET_PATH:
                    print(f"\n[ALERT] Unauthorized infostealer read detected on Linux!")
                    print(f" -> Process: {proc.info['name']} (PID: {pid})")
                    print(f" -> Target:  {f.path}")
                    print(f" -> Action:  Sending SIGKILL to rogue process...")
                    
                    os.kill(pid, signal.SIGKILL)
                    
                    print(f" -> Status:  Process terminated successfully.\n")
                    break

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

class LinuxCookieMonitorHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if os.path.abspath(event.src_path) == EXACT_TARGET_PATH:
            scan_and_kill_rogue_processes()

if __name__ == "__main__":
    print("[*] SessionSentinel OS Daemon (Linux) started.")
    print(f"[*] Monitoring exact target: {EXACT_TARGET_PATH}")

    if not os.path.exists(CHROME_DIR):
        print(f"[-] Target directory not found: {CHROME_DIR}")
        sys.exit(1)

    event_handler = LinuxCookieMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, CHROME_DIR, recursive=False)
    observer.start()

    try:
        while True:
            scan_and_kill_rogue_processes()
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Shutting down Linux daemon.")

    observer.join()