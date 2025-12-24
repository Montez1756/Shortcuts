from configparser import ConfigParser
import os.path, json, glob, sys

def getIniConfig(filename : str):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found : {filename}")
    config = ConfigParser()
    config.read(filename)
    return config
    

def getShortcutConfig(shortcut_path):
    if not os.path.exists(shortcut_path):
        raise FileNotFoundError(f"File not found : {shortcut_path}")
    
    def getFile(path):
        file = glob.glob(path)
        if file:
            return file[0]
        return ""

    shortcut_file = getFile(os.path.join(shortcut_path, "file/*.py"))

    shortcut_icon = getFile(os.path.join(shortcut_path, "icon/*.*"))

    shortcut_info = getFile(os.path.join(shortcut_path, "info.json"))

    shortcut_venv = "" 
    if sys.platform == "win32":
        window_venv = os.path.join(shortcut_path, "venv/Scripts/python.exe")
        if os.path.exists(window_venv):
            shortcut_venv = window_venv
    elif sys.platform == "linux":
        linux_venv = os.path.join(shortcut_path, "venv/bin/python")
        if os.path.exists(linux_venv):
            shortcut_venv = linux_venv

    if shortcut_info:
        with open(shortcut_info, "r") as file:
            shortcut_json = json.loads(file.read())
    shortcut_json["file"] = shortcut_file
    shortcut_json["icon"] = shortcut_icon
    shortcut_json["venv"] = shortcut_venv

    return shortcut_json
