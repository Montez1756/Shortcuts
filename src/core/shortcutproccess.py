from PyQt5.QtCore import Qt, QObject, QProcess, pyqtSignal, pyqtSlot, QThread


class Worker(QObject):
    stdout = pyqtSignal(str)
    stderr = pyqtSignal(str)
    finished = pyqtSignal()
    force_finished = pyqtSignal()
    def __init__(self, exe : str, args : list, cwd : str):
        super().__init__(None)
        self.exe = exe
        self.args = args
        self.cwd = cwd
        self.process = QProcess(self)
    def run(self):
        
        self.process.setWorkingDirectory(self.cwd)
        self.process.readyReadStandardOutput.connect(self.handleOutput)
        self.process.readyReadStandardError.connect(self.handleError)
        self.process.finished.connect(self.finished.emit)
        self.force_finished.connect(self.process.kill)

        self.process.start(self.exe, self.args)
    def handleOutput(self):
        output = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="ignore").strip()
        print(output)
        self.stdout.emit(output)

    def handleError(self):
        output = bytes(self.process.readAllStandardError()).decode("utf-8", errors="ignore").strip()
        print(output)
        self.stderr.emit(output)

    def write(self, value : str):
        self.process.write(bytes((value + "\n").encode("utf-8")))
        self.process.waitForBytesWritten()

class ShortcutProccess(QObject):
    stdout = pyqtSignal(str)
    stderr = pyqtSignal(str)
    stdipc = pyqtSignal(str)
    stdin = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, exe, args, cwd):
        super().__init__(None)
        self.exe = exe
        self.args = args
        self.cwd = cwd
        self._thread = QThread(self)
        self.worker = Worker(exe, args, cwd)

    def start(self):
        self.worker.moveToThread(self._thread)

        self.worker.stdout.connect(self.handleStdout)
        self.worker.stderr.connect(self.stderr.emit)
        self.stdin.connect(self.worker.write)
        self.worker.finished.connect(self._thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.finished.emit)

        self._thread.started.connect(self.worker.run)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def handleStdout(self, value : str):
        for line in value.splitlines():
            if line.startswith("{EMC}"):
                self.stdipc.emit(line.split("{EMC}", 1)[1])
            else:
                self.stdout.emit(line)
    def kill(self):
        self.worker.force_finished.emit()
