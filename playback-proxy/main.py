import websocket as _websocket
from fastapi import FastAPI
from fastapi import WebSocket as fWebSocket
from starlette.endpoints import WebSocketEndpoint
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from httpx import AsyncClient
from io import BytesIO
import sys
import time
import threading
import os
from waiting import wait
import logging
from color_logger import logger
import asyncio
import settings
from recorder import Recorder
from player import Player
import utils

client = AsyncClient()
app = FastAPI()

recorder: Recorder = None
player: Player = None
is_playback = False
is_record = False
is_proxy = False

def accept_socket(message: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(inSocket.send_bytes(message.encode('utf-8')))

def print_welcome(mode: str):
    record: str = None
    if settings.record_name != None:
        record = f" {settings.record_name} "
    else:
        record = " "
    logger.info("*************************************************")
    logger.info(f"\n\nSTARTING{record}IN {mode} MODE\n\n")
    logger.info("*************************************************")

def quit_proxy():
    os.system("kill -9 `ps -jaxwww | grep \"[.]/playback-proxy\" | awk '{print $2}'`")

def start(record_name: str = None, mode: str = None):
    if record_name != None and mode != None:
        settings.mode = mode
        settings.record_name = record_name

    set_mode()

    if is_record:
        utils.set_paths()
        print_welcome("RECORDING")
        global recorder
        recorder = Recorder()
        recorder.prepare()
    elif is_playback:
        utils.set_paths()
        print_welcome("PLAYBACK")
        global player
        player = Player(accept_socket)
        player.prepare()
    elif is_proxy:
        print_welcome("PROXY")

def set_mode():
    global is_playback
    global is_record
    global is_proxy
    is_playback = settings.mode == "PLAYBACK"
    is_record = settings.mode == "RECORD"
    is_proxy = is_record or settings.mode == "PROXY"

settings.load_envs()
start()

def proxied_url(rop: str):
    return f"{settings.protocol}{settings.endpoint}{rop}"

async def proxy_request(request: Request, rop: str):
    if is_proxy and rop not in settings.ignore_log:
        logger.info(f"Asking {request.method} {request.url}")

    result: httpx.Response

    if is_playback:
        result = player.load_next(rop)
    else:
        body = await request.body()
        result = await client.request(
            method=request.method,
            url=proxied_url(rop),
            params=request.query_params,
            content=body
        )

    if is_record:
        recorder.save(rop, result)

    if is_proxy and rop not in settings.ignore_log:
        logger.info(f"Received {result.status_code} from {result.url}")

    headers = result.headers
    content_type = None
    response: Response = None

    try:
        content_type = result.headers['content-type']
    except KeyError:
        response = Response(
            result.text,
            headers=headers,
            status_code=result.status_code
            )

    if response == None and result.headers['content-type'] == 'application/json':
        response = Response(
            result.text,
            media_type="application/json",
            headers=headers,
            status_code=result.status_code
            )
    elif response == None and result.headers['content-type'].startswith("image"):
        response = StreamingResponse(
            BytesIO(result.content), 
            media_type=result.headers['content-type'],
            headers=headers,
            status_code=result.status_code
            )

    return response

@app.get("/{rest_of_path:path}")
async def on_get(request: Request, rest_of_path: str):
    return await proxy_request(request, rest_of_path)

@app.post("/{rest_of_path:path}")
async def on_post(request: Request, rest_of_path: str):
    split = rest_of_path.split("/")
    if split[0] == "__playback-proxy":
        if split[1] == "quit":
            logger.info("Quitting proxy")
            quit_proxy()
            return Response("Shutting down proxy", media_type='text/plain')
        elif split[1] == "record":
            start(split[-1], "RECORD")
            return Response(f"Re-starting proxy for {split[-1]} in RECORD mode", media_type='text/plain')
        elif split[1] == "play":
            start(split[-1], "PLAYBACK")
            return Response(f"Re-starting proxy for {split[-1]} in PLAYBACK mode", media_type='text/plain')

    return await proxy_request(request, rest_of_path)

@app.put("/{rest_of_path:path}")
async def on_put(request: Request, rest_of_path: str):
    return await proxy_request(request, rest_of_path)

@app.delete("/{rest_of_path:path}")
async def on_delete(request: Request, rest_of_path: str):
    return await proxy_request(request, rest_of_path)

out_connected = False
inSocket: fWebSocket
outSocket: _websocket.WebSocketApp
out_socket_endpoint = f"{settings.socket_protocol}{settings.endpoint}{settings.socket_rop}"

def outConnected():
    return out_connected

if settings.socket_rop is not None:
    logger.info(f"Setting up socket on {settings.socket_rop}")
    @app.websocket_route(f"/{settings.socket_rop}")
    class MessagesEndpoint(WebSocketEndpoint):
        async def on_connect(self, in_ws):
            global inSocket, outSocket
            inSocket = in_ws
            await in_ws.accept()

            logger.info(f"IN socket connected on {settings.socket_rop}")

            if is_record:
                global recorder
                recorder.start()
            elif is_playback:
                player.start()

            if is_proxy:
                outSocket = _websocket.WebSocketApp(out_socket_endpoint,
                                      on_message = out_on_message,
                                      on_error = out_on_error,
                                      on_close = out_on_close)
                outSocket.on_open = out_on_open
                t = threading.Thread(target=outSocketThread, args=(outSocket,))
                t.daemon = True
                t.start()
                wait(outConnected)

        async def on_receive(self, in_ws, data) -> None:
            logger.info("Received from IN socket " + data.decode("utf-8"))
            if is_proxy:
                outSocket.send(data)

        async def on_disconnect(self, in_ws, close_code):
            logger.info(f"IN socket disconnected on {settings.socket_rop}")


    def outSocketThread(ws: _websocket):
        ws.on_open = out_on_open
        ws.run_forever()

    def out_on_message(ws, message):
        logger.info(f"Received from OUT socket {message}")

        if is_record:
            global recorder
            recorder.save_socket(message)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(inSocket.send_bytes(message))

    def out_on_error(ws, error):
        logger.error(f"Got error on OUT socket {error}")

    def out_on_close(ws):
        logger.warning(f"OUT socket was closed")

    def out_on_open(ws):
        logger.info(f"OUT socket connected to {out_socket_endpoint}")
        global out_connected
        out_connected = True

