import abc
import os
import shutil
import subprocess
import tempfile
import time
from functools import cache
from threading import Condition
from typing import Optional
from urllib.parse import quote_plus, urlunsplit

import requests
import structlog
from django.conf import settings
from requests_unixsocket import Session as UnixSocketSession

LOG = structlog.get_logger()


class BaseFrontendServer(abc.ABC):
    @abc.abstractmethod
    def get_session_and_base_url(self) -> tuple[requests.Session, str]:
        ...


class FrontendDevServer(BaseFrontendServer):
    def __init__(self, *, base_url: str):
        self._base_url = base_url
        self._session = requests.Session()

    def get_session_and_base_url(self) -> tuple[requests.Session, str]:
        return self._session, self._base_url


class FrontendServer(BaseFrontendServer):
    _entry_point: str
    _session: UnixSocketSession
    _tmp_dir: Optional[tempfile.TemporaryDirectory]
    _base_url: Optional[str]
    _server_process: Optional[subprocess.Popen]
    _server_ready: bool
    _server_ready_condition: Condition

    def __init__(self, *, entry_point: str):
        self._entry_point = entry_point
        self._session = UnixSocketSession()
        self._tmp_dir = None
        self._base_url = None
        self._server_process = None
        self._server_ready = False
        self._server_ready_condition = Condition()
        self._start()

    def __del__(self):
        self._stop()

    def _start(self):
        assert self._server_process is None and not self._server_ready
        self._tmp_dir = tempfile.TemporaryDirectory(prefix="django-frontend-")
        socket_path = os.path.join(self._tmp_dir.name, "server.socket")
        node_executable = getattr(settings, "FRONTEND_NODE_BIN", shutil.which("node"))
        if node_executable is None or not os.path.isfile(node_executable):
            raise RuntimeError(
                "A nodejs binary could not be found. Ensure that the FRONTEND_NODE_BIN setting "
                "points to a nodejs binary."
            )
        LOG.info(
            "Starting frontend server",
            node_executable=node_executable,
            entry_point=self._entry_point,
            socket_path=socket_path,
        )
        self._server_process = subprocess.Popen(
            [node_executable, self._entry_point],
            env={
                "NODE_ENV": "production",
                "SOCKET_PATH": socket_path,
            },
        )
        self._base_url = urlunsplit(("http+unix", quote_plus(socket_path), "/", "", ""))

        with self._server_ready_condition:
            # Wait for the server to be alive.
            for _ in range(200):
                if self._server_process.returncode is not None:
                    LOG.error(
                        "Frontend server process exited", exit_code=self._server_process.returncode
                    )
                    self._server_process = None
                    self._stop()

                    raise RuntimeError("Frontend server process exited.")

                try:
                    r = self._session.get(self._base_url, timeout=0.1)
                    if r.ok:
                        break
                except requests.exceptions.RequestException:
                    pass

                LOG.info("Waiting for frontend server...")
                time.sleep(0.1)
            else:
                raise RuntimeError("Timeout waiting for frontend server.")

            self._server_ready = True
            self._server_ready_condition.notify_all()

    def _stop(self):
        self._tmp_dir = None
        self._base_url = None
        self._server_ready = False

        if self._server_process is not None:
            self._server_process.terminate()
            try:
                self._server_process.wait(5)
            except subprocess.TimeoutExpired:
                LOG.warn("Frontend server process did not stop gracefully.")
                self._server_process.kill()

            self._server_process = None

    def _ensure_server(self):
        if self._server_process is None:
            self._start()

        if not self._server_ready:
            with self._server_ready_condition:
                while not self._server_ready:
                    self._server_ready_condition.wait()

    def get_session_and_base_url(self) -> tuple[requests.Session, str]:
        self._ensure_server()
        assert self._base_url is not None
        return self._session, self._base_url


@cache
def ensure_frontend_server() -> Optional[BaseFrontendServer]:
    server_base_url = getattr(settings, "FRONTEND_SERVER", None)
    if server_base_url is not None:
        return FrontendDevServer(base_url=server_base_url)

    server_entry_point = getattr(settings, "FRONTEND_SERVER_ENTRY_POINT", None)
    if server_entry_point is None:
        LOG.warn(
            "FRONTEND_SERVER_ENTRY_POINT setting not set and is required when serving the UI."
        )
        return None

    return FrontendServer(entry_point=server_entry_point)
