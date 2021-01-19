from color_logger import logger
from httpx import Response
import settings

import os
import shutil
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

from utils import PResponse, PSocket, single_path, multiple_path, socket_path, multiple_filename
from utils import Timer
import utils

class Recorder:
    def __init__(self):
        self.socket_counter = 0
        self.singles_saved = list()
        self.multiples_saved = {}
        self.last_request = "First"
        self.timer = None

    def prepare(self):
        try:
            shutil.rmtree(utils.record_path)
        except OSError as e:
            logger.info(f"Nothing to delete at {utils.record_path}")
        else:
            logger.info(f"Removed existing record folder at {utils.record_path}")

        try:
            os.mkdir(utils.record_path)
            if settings.save_single is not None:
                os.mkdir(utils.singles_path)
            if settings.socket_rop is not None:
                os.mkdir(utils.sockets_path)
        except OSError as e:
            logger.error(f"Error creating record folder at {utils.record_path}: {str(e)}")
        else:
            logger.info(f"Created new record folder at {utils.record_path}")

    def start(self):
        if self.timer is None:
            self.timer = Timer()
            self.timer.start()

    def save(self, uri: str, response: Response):
        pResponse = PResponse(response)
        if uri in settings.save_single:
            self.save_single(uri, pResponse)
        else:
            self.start()
            self.save_multiple(uri, pResponse)

    def save_multiple(self, uri: str, response: PResponse):
        counter = self.multiples_saved.get(uri, 0)
        to = multiple_path(uri, counter)
        logger.info(f"Saving response to {to}")
        with open(to, "wb+") as f:
            pickle.dump(response, f, -1)
        counter += 1
        self.multiples_saved[uri] = counter
        self.last_request = multiple_filename(uri, counter - 1)
        self.timer.restart()

    def save_single(self, uri: str, response):
        if uri in self.singles_saved:
            return
        to = single_path(uri)
        logger.info(f"Saving single response to {to}")
        with open(to, "wb+") as f:
            pickle.dump(response, f, -1)
            self.singles_saved.append(uri)

    def save_socket(self, message: object):
        time_after = self.timer.nostop_check()
        pSocket = PSocket(message, self.last_request, time_after)
        to = socket_path(self.socket_counter)
        logger.info(f"Saving socket message to {to}")
        with open(to, "wb+") as f:
            pickle.dump(pSocket, f, -1)
        self.socket_counter += 1
