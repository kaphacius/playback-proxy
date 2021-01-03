from settings import mode
from settings import record_name
from settings import save_single as should_save_single
from color_logger import logger
from httpx import Response

import os
import shutil
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

cwd = "/".join(os.getcwd().split("/")[:-1]) + "/recordings"

singles = "singles"
sockets = "sockets"
record_path = f"{cwd}/{record_name}/"
singles_path = record_path + singles
sockets_path = record_path + sockets

class PResponse:
    def __init__(self, r: Response):
        self.status_code = r.status_code
        self.headers = r.headers
        self.content = r.content

class PSocket:
    def __init__(self, m: str, last_request: int):
        self.message = m
        self.last_request = last_request

class Recorder:
    def __init__(self):
        self.counter = 0
        self.socket_counter = 0
        self.singles_saved = list()

    def start(self):
        try:
            shutil.rmtree(record_path)
        except OSError as e:
            logger.info(f"Nothing to delete at {record_path}")
        else:
            logger.info(f"Removed existing record folder at {record_path}")

        try:
            os.mkdir(record_path)
            os.mkdir(singles_path)
            os.mkdir(sockets_path)
        except OSError as e:
            logger.error(f"Error creating record folder at {record_path}: {str(e)}")
        else:
            logger.info(f"Created new record folder at {record_path}")

    def save(self, uri: str, response: Response):
        escaped_uri = uri.replace('/', '\\')
        pResponse = PResponse(response)
        if uri in should_save_single:
            self.save_single(escaped_uri, pResponse)
        else:
            self.save_multiple(escaped_uri, pResponse)

    def save_multiple(self, uri: str, response):
        to = f"{record_path}{self.counter}_{uri}.bin"
        logger.info(f"Saving response to {to}")
        with open(to, "wb+") as f:
            pickle.dump(response, f, -1)
            self.counter += 1

    def save_single(self, uri: str, response):
        if uri in self.singles_saved:
            return
        to = f"{singles_path}/{uri}.bin"
        logger.info(f"Saving single response to {to}")
        with open(to, "wb+") as f:
            pickle.dump(response, f, -1)
            self.singles_saved.append(uri)

    def save_socket(self, message: object):
        pSocket = PSocket(message, self.counter)
        to = f"{sockets_path}/{self.counter}_{self.socket_counter}.bin"
        logger.info(f"Saving socket message to {to}")
        with open(to, "wb+") as f:
            pickle.dump(pSocket, f, -1)
            self.socket_counter += 1

    # logger.info(f"Playing back record {record_name}")
