from __future__ import annotations
import contextlib
import io, os
import logging
import platform
from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

if TYPE_CHECKING:
    from backend_server import HTTPServer


def eval_and_capture_output(code, context={}):
    # Create a string stream to capture output
    output_stream = io.StringIO()

    # Redirect stdout to the string stream
    with contextlib.redirect_stdout(output_stream):
        try:
            # Evaluate the code
            exec(code, context)
        except Exception as e:
            # Print any exception that occurs
            print(f"Error during execution: {e}")

    # Get the content from the stream
    captured_output = output_stream.getvalue()

    return captured_output


_http_servers: list[HTTPServer] = []


def register_httpd(httpd):
    _http_servers.append(httpd)


def close_app():
    for _http_server in _http_servers:
        _http_server.stop_server()

    for widget in QApplication.topLevelWidgets():
        widget.close()
    instance = QApplication.instance()
    if instance is not None:
        instance.quit()


def signal_handler(sig, frame):
    close_app()


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Replace newlines in the message
        record.msg = record.msg.replace('\n', '\\n')
        return super().format(record)


def init_logging_config(debug=False):
    logging.basicConfig(level=logging.DEBUG, filename='./config/app.log', filemode='w')
    logger = logging.getLogger()
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    # Create a stream handler (or any other handler)
    handler = logging.StreamHandler()
    # Set the custom formatter for the handler
    formatter = CustomFormatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # Add the handler to the logger
    logger.addHandler(handler)


def list_files_and_directories(path):
    try:
        # List all files and directories in the specified path
        result = list()
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                result.append(entry + "/")
            else:
                result.append(entry)
        logging.debug(f"List files and directories in {path}: {result}")
        return result
    except FileNotFoundError:
        logging.error(f"The path {path} does not exist.")
    except PermissionError:
        logging.error(f"Permission denied for accessing the path {path}.")
    return []


def windows_hidpi_support():
    if platform.system() == "Windows":
        QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QtGui.QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
