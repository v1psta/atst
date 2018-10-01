import gc
import multiprocessing
import socket
import socketserver
import time
from urllib.parse import urlparse, urljoin

# This is adapted from flask-testing, https://github.com/jarus/flask-testing
# Inspired by https://docs.djangoproject.com/en/dev/topics/testing/#django.test.LiveServerTestCase
class LiveServer:
    def __init__(self, app, port=5000, timeout=5):
        self.app = app
        self._configured_port = port
        self._timeout = timeout
        self._port_value = multiprocessing.Value("i", self._configured_port)

    @property
    def server_url(self):
        return "http://localhost:%s" % self._port_value.value

    def spawn_live_server(self):
        self._process = None
        port_value = self._port_value

        def worker(app, port):
            # Based on solution: http://stackoverflow.com/a/27598916
            # Monkey-patch the server_bind so we can determine the port bound
            # by Flask.  This handles the case where the port specified is `0`,
            # which means that the OS chooses the port. This is the only known
            # way (currently) of getting the port out of Flask once we call
            # `run`.
            original_socket_bind = socketserver.TCPServer.server_bind

            def socket_bind_wrapper(self):
                ret = original_socket_bind(self)

                # Get the port and save it into the port_value, so the parent
                # process can read it.
                (_, port) = self.socket.getsockname()
                port_value.value = port
                socketserver.TCPServer.server_bind = original_socket_bind
                return ret

            socketserver.TCPServer.server_bind = socket_bind_wrapper
            app.run(port=port, use_reloader=False)

        self._process = multiprocessing.Process(
            target=worker, args=(self.app, self._configured_port)
        )

        self._process.start()

        # We must wait for the server to start listening, but give up
        # after a specified maximum timeout
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > self._timeout:
                raise RuntimeError(
                    "Failed to start the server after %d seconds. " % self._timeout
                )

            if self._can_ping_server():
                break

    def _can_ping_server(self):
        host, port = self.address
        if port == 0:
            # Port specified by the user was 0, and the OS has not yet assigned
            # the proper port.
            return False

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
        except socket.error as e:
            success = False
        else:
            success = True
        finally:
            sock.close()

        return success

    @property
    def address(self):
        """
        Gets the server address used to test the connection with a socket.
        Respects both the LIVESERVER_PORT config value and overriding server_url
        """
        parts = urlparse(self.server_url)

        host = parts.hostname
        port = parts.port

        if port is None:
            if parts.scheme == "http":
                port = 80
            elif parts.scheme == "https":
                port = 443
            else:
                raise RuntimeError("Unsupported server url scheme: %s" % parts.scheme)

        return host, port

    def terminate(self):
        if self._process:
            self._process.terminate()
