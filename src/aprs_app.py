"""
More specific applciation for watching and reading APRS packets comming in
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect

import json
import time
import base64
import asyncio
import dr5_aprs
import dr5_config
import aprs_data

aprs_app = FastAPI()
config = dr5_config.config

rc = dr5_aprs.RedisConnector(redis_host=config["redis"]["host"], redis_port=config["redis"]["port"])

@aprs_app.get("/stations")
async def live_feed(request: Request):
    return {"hello": "aprs"}

@aprs_app.get("/raw_packets")
async  def get_raw_packets(request: Request):
    packets = rc.get_packets()
    result = []
    for packet in packets:
        raw_packet = dr5_aprs.b64_to_bin(packet["raw_packet"])
        pars = aprs_data.process_raw_frame(raw_packet)
        if pars is not None:
            packet["pars"] = pars
        else:
            packet["pars"] = None
    return packets
