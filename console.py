import os, sys, json, shutil
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QPushButton, QStyle, QVBoxLayout, QApplication,
    QLabel, QSizePolicy, QInputDialog
)
from PyQt5.QtCore import (Qt, QTimer, QProcess, QUrl, pyqtSignal, QThread, pyqtSlot,
                          QObject,)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QPixmap


class Media(QWidget):
    def __init__(self, parent: QWidget = None, file: str = ""):
        super().__init__(parent)
        self._parent = parent
        self.setStyleSheet('background-color:black;')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file = file

        # Normalize extension handling
        self._ext = os.path.splitext(self.file)[1].lower()

        self.videoExtensions = {'.mp4', '.mov', '.wmv', '.avi', '.mkv', '.webm', '.flv', '.m4v', '.3gp', '.ogg', '.ogv', '.ts'}
        # Keep to common raster formats that QPixmap usually supports
        self.imgExtensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff', '.tif', '.bmp', '.ico'}
        self.textExtensions = {'.txt'}

        self.type = self.getType()
        self.mediaElement = None
        self.mediaPlayer = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.handleType()
        self.show()
        if self.mediaElement:
            self.mediaElement.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.mediaElement.raise_()

    def handleType(self):
        if self.type == 'text':
            try:
                with open(self.file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                content = f"Failed to read file:\n{e}"
            self.mediaElement = QTextEdit(self)
            self.mediaElement.setReadOnly(True)
            self.mediaElement.setPlainText(content)

        elif self.type == 'video':
            self.mediaPlayer = QMediaPlayer(self)
            self.mediaElement = QVideoWidget(self)
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(self.file))))
            self.mediaPlayer.setVideoOutput(self.mediaElement)
            self.mediaPlayer.play()

        elif self.type == 'image':
            pixmap = QPixmap(self.file)
            if not pixmap.isNull():
                self.mediaElement = QLabel(self)
                self.mediaElement.setAlignment(Qt.AlignCenter)
                self.mediaElement.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        if self.mediaElement:
            self.layout().addWidget(self.mediaElement)
            self.mediaElement.show()

    def getType(self):
        if self._ext in self.videoExtensions:
            return 'video'
        if self._ext in self.imgExtensions:
            return 'image'
        if self._ext in self.textExtensions:
            return 'text'
        return 'unknown'

    def stop(self):
        if self.type == 'video' and self.mediaPlayer:
            self.mediaPlayer.stop()

    def resizeEvent(self, ev):
        if isinstance(self.mediaElement, QLabel):
            pixmap = QPixmap(self.file)
            if not pixmap.isNull():
                self.mediaElement.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super().resizeEvent(ev)



class ProcessWorker(QObject):
    text_signal = pyqtSignal(str)
    display_signal = pyqtSignal(str)
    prompt_signal = pyqtSignal(str)
    finished = pyqtSignal(int, int)   # (exitCode, exitStatus)
    
    def __init__(self, exe, file, args):
        super().__init__()
        self.exe = exe
        self.file = file
        self.args = args
        self.process = None

    @pyqtSlot()
    def start(self):
        # Create QProcess *in this thread*, parented to this worker
        self.process = QProcess(self)
        self.text_signal.emit(f"Running {self.file} {self.args}...\n")

        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(
            lambda: self.text_signal.emit(
                bytes(self.process.readAllStandardError()).decode('utf-8', errors='replace').strip()
            )
        )
        self.process.errorOccurred.connect(
            lambda e: self.text_signal.emit(f"Process error: {e}")
        )
        self.process.finished.connect(self._on_finished)

        # flatten args like you had
        flattened_args = [a for arg in self.args for a in (arg if isinstance(arg, list) else [arg])]

        # start
        if self.file.endswith('.py'):
            exe = self.exe
            if not exe or not shutil.which(exe):
                exe = sys.executable
            self.process.start(exe, [self.file] + flattened_args)
        elif self.file.endswith('.bat'):
            self.process.start('cmd', ['/c', self.file] + flattened_args)  # /c = run and close
        else:
            self.process.start(self.file, flattened_args)
    @pyqtSlot()
    def terminate_process(self):
        if self.process and self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(1500):
                self.process.kill()

    @pyqtSlot()
    def _handle_stdout(self):
        while self.process and self.process.canReadLine():
            line = bytes(self.process.readLine()).decode('utf-8', errors='replace').strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                if 'status' in msg:
                    self.text_signal.emit(f"Status: {msg['status']}")
                elif 'progress' in msg:
                    self.text_signal.emit(f"Progress: {msg['progress']}")
                elif 'display' in msg:
                    self.display_signal.emit(str(msg['display']))
                elif 'prompt' in msg:
                    print(msg)
                    self.prompt_signal.emit(str(msg.get('placeholder', 'Enter value:')))
                else:
                    self.text_signal.emit(line)
            except Exception:
                self.text_signal.emit(line)
    def send_input(self, text):
        if self.process:
            print(text)
            self.process.write((text + '\n').encode('utf-8'))
            self.process.waitForBytesWritten()
    @pyqtSlot(int, QProcess.ExitStatus)
    def _on_finished(self, code, status):
        self.text_signal.emit(f"\nScript finished with code {code}.")
        self.finished.emit(code, int(status))

class Console(QWidget):
    text_signal = pyqtSignal(str)

    def __init__(self, parent: QWidget = None, app: QApplication = None):
        super().__init__(parent)
        self._parent = parent
        self.setStyleSheet("background-color: black; color: white; border: 1px solid #333;")
        if parent is not None:
            self.setGeometry(0, 0, parent.width(), parent.height())
        else:
            self.resize(800, 600)
        self.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        self.queue = []
        self.mediaElement = None
        self.thread: ProcessWorker = None
        self.process = None  # kept for backward-compat; always None in thread mode

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_media)

        # Safe QStyle acquisition
        self._style = (QApplication.instance() or app).style() if (QApplication.instance() or app) else None

        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        self.text.setFocusPolicy(Qt.NoFocus)
        self.text.setStyleSheet("background-color: black; color: white; border: none;")
        self.text_signal.connect(self.text.append)
        layout.addWidget(self.text)

        # Close button: icon if style available, fallback to text
        if self._style:
            self.closeButton = QPushButton(self._style.standardIcon(QStyle.SP_TitleBarCloseButton), '', self)
        else:
            self.closeButton = QPushButton('x', self)
        self.closeButton.setGeometry(self.width() - 35, 5, 30, 30)
        self.closeButton.raise_()
        self.closeButton.clicked.connect(self.hide)

    from PyQt5.QtCore import QThread

    def run(self, exe, file, *args):
        self.setVisible(True)
        try:
            if getattr(self._parent, 'shortcuts', None):
                self._parent.hideShortcuts()
        except Exception:
            pass
        self.raise_()

        if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
            self.worker.terminate_process()
            self.worker_thread.quit()
            self.worker_thread.wait()

        self.worker_thread = QThread(self)
        self.worker = ProcessWorker(exe, file, args)
        self.worker.moveToThread(self.worker_thread)

        self.worker.text_signal.connect(self.text.append)
        self.worker.display_signal.connect(self.queue_media)
        self.worker.prompt_signal.connect(self._handle_prompt)

        self.worker_thread.started.connect(self.worker.start)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(lambda: setattr(self, 'worker_thread', None))

        self.worker_thread.start()

    def runAutomation(self, exe, file, args, monitor):
        self.setVisible(True)
        self.raise_()

        # Stop existing worker/thread
        # if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
        #     self.worker.terminate_process()
            # self.worker_thread.quit()
            # self.worker_thread.wait()

        # self.worker_thread = QThread(self)
        self.worker = ProcessWorker(exe, file, args)
        # self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker.text_signal.connect(self.text.append)
        self.worker.display_signal.connect(self.queue_media)
        self.worker.prompt_signal.connect(self._handle_prompt)
        self.worker.start()
        # self.worker_thread.started.connect(self.worker.start)

        # Finished handler
        if getattr(monitor, 'needInt', None) == True:
            i = int(args[-1]) if args else -1
        else:
            i = args[-1]
        def on_finished(code, status):
            monitor.handleDone(i)
            # cleanup after finished
            # self.worker_thread.quit()
            # self.worker_thread.wait()
            self.worker.deleteLater()
            # self.worker_thread.deleteLater()
            # self.worker_thread = None

        self.worker.finished.connect(on_finished)

        # self.worker_thread.start()


    @pyqtSlot(str)
    def queue_media(self, src: str):
        if src and os.path.exists(src):
            self.queue.append(src)
        else:
            return

        if not self.timer.isActive():
            self.timer.start(5000)   # show next item every 5s
            self.display_media()     # show first immediately

    def display_media(self):
        if self.mediaElement:
            self.mediaElement.stop()
            self.mediaElement.deleteLater()
            self.mediaElement = None

        if self.queue:
            path = self.queue.pop(0)
            self.mediaElement = Media(self, path)
            self.mediaElement.setParent(self)
            # Bottom half
            self.mediaElement.setGeometry(0, self.height() // 2, self.width(), self.height() // 2)
            self.mediaElement.show()
            self.mediaElement.raise_()
        else:
            if self.timer.isActive():
                self.timer.stop()

    def resizeEvent(self, event):
        self.closeButton.setGeometry(self.width() - 35, 5, 30, 30)
        # Keep media in bottom half on resize
        if self.mediaElement:
            self.mediaElement.setGeometry(0, self.height() // 2, self.width(), self.height() // 2)
        super().resizeEvent(event)

    @pyqtSlot(str)
    def _handle_prompt(self, placeholder: str):
        text, ok = QInputDialog.getText(self, "Prompt", placeholder)
        if ok and self.worker:
            self.worker.send_input(text)
    def alert(self, msg):
        span = f"<span style=\"color:red;\">{msg}</span>"
        self.text.append(span)
    def hide(self):
        self.setVisible(False)

        # Stop process/thread cleanly
        if self.thread and self.thread.isRunning():
            self.thread.terminate_process()
            self.thread.quit()
            self.thread.wait()

        self.text.clear()

        if self.mediaElement:
            self.mediaElement.stop()
            self.mediaElement.deleteLater()
            self.mediaElement = None

        try:
            if hasattr(self._parent, 'showShortcuts'):
                self._parent.showShortcuts()
        except Exception:
            pass

        super().hide()
