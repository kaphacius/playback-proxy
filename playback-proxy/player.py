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

from utils import record_path, singles_path, multiple_path, multiple_filename, sockets_path
from utils import PResponse, PSocket, unescape_uri, not_found_response
from threading import Timer

class Player:
    def __init__(self, send_socket):
        self.socket_counter = 0
        self.singles_saved = {}
        self.sockets_saved = []
        self.multiples_saved = {}
        self.last_request = "First"
        self.send_socket = send_socket
        self.dispatchers = list()

    def prepare(self):
        for single in os.listdir(singles_path):
            path = f"{singles_path}/{single}"
            logger.info(f"Attempting to load single response from {path}")
            with open(path, 'rb') as f:
                self.singles_saved[os.path.splitext(unescape_uri(single))[0]] = pickle.load(f)

        for socket in os.listdir(sockets_path):
            path = f"{sockets_path}/{socket}"
            logger.info(f"Attempting to load socket message from {path}")
            with open(path, 'rb') as f:
                self.sockets_saved.append(pickle.load(f))
        logger.info("Loaded socket events: ")
        logger.info("\n".join([s.description() for s in self.sockets_saved]))

    def start(self):
        logger.info("---Player started---")
        self.check_socket()

    def load_next(self, uri: str):
        if uri in should_save_single and uri in self.singles_saved:
            return self.singles_saved[uri].toResponse()
        
        counter = self.multiples_saved.get(uri, 0)
        path = multiple_path(uri, counter)
        if not os.path.exists(path):
            logger.warning(f"Response not found at {path}")
            if counter is not 0:
                logger.warning(f"Attempting previous response")
                counter -= 1
                path = multiple_path(uri, counter)
            else:
                logger.error(f"Unknown call")
                return not_found_response
        logger.info(f"Attempting to load response from {path}")
        with open(path, 'rb') as f:
            pResponse: PResponse = pickle.load(f)
            counter += 1
            self.multiples_saved[uri] = counter
            self.last_request = multiple_filename(uri, counter - 1)
            self.check_socket()
            return pResponse.toResponse()

    def check_socket(self):
        to_send = list()
        for socket in self.sockets_saved:
            if socket.last_request == self.last_request:
                to_send.append(socket)

        for socket in to_send:
            self.dispatch_socket(socket)
            self.sockets_saved.remove(socket)

    def dispatch_socket(self, socket: PSocket):
        logger.info(f"Sending {socket.message} via socket in {socket.time_after} seconds")
        t = Timer(socket.time_after, self.send_socket, args=(socket.message,))
        t.start()
        self.dispatchers.append(t)









