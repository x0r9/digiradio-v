"""
Shameless copied and modified from:
https://fastapi.tiangolo.com/advanced/websockets/
"""

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import redis
import asyncio
import time


app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8081/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


html_redis = """
<!DOCTYPE html>
<html>
    <head>
        <title>Redis</title>
    </head>
    <body>
        <h1>WebSocket Redis</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8081/ws-redis");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get("/redis")
async def get():
    return HTMLResponse(html_redis)

@app.websocket("/ws-redis")
async def websocket_redis_endpoint(websocket: WebSocket):
    await websocket.accept()
    r = redis.Redis(host="localhost", port=6379, db=0)
    p = r.pubsub()
    pub_topic = "ps_livepoints"
    p.subscribe(pub_topic)
    ping_interval = 5
    next_ping = time.time()+ping_interval
    ping_count = 0
    first_message = True
    while True:
        data = p.get_message()
        ts = time.time()

        if ts > next_ping:
            await websocket.send_text('{"dtype":"ping", "data": {"ts": {'+str(ts)+', "count":'+str(ping_count)+'}}}')
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
