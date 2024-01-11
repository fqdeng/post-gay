import signal
import sys, os
import threading

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

import backend_server
import util
from backend_server import HTTPServer
from main_window import MainWindow
import fire


class App:
    def __init__(self):
        self.main_window = None

    def main(self, debug=False, remote=False):
        app = QApplication(sys.argv)
        os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-pinch --disable-gpu --overscroll-history-navigation=0'

        if remote:
            backend_server.PORT = 3000
        else:
            HTTPServer().start_server()

        util.windows_hidpi_support()
        util.init_logging_config(debug=debug)
        self.main_window = MainWindow(debug=debug)
        self.main_window.show()

        timer = QTimer()
        timer.start(500)  # You may change this if you wish.
        timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
        # Register the signal handler for Ctrl+C
        signal.signal(signal.SIGINT, util.signal_handler)

        sys.exit(app.exec_())


if __name__ == '__main__':
    fire.Fire(App().main)
