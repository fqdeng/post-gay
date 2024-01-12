import os
import signal
import sys
from random import Random

import fire
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

import util
from backend_server import HTTPServer
from main_window import MainWindow


class App:
    def __init__(self):
        self.main_window = None

    def main(self, debug=False, remote=False):
        app = QApplication(sys.argv)
        os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] \
            = ('--disk-cache-dir=/dev/null --disk-cache-size=1 --disable-pinch'
               '--overscroll-history-navigation=0 --sand-box')

        if remote:
            port = 3000
        else:
            port = Random().randint(1024, 3098)
            HTTPServer(port=port).start_server()

        util.windows_hidpi_support()
        util.init_logging_config(debug=debug)
        self.main_window = MainWindow(debug=debug, port=port)
        self.main_window.show()

        timer = QTimer()
        timer.start(500)  # You may change this if you wish.
        timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
        # Register the signal handler for Ctrl+C
        signal.signal(signal.SIGINT, util.signal_handler)

        sys.exit(app.exec())


if __name__ == '__main__':
    fire.Fire(App().main)
