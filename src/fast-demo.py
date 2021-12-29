from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import redis

import os
import json
import asyncio

#Local modules
import aprs_data
import dr5_aprs
import time






templates = Jinja2Templates(directory="templates")

def get_config(config_path=None):

    # If not supplied find it locally or in /etc/...
    if config_path is None:
        if os.path.isfile("config.json"):
            config_path = "config.json"
        else:
            config_path = "/etc/digiradio-v/config.json"

    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            return json.loads(f.read())
    raise IOError("No config file found")

config = get_config()
rc = dr5_aprs.RedisConnector(redis_host=config["redis"]["host"], redis_port=config["redis"]["port"])

## Start Specifiying the FastAPI app
app = FastAPI(root_path=config.get("root_path", None))
app.mount("/static/", StaticFiles(directory="static"), name="static")

@app.get("/symbol-test", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("symbol-test.html", {"request": request, "id": id})

# @app.get("/last-points-file/{window_secs}")
# async def last_points(request: Request, window_secs: int):
#     return {"points":aprs_data.get_last_points(window_secs)}

@app.get("/last-points/{window_secs}")
async def last_points(request: Request, window_secs: int):
    n = time.time()
    n -= window_secs
    return {"points":rc.get_last_points(n), "moves":rc.get_last_moves(n)}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    ws_url = ""
    if config.get("root_path", None) is not None:
        root_path = config["root_path"]
        if not root_path.startswith("/"):
            root_path = "/"+root_path
        if not root_path.endswith("/"):
            root_path = root_path+"/"
        ws_url = "ws://hostname-here"+root_path+"ws-live"
    template_data = {"request": request,
                     "config": config,
                     "ws_url": ws_url}
    return templates.TemplateResponse("full-map.html", template_data)

## Websockets...
@app.websocket("/ws-live")
async def websocket_redis_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("ws connected")
    r = redis.Redis(host=config["redis"]["host"], port=config["redis"]["port"], db=0)
    p = r.pubsub()
    pub_topic = "ps_livepoints"
    p.subscribe(pub_topic)
    ping_interval = 10
    next_ping = time.time()+ping_interval
    ping_count = 0
    first_message = True
    while True:
        data = p.get_message()
        ts = time.time()

        if ts > next_ping:
            await websocket.send_text('{"dtype":"ping", "data": {"ts":'+str(ts)+', "count":'+str(ping_count)+'}}')
            ping_count += 1
            next_ping = time.time() + ping_interval
        if data is None:
            await asyncio.sleep(0.2)
            continue
        elif first_message:
            # First message is subscribe, do not send to web client...
            first_message = False
        else:
            try:
                json_data = data["data"].decode("ascii")
                await websocket.send_text(f"{json_data}")
            except:
                pass
