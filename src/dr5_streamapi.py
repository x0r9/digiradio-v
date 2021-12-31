"""
Simple server/cloud side listener for api data
"""
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect

import json
import time
import base64
import asyncio
import dr5_aprs
import dr5_config
import aprs_data

streamapi = FastAPI()

@streamapi.get("/hello")
async def stream_hello(request: Request):
    return {"hello": "streamapi"}

@streamapi.websocket("/push-aprs/{api_key}/ws")
async def push_aprs_ws(websocket: WebSocket, api_key: str):
    """
    the api websocket for getting APRS data
    """
    print("here")
    # Is the API key okay?
    if type(api_key) is not str or len(api_key) < 10:
        # Error
        return

    key_data = dr5_config.get_api_key_setup(api_key)
    # Support for APRS?
    if key_data is None or "aprs" not in key_data["modes"]:
        # Error
        return

    ## Ideally check if there is a previous connection

    #Otherwise All good!?

    await websocket.accept()

    ## setup message handler
    rc = dr5_aprs.RedisConnector()
    def _on_aprs_redis(ts, frame):
        par = aprs_data.process_raw_frame(frame)
        print(f"{type(par)}, {str(par)}")
        if par is None:
            return
        obj_name = aprs_data.aprs_object_name(par)
        print(f"new frame {obj_name}")
        if aprs_data.is_a_point(par):
            print("is point")
            print(rc.new_point(ts, par))

    try:
        while True:
            rx_data = await websocket.receive_text()
            print("got data", rx_data)
            j_data = json.loads(rx_data)
            dtype = j_data["dtype"]
            if dtype == "raw_aprs":
                # Parse the data and yeet
                _on_aprs_redis(time.time(), base64.b16decode(j_data["data"]["payload"].upper()))
    except WebSocketDisconnect:
        pass

@streamapi.get("/push-aprs/ws2")
async def push_aprs_ws2(request: Request):
    print("ws2")
    return {"hello": "ws2"}
