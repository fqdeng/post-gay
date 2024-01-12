from __future__ import annotations

import logging

from PySide6 import QtCore
from PySide6.QtCore import QUrl, QObject,  Qt, QEvent
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QObject, Slot, Signal

import util
from common_window import SavePositionWindow

real_index = "./config/main/build/index.html"


class TouchEventFilter(QObject):
    def eventFilter(self, obj, event):
        # Filter out all touch events
        if event.type() in [QEvent.Type.NativeGesture]:
            return True  # Ignore the NativeGesture the disable the QWebEngineView zoom behavior
        # logging.debug(f"Event: {event.type()}")
        return super(TouchEventFilter, self).eventFilter(obj, event)


class JavascriptHandler(QObject):
    def __init__(self, window: MainWindow):
        super().__init__()
        self.window = window

    @Slot(str)
    def log(self, text):
        logging.debug(f"python receive JS: {text}")

    @Slot(str, result=str)
    def openFile(self, file_types: str):
        file_path = self.window.open_file(file_types=file_types)
        return file_path

    @Slot(int, str, str, int, result=int)
    def showMessageBox(self, icon, title, message, buttons):
        logging.debug(f"python receive JS: {message}")
        return QMessageBox.question(self.window, title, message, QMessageBox.StandardButton(buttons))


class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, sourceID):
        logging.debug(f"JS: {util.format_message(message)} (Line: {line} Source: {sourceID})")


class DisableContextMenuEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super(DisableContextMenuEngineView, self).__init__(parent)

    def contextMenuEvent(self, event):
        # Override the context menu event but do nothing.
        # This disables the default context menu.
        pass


class MainWindow(SavePositionWindow):
    def __init__(self, port=None, debug=False):
        super().__init__()
        self.dev_tools_view = None
        self.dev_tools_window = None
        self._debug = debug
        self.touch_event_filter = TouchEventFilter()
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Main", "Main"))
        self.port = port
        self.initUI()
        # self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

    def keyPressEvent(self, event):
        if self._debug and event.key() == Qt.Key.Key_F12:
            self.show_dev_tools()
        else:
            super().keyPressEvent(event)

    def initUI(self):
        self.browser = DisableContextMenuEngineView(self)
        if self._debug:
            self.browser = QWebEngineView(self)
        else:
            self.browser = DisableContextMenuEngineView(self)
        # 获取 QWebEngineSettings 实例
        settings = self.browser.settings()

        self.setCentralWidget(self.browser)

        self.browser.setPage(CustomWebEnginePage(self.browser))
        self.channel = QWebChannel(self.browser.page())
        self.ace_editor_handler = JavascriptHandler(window=self)
        self.channel.registerObject("python", self.ace_editor_handler)
        self.browser.page().setWebChannel(self.channel)

        self.setCentralWidget(self.browser)

        self.init_script()
        self.browser.load(QUrl(f"http://localhost:{self.port}"))

        self.browser.focusProxy().installEventFilter(self.touch_event_filter)

    def init_script(self):
        # JavaScript code to be injected
        js_code = """
            window.app=true
        """
        # Create a QWebEngineScript object
        script = QWebEngineScript()
        script.setSourceCode(js_code)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        # Add the script to the web engine
        self.browser.page().scripts().insert(script)

    def open_file(self, file_types: str = "All Files (*)"):
        # Open a file dialog and set the filter to .xlsx files
        options = QFileDialog.Option(0)  # Creating an instance of QFileDialog.Option
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", file_types, options=options)

        logging.debug(f"open file {file_path}")
        if file_path:
            return file_path  # Or handle the file path as needed
        return ""

    def resizeEvent(self, event):
        # This code will be executed every time the window is resized
        new_size = event.size()
        logging.debug(f"{self.__class__} Window resized to: {new_size.width()}x{new_size.height()}")
        self.resize_ace_editor(new_size.width(), new_size.height())
        super().resizeEvent(event)  # Ensure the default handler runs too

    def resize_ace_editor(self, width=None, height=None):
        if width is None:
            width = self.width()
        if height is None:
            height = self.height()
        logging.debug(f"Resize ace editor to: {width}x{height}")

    def run_js_code(self, js_code):
        self.browser.page().runJavaScript(js_code)

    def show_dev_tools(self):
        # Create a separate window for developer tools
        self.dev_tools_window = SavePositionWindow()
        self.dev_tools_view = QWebEngineView()

        # Set the developer tools view as the central widget of the new window
        self.dev_tools_window.setCentralWidget(self.dev_tools_view)

        # Connect the current page to the dev tools
        self.browser.page().setDevToolsPage(self.dev_tools_view.page())

        # Show the developer tools window
        self.dev_tools_window.show()

    def closeEvent(self, event):
        self.browser.close()
        util.close_app()
        super().closeEvent(event)
