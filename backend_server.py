import http.server
import logging
import socketserver
import threading

import util

PORT = 8740
DIRECTORY = "../../javascript/post-gay-web/build"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


class HTTPServer:
    def __init__(self, directory=DIRECTORY, port=PORT):
        self.port = port
        global DIRECTORY
        DIRECTORY = directory
        self.httpd = None

    def _run_server(self):
        with socketserver.TCPServer(("", self.port), Handler) as httpd:
            logging.info(f"http serving at port: {self.port}")
            self.httpd = httpd
            httpd.serve_forever()

    def start_server(self):
        thread = threading.Thread(target=self._run_server, daemon=True)
        thread.start()
        return thread

    def stop_server(self):
        logging.info("http server stopped.")
        self.httpd.shutdown()
        self.httpd.server_close()
