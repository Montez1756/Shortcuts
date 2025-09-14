from PyQt5.QtCore import pyqtSignal, QThread, QObject
import sys, time
OS = sys.platform
if OS == "win32":
    import wmi, pythoncom, win32process
class Automator(QObject):
    run_signal = pyqtSignal(QObject, list)
    error_signal = pyqtSignal(str)
    def __init__(self, shortcuts):
        super().__init__(None)
        self.shortcuts = shortcuts
        self.monitors = [
            {
                "name":"app",
                "monitor":AppMonitor
            }
        ]

    def loadMonitors(self):
        for monitor in self.monitors:
            temp = []
            for shortcut in self.shortcuts:
                if getattr(shortcut, 'monitor', None) == monitor['name']:
                    temp.append(shortcut)
            new_monitor = getattr(self, monitor['name'], None)
            if new_monitor:
                new_monitor.shortcuts = temp
                new_monitor.reload()
                return
            else:
                new_monitor = monitor['monitor'](temp)
                setattr(self, monitor['name'], new_monitor)
                new_monitor.run_signal.connect(self.run_signal.emit)
        
    def reload(self):
        self.loadMonitors()

class Monitor(QObject):

    run_signal = pyqtSignal(QObject, list)
    error_signal = pyqtSignal(str)
    def __init__(self, shortcuts):
        super().__init__(None)
        self.shortcuts = shortcuts

        thread = QThread(self)

        self.moveToThread(thread)

        if OS == "win32":
            thread.started.connect(self.startMonitor)
        else:
            thread.started.connect(self.startMonitor_l)
        thread.start()

    def error(self, e):
        self.error_signal.emit(e)

    def startMonitor(self):
        raise NotImplementedError
    def startMonitor_l(self):
        raise NotImplementedError
    def reload(self):
        raise NotImplementedError
    
class AppMonitor(Monitor):
    
    def __init__(self, shortcuts):
        super().__init__(shortcuts)

    
    def startMonitor(self):

        pythoncom.CoInitialize()
        try:

            c = wmi.WMI()

            process_watcher = c.Win32_Process.watch_for("creation")

            while True:
                new_process = process_watcher() 
                name = new_process.Caption
                pid = new_process.ProcessId
                try:
                    parent_pid = win32process.GetParentProcessId(pid)
                    continue
                except:
                    for shortcut in self.shortcuts:
                        if shortcut.app == name:
                            self.run_signal.emit(shortcut, ['-process', name, pid])

                time.sleep(0.5)
        except wmi.x_wmi as e:
            self.error(e)
        except Exception as e:
            self.error(e)
    def reload(self):
        pass