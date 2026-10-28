import os
import time
import platform

print("[*] Mock Infostealer PoC starting...")

# Determine OS and set target path
if platform.system() == "Windows":
    target = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies")
else:
    target = os.path.expanduser("~/.config/google-chrome/Default/Cookies")

print(f"[*] Attempting to steal cookies from: {target}")

try:
    with open(target, 'rb') as f:
        print("[+] Successfully opened database! Simulating data exfiltration...")
        # Hold the file open so the daemon has time to catch and kill this process
        time.sleep(10) 
except FileNotFoundError:
    print("[-] Target database not found. Is Chrome installed?")
except PermissionError:
    print("[-] Access denied.")
except Exception as e:
    print(f"[-] Error: {e}")