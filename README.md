# 🖇️ Shortcuts for Windows (iOS Shortcuts Replica)

A desktop automation framework inspired by **iOS Shortcuts**, starting on **Windows** with plans for **Linux** support in the future.  
This project allows you to build, trigger, and run shortcuts that can automate apps, scripts, and system events.

---

## ✨ Current Features (Windows)

### Shortcuts (`shortcut.py`)
- 🎯 Each shortcut is defined by:
  - `file` → Python/BAT/script file to run  
  - `info` → metadata JSON (name, description, background color, automation type, etc.)  
  - `icon` → optional icon image for display  
  - `python` → interpreter to use (per-shortcut venv supported)  
- 📦 Drag & Drop support → pass files to shortcuts directly  
- 🖼️ Custom icons and background colors  
- 📝 Tooltips with description and metadata  

### Console (`console.py`)
- 🖥️ **Interactive Console** for running shortcuts  
- 🔎 Captures stdout/stderr with real-time display  
- 🎞️ Media integration → display images, videos, or text output inside the console  
- ⌨️ Supports **prompt input** (shortcuts can request user input dynamically)  
- ❌ Clean process management (terminate, kill, restart)  

### Automation (`automation.py`)
- ⚙️ **Automator** engine that manages monitors and triggers  
- 👀 **AppMonitor** → watches for process launches via WMI; triggers shortcuts when specific apps start  
- 🌐 **RequestMonitor** → polls URLs and triggers shortcuts based on responses  
- 🔄 Independent execution threads for each automation  
- ✅ Restartable and stoppable monitors  

---

## 📌 Planned Features

### Near-Term (Windows)
- 🔌 Extensible action plugins  
- ⏰ Scheduling & triggers (time, idle, system events)  
- 🖼️ More shortcut UI customization (layouts, grouping)  
- ☁️ Export/import shortcuts for sharing  

### Future (Linux)
- 🔧 Shortcut execution via Bash/Python scripts  
- 🗂️ Integrations with systemd, cron, DBus signals  
- 🔌 Unified automation monitors (processes, network, filesystem)  

---

## 🚀 Getting Started

### Requirements
- **Windows 10/11**  
- Python 3.12+  

### Install
```bash
git clone https://github.com/Montez1756/Shortcuts.git
cd Shortcuts
pip install -r requirements.txt
python main.py
