import websocket as _websocket
from fastapi import FastAPI
from fastapi import WebSocket as fWebSocket
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from httpx import AsyncClient
from io import BytesIO
import sys
import time
import threading
from waiting import wait
import logging
from color_logger import logger
import asyncio
from settings import protocol, socket_protocol, endpoint
from settings import socket_rop, ignore_log, save_single
from settings import mode
from recorder import Recorder
from player import Player

out_socket_endpoint = f"{socket_protocol}{endpoint}{socket_rop}"
client = AsyncClient()

app = FastAPI()

def accept_socket(message: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print(inSocket)
    loop.run_until_complete(inSocket.send_bytes(message.encode('utf-8')))

is_playback = mode == "PLAYBACK"
is_record = mode == "RECORD"
is_proxy = is_record or mode == "PROXY"

if is_record:
    logger.info("\n\n\nSTARTING IN RECORDING MODE\n\n\n")
    recorder = Recorder()
    recorder.prepare()
elif is_playback:
    logger.info("\n\n\nSTARTING IN PLAYBACK MODE\n\n\n")
    player = Player(accept_socket)
    player.prepare()
elif is_proxy:
    logger.info("\n\n\nSTARTING IN PROXY MODE\n\n\n")

def proxied_url(rop: str):
    return f"{protocol}{endpoint}{rop}"

async def proxy_request(request: Request, rop: str):
    if is_proxy and rop not in ignore_log:
        logger.info(f"Asking {request.method} {request.url}")

    result: httpx.Response

    if is_playback:
        result = player.load_next(rop)
    elif is_proxy:
        body = await request.body()
        result = await client.request(
            method=request.method,
            url=proxied_url(rop),
            params=request.query_params,
            content=body
        )

    if is_record:
        recorder.save(rop, result)

    if is_proxy and rop not in ignore_log:
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

def outConnected():
    return out_connected

@app.websocket(f"/{socket_rop}")
async def socket_endpoint(in_ws: fWebSocket):
    global inSocket, outSocket
    inSocket = in_ws
    await in_ws.accept()
    logger.info(f"IN socket connected on {socket_rop}")

    if is_record:
        global recorder
        recorder.start()
    elif is_playback:
        print("starting player")
        player.start()

    if is_proxy:
        outSocket = _websocket.WebSocketApp(out_socket_endpoint,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
        outSocket.on_open = on_open
        t = threading.Thread(target=outSocketThread, args=(outSocket,))
        t.daemon = True
        t.start()
        wait(outConnected)

    try:
        while True:
            data = await inSocket.receive_bytes()
            logger.info("Received from IN socket " + data.decode("utf-8"))
            if is_proxy:
                outSocket.send(data)
    except RuntimeError as e:
        logger.error(f"Got exception on IN socket {e}")
        


def outSocketThread(ws: _websocket):
    ws.on_open = on_open
    ws.run_forever()

def on_message(ws, message):
    logger.info(f"Received from OUT socket {message}")

    if is_record:
        global recorder
        recorder.save_socket(message)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(inSocket.send_bytes(message))

def on_error(ws, error):
    logger.error(f"Got error on OUT socket {error}")

def on_close(ws):
    logger.warning(f"OUT socket was closed")

def on_open(ws):
    logger.info(f"OUT socket connected to {out_socket_endpoint}")
    global out_connected
    out_connected = True
