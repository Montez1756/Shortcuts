from PyQt5.QtCore import QThread, QTimer, QObject, pyqtSignal
from shortcut import Shortcut
import sys, time, psutil, requests

OS = sys.platform

if OS == 'win32':
    import wmi, pythoncom
elif OS == 'linux':
    from Xlib import X, display, Xatom
class Automator(QObject):

    def __init__(self, automations, parent = None):
        super().__init__(parent)
        self._parent = parent
        self.automations = automations
        # print(automations)
        self.initMonitors()
        # self.app_monitor = None
        # self.request_monitor = None

    def initMonitors(self):
        monitor_list = [
            {
                "key":"app",
                "class":AppMonitor,
                "attr":"app_monitor"
            },
            {
                "key":"request",
                "class":RequestMonitor,
                "attr":"request_monitor"
            }
            ]
        for monitor in monitor_list:
            temp = [automation for automation in self.automations if automation.json.get('automation') == monitor['key']]
            if temp:
                monitor_check = getattr(self, monitor['attr'], None)
                if monitor_check:
                    if hasattr(monitor_check, 'stop'):
                        monitor_check.stop()
                    monitor_check.deleteLater()
                setattr(self, monitor['attr'], monitor['class'](temp, self))
                new_monitor = getattr(self, monitor["attr"], None)
                if new_monitor:
                    if getattr(self._parent, 'console', None):
                            new_monitor.run_signal.connect(self._parent.console.runAutomation)
                    
    def reload(self):
        self.initMonitors()

def is_independent_launch(pid, target_name):
    """Return True if the process was launched independently (not as a child of the same exe)."""
    try:
        p = psutil.Process(pid)
        parent = p.parent()
        if parent and parent.name().lower() == target_name.lower():
            return False
    except Exception:
        pass
    return True

class Monitor(QObject):
    run_signal = pyqtSignal(str, str, list, QObject)
    # run_signal_pid = pyqtSignal(str, str, list, QObject)
    def __init__(self, automations, parent = None):
        super().__init__(None)
        self.automations  = automations
        self.needInt = False
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.runMonitor)
        self._thread.start()

    def runMonitor(self):
        raise NotImplementedError
    def handleDone(self):
        pass
    def stop(self):
        self._thread.quit()
        # raise NotImplementedError

if OS == 'linux':
    def get_window_pid(d, window):
        NET_WM_PID = d.intern_atom('_NET_WM_PID')
        pid_prop = window.get_full_property(NET_WM_PID, Xatom.CARDINAL)
        if pid_prop:
            return pid_prop.value[0]
        return None

class AppMonitor(Monitor):
    def __init__(self, automations, parent=None):
        super().__init__(automations, parent)
        self.current_programs = {}
        self.needInt = True
    if OS == 'win32':
        def runMonitor(self):
            try:
                pythoncom.CoInitialize()
                c = wmi.WMI()
                process_watcher = c.Win32_Process.watch_for('creation')
                while True:
                    new_process = process_watcher()
                    pid = new_process.ProcessId
                    name = new_process.Name

                    if pid not in self.current_programs:
                        for automation in self.automations:
                            if automation.json.get('app') == name:
                                if is_independent_launch(pid, name):
                                    self.current_programs[pid] = name
                                    exe = automation.python
                                    file = automation.file
                                    args = ['-p', name, str(pid)]
                                    print(f"Launching automation for {name} (pid {pid})")
                                    self.run_signal.emit(exe, file, args, self)
                    time.sleep(0.2)

            except Exception as e:
                print(f"AppMonitor error: {e}")
    elif OS == 'linux':
        def runMonitor(self):
            try:
                d = display.Display()
                root = d.screen().root
                root.change_attributes(event_mask=X.SubstructureNotifyMask)

                while True:
                    e.d.next_event()
                    if e.type == X.CreateNotify:
                        name = e.window.id

                        for automation in self.automations:
                            if automation.json.get('app') == name:
                                exe = automation.python
                                file = automation.file
                                args = ['-p', name, str(get_window_pid(d, e.window))]
                                self.run_signal.emit(exe, file, args, self)
            except Exception as e:
                print(f"AppMonitor error: {e}")
    def handleDone(self, pid: int):
        """Called when Console/ProcessThread finishes automation."""
        if pid in self.current_programs:
            name = self.current_programs.pop(pid)
            print(f"Automation done for {name} (pid {pid})")
        else:
            print(f"handleDone called for unknown pid {pid}")
    def stop(self):
        return super().stop()

class RequestWorker(QObject):
    run_signal  = pyqtSignal(Shortcut)
    error_signal = pyqtSignal(str)
    stop_signal = pyqtSignal()
    restart_signal = pyqtSignal(int)
    def __init__(self, automation, parent=None):
        super().__init__(None)
        self.automation = automation
        self.var = self.automation.json.get('var')
        self.duration = self.automation.json.get('duration') or 1000
        self.url = self.automation.json.get('url')
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.handleRequest)
    def start(self):
        if not self.url or not self.var:
            self.error_signal.emit(f"Could not find url in automation: {self.automation.json.get('name')}")
            return
        self.timer = QTimer()
        self.timer.timeout.connect(self.handleRequest)
        self.timer.start(self.duration)
        self.restart_signal.connect(self.timer.start)
    def handleRequest(self):
          print('Hello')
          with requests.get(self.url, timeout=10, allow_redirects=True, stream=True) as r:
                    if self.var == r.text:
                        self.run_signal.emit(self.automation)
                        self.timer.stop()
        # self.timer.start(self.duration)
    # def handleRequest(self):
    #     with requests.get(self.url, timeout=10, allow_redirects=True, stream=True) as r:
    #         if self.var in r.text:
    #             self.run_signal.emit()
    def restart(self):
        self.timer.start(self.duration)
    def stop(self):
        # self.timer.stop()
        self.stop_signal.emit()
class RequestMonitor(Monitor):
    def __init__(self, automations, parent=None):
        super().__init__(automations, parent)
        self.workers = []
    def runMonitor(self):
        for automation in self.automations:
            thread = QThread(self)
            worker = RequestWorker(automation, self)
            worker.run_signal.connect(self.handleRequest)
            # worker.error_signal.connect()
            self.workers.append(worker)
            worker.moveToThread(thread)
            thread.started.connect(worker.start)
            worker.stop_signal.connect(thread.quit)
            thread.start()
    def handleRequest(self, automation):
        exe = automation.python
        file = automation.file
        args = [file]
        self.run_signal.emit(exe, file, args, self)
        print(args)
    def handleDone(self, file):
        for worker in self.workers:
            if worker.automation.file == file:
                worker.restart_signal.emit(worker.duration)
        # return super().handleDone()
    def stop(self):
        for worker in self.workers:
            worker.stop()
        return super().stop()