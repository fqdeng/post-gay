import http.server
import logging
import socketserver
import threading

import util

DIRECTORY = "../../javascript/post-gay-web/build"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


class HTTPServer:
    def __init__(self, directory=DIRECTORY, port=None):
        self.port = port
        global DIRECTORY
        DIRECTORY = directory
        self.httpd: socketserver.TCPServer = None

    def _run_server(self):
        util.register_httpd(self)
        ip = "127.0.0.1"
        with socketserver.TCPServer((ip, self.port), Handler) as httpd:
            logging.debug(f"http serving at port: http://{ip}:{self.port}")
            self.httpd = httpd
            httpd.serve_forever()

    def start_server(self):
        thread = threading.Thread(target=self._run_server, daemon=True)
        thread.start()
        return thread

    def stop_server(self):
        if self.httpd is not None:
            logging.debug("http server stopped.")
            self.httpd.server_close()
