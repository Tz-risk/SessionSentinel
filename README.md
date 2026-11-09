<div align="center">

# 🛡️ SessionSentinel

**Dual-Layer Endpoint Defense Against Modern Infostealers and Session Hijacking**

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-818cf8?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Manifest V3](https://img.shields.io/badge/Chrome-Manifest%20V3-c084fc?style=for-the-badge&logo=googlechrome&logoColor=white)](https://developer.chrome.com/docs/extensions/mv3/)
[![Platform](https://img.shields.io/badge/OS-Windows%20%7C%20Linux-38bdf8?style=for-the-badge&logo=linux&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-4ade80?style=for-the-badge)](LICENSE)
[![Creator](https://img.shields.io/badge/Created%20by-Om%20Patel-f472b6?style=for-the-badge)](#author)

*Shred authentication tokens on tab closure and neutralize unauthorized SQLite credential harvesting in under 500ms.*

</div>

## ✨ Overview

**SessionSentinel** is a zero-trust, dual-layer endpoint defense architecture created by **Om Patel**. While traditional endpoint protections often ignore passive file reads inside a user's local profile directory, modern infostealers (*Lumma*, *RedLine*, *Stealc*, *Vidar*) exploit this gap by directly reading Chromium SQLite cookie stores (`Cookies`) or hijacking long-lived authentication tokens left on disk.

SessionSentinel closes this gap by synchronizing **real-time browser token lifecycle shredding** (Manifest V3 Service Worker) with an **out-of-band host OS process interceptor** (`watchdog` + `psutil`) across Windows and Linux.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ S e s s i o n S e n t i n e l   dual-layer endpoint defense   ● ACTIVE · <500ms SLA  │
├───────────────────────────────────────────┬──────────────────────────────────────────────┤
│ LAYER 1 · BROWSER RUNTIME (Manifest V3)   │ LAYER 2 · HOST OS DAEMON (Windows & Linux)   │
│ ╭───────────────────────────────────────╮ │ ╭──────────────────────────────────────────╮ │
│ │ 🌐 Active Tab Map (tabDomains)        │ │ │ 🔒 Target: ...\Default\Network\Cookies   │ │
│ │  ├─ [Tab 104] github.com     ● ACTIVE │ │ │ 📡 Engine: watchdog + 500ms psutil sweep │ │
│ │  ├─ [Tab 108] reddit.com     ✕ CLOSED │ │ │ ✅ Allowed: chrome.exe, msedge.exe       │ │
│ │  ╰─ ▶ Action: purgeCookiesForDomain() │ │ │ 🛡️ Canonical Path Filter: ENABLED        │ │
│ ╰───────────────────────────────────────╯ │ ╰──────────────────────────────────────────╯ │
│ ╭─ TOKEN SHREDDER LOG ──────────────────╮ │ ╭─ LIVE THREAT INTERCEPTION ───────────────╮ │
│ │ [✓] Shredded: loid       (reddit.com) │ │ │ [!] ALERT: Unauthorized SQLite Read!     │ │
│ │ [✓] Shredded: csv        (reddit.com) │ │ │  ├─ Rogue Process: python.exe (PID 26840)│ │
│ │ [✓] Shredded: edgebucket (reddit.com) │ │ │  ├─ Vector: Read-Only Handle ('rb')      │ │
│ │ [✓] Shredded: ads_cookie (reddit.com) │ │ │  ╰─ Status: ☠️ TERMINATED (SIGKILL)      │ │
│ ╰───────────────────────────────────────╯ │ ╰──────────────────────────────────────────╯ │
└───────────────────────────────────────────┴──────────────────────────────────────────────┘
```

## 🌟 Key Features

- **🔥 Automated Tab-Close Token Shredding (Layer 1)**
  Actively tracks tab lifecycles and domain mappings in real time via a Manifest V3 Service Worker (`background.js`). The instant a tab is closed, SessionSentinel queries the browser cookie store, reconstructs the exact `http://` or `https://` origin URL, and purges every associated session token from disk.
- **⚡ Sub-500ms Infostealer Process Neutralization (Layer 2)**
  Operates out-of-band on Windows (`monitor_win.py`) and Linux (`monitor_linux.py`). Any unauthorized non-browser process that opens a read handle to the Chrome `Cookies` database is immediately identified by PID and terminated via `proc.kill()` / `SIGKILL`.
- **🔬 Hybrid NTFS & Handle-Polling Detection Engine**
  Windows NTFS suppresses passive `on_accessed` timestamps for performance, allowing silent `open('rb')` infostealer reads to bypass standard `ReadDirectoryChangesW` listeners. SessionSentinel pairs `watchdog` file-event hooks with an active 0.5-second `psutil` process handle table sweep to guarantee 100% detection of silent reads.
- **🎯 Surgical Canonical Path Normalization (Zero Electron False Positives)**
  Desktop apps built on Electron (*VS Code*, *Discord*, *Spotify*, *Steam*) maintain their own internal Chromium `Cookies` files. SessionSentinel enforces strict canonical path normalization (`os.path.normcase(os.path.abspath(...))`) against the exact primary browser database path so everyday desktop apps are never interrupted.
- **🧪 Built-In Cross-Platform Attack Simulator (`rogue_stealer.py`)**
  Ships with a safe, read-only Proof of Concept (PoC) infostealer simulator in `tests/rogue_stealer.py` so security engineers and reviewers can validate live process termination on both Windows and Linux.

## 🛡️ Defense Matrix & Threat Coverage

| Layer | Component | Target Vector | Mitigation Mechanism | Response Time |
| :-: | :--- | :--- | :--- | :-: |
| `1` | **🌐 Browser Extension** | Post-Session Offline Theft | Hooks `chrome.tabs.onRemoved` & shreds domain tokens via `chrome.cookies.remove` | Instant (`<10ms`) |
| `2` | **🪟 Windows Daemon** | Live SQLite Handle Exfiltration | `watchdog` observer + 500ms `psutil` handle-table sweep & `proc.kill()` | `<500ms` |
| `3` | **🐧 Linux Daemon** | Unauthorized `/proc` File Reads | `inotify` directory hooks + `/proc` descriptor inspection & `SIGKILL` | `<500ms` |
| `4` | **🧪 PoC Simulator** | Defense Validation | Simulates `open(target, 'rb')` credential exfiltration across Windows & Linux | 10s Window |

## 🚀 Installation & Quick Start

### Prerequisites

- **Python 3.9+** (`watchdog`, `psutil`)
- **Google Chrome** or Chromium-based browser (Manifest V3 support)

### 1. Clone the Repository

```bash
git clone https://github.com/Tz-risk/SessionSentinel.git
cd SessionSentinel
```

### 2. Load the Browser Layer (Chrome Extension)

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Toggle on **Developer mode** in the top-right corner.
3. Click **Load unpacked** in the top-left corner and select the `extension/` directory.
4. Click the blue **service worker** link on the SessionSentinel card to watch real-time cookie shredding logs.

### 3. Run the Host OS Layer (Daemon)

#### Windows (One-Step Launcher)

```powershell
.\daemon\windows\install.bat
```

*(Automatically installs dependencies from `requirements.txt` and launches the Windows protection daemon.)*

#### Cross-Platform (Windows PowerShell & Linux Bash via `.venv`)

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r daemon\requirements.txt

python daemon\windows\monitor_win.py
```

```bash
# Linux (Bash)
python3 -m venv .venv
source .venv/bin/activate
pip install -r daemon/requirements.txt

python3 daemon/linux/monitor_linux.py
```

## 🧪 Live Verification & PoC Simulation

### 1. Verify Browser Token Shredding
Open a test tab (e.g., `https://reddit.com`), allow it to load, and close the tab. Inspect the Extension Service Worker console:

```text
[SessionSentinel] Tab closed. Purging session data for: reddit.com
[SessionSentinel] Shredded token: loid for https://reddit.com/
[SessionSentinel] Shredded token: csv for https://reddit.com/
[SessionSentinel] Shredded token: edgebucket for https://reddit.com/
[SessionSentinel] Shredded token: ads_cookie for http://www.reddit.com/
```

### 2. Verify OS Daemon Infostealer Neutralization
Run the OS daemon in **Terminal 1**, release Chrome's exclusive kernel file lock on Windows (`taskkill /F /IM chrome.exe /T`), and launch the mock infostealer in **Terminal 2**:

```powershell
# Terminal 2: Launch the simulated credential stealer
python tests\rogue_stealer.py
```

Within 500ms, **Terminal 1** spots the unauthorized handle and terminates the process:

```text
[*] SessionSentinel OS Daemon (Windows) started.
[*] Monitoring exact target: C:\Users\Risk\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies

[ALERT] Unauthorized infostealer read detected!
 -> Process: python.exe (PID: 26840)
 -> Action: Attempting to terminate rogue process...
 -> Status: Process terminated successfully.
```

## 🏗️ Project Structure

```text
SessionSentinel/
├── extension/
│   ├── manifest.json        # Manifest V3 configuration & host permissions
│   ├── background.js        # Service Worker for tab-to-domain mapping & token shredding
│   ├── content.js           # DOM-level session context hooks
│   └── icons/               # Extension assets
├── daemon/
│   ├── requirements.txt     # Runtime dependencies (watchdog==3.0.0, psutil==5.9.6)
│   ├── windows/
│   │   ├── monitor_win.py   # Windows hybrid NTFS watcher & 500ms handle-polling daemon
│   │   └── install.bat      # Windows one-step dependency installer & launcher
│   └── linux/
│       ├── monitor_linux.py # Linux inotify watcher & /proc descriptor scanner
│       └── sentinel.service # systemd background service unit
├── tests/
│   └── rogue_stealer.py     # Cross-platform PoC infostealer simulator
├── .gitignore               # Excludes .venv/, __pycache__/, and OS artifacts
└── README.md                # Project documentation
```

## 🔒 Monitored Credential Stores

SessionSentinel automatically resolves and monitors the canonical SQLite cookie store for your active OS:

- **Windows:**
  - `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies`
- **Linux:**
  - `~/.config/google-chrome/Default/Cookies`
  - `~/.config/google-chrome/Default/Network/Cookies`
  - `~/.config/chromium/Default/Cookies`

## 👨‍💻 Author
**Om Patel**  
*Cybersecurity (Honours) Undergraduate | Carleton University*
- **LinkedIn:** [www.linkedin.com/in/om-patel-1806-bcyber](https://www.linkedin.com/in/om-patel-1806-bcyber)
- **Email:** [ompatel14@cmail.carleton.ca](mailto:ompatel14@cmail.carleton.ca)
- **Personal Email:** [om1806patel@gmail.com](mailto:om1806patel@gmail.com)

## 📄 License

This project is licensed under the [MIT License](LICENSE). © Om Patel.