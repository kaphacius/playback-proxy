import os
import shutil
import time

from settings import mode
from settings import record_name
from settings import save_single as singles_list
from settings import socket_rop
from settings import records_path
from httpx import Response

cwd = os.getcwd()
record_path = f"{cwd}/{records_path}/{record_name}/"

if socket_rop is not None:
    sockets = "sockets"
    sockets_path = record_path + sockets
else:
    sockets_path = None

if singles_list is not None:
    singles = "singles"
    singles_path = record_path + singles
else:
    singles_path = None

not_found_response = Response(status_code=404)
slash_escape = '\\'

def escape_uri(uri: str):
    return uri.replace('/', slash_escape)

def unescape_uri(uri: str):
    return uri.replace(slash_escape, '/')

def single_path(uri: str):
    return f"{singles_path}/{escape_uri(uri)}.bin"

def multiple_path(uri: str, counter: int):
    return f"{record_path}{multiple_filename(uri, counter)}.bin"

def multiple_filename(uri: str, counter: int):
    return f"{counter}_{escape_uri(uri)}"

def socket_path(socket_counter: int):
    return f"{sockets_path}/{socket_counter}.bin"

class PResponse:
    def __init__(self, r: Response):
        self.status_code = r.status_code
        self.headers = r.headers
        self.content = r.content

    def toResponse(self):
        return Response(
            status_code=self.status_code,
            headers=self.headers,
            content=self.content
            )

class PSocket:
    def __init__(self, m: str, last_request: str, time_after: float):
        self.message = m
        self.last_request = last_request
        self.time_after = time_after

    def description(self):
        return f"{self.time_after} after {unescape_uri(self.last_request)}: {self.message}"

class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        if self._start_time is None:
            self._start_time = time.perf_counter()

    def stop(self):
        if self._start_time is not None:
            elapsed_time = time.perf_counter() - self._start_time
            self._start_time = None
            return elapsed_time

    def restart(self):
        elapsed_time = self.stop()
        self.start()
        return elapsed_time

    def nostop_check(self):
        if self._start_time is None:
            return 0.0
        else:
            return time.perf_counter() - self._start_time

