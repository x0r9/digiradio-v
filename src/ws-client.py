import socket
from websockets import connect
from websockets.exceptions import ConnectionClosedError
import socket
import binascii
import asyncio
from asyncio.exceptions import TimeoutError
import kiss
import argparse
import time


ws_url = "ws://127.0.0.1:8080/streamapi/push-aprs/super-secret-key/ws"


async def send_data_loop(kclient, websocket, messages, ping_interval=10):
    def _on_message(msg):
        print("Got Message")
        messages["msgs"].append(msg)
    next_ping = time.time() + ping_interval

    while True:
        n = time.time()
        if n > next_ping:
            print("Send ping")
            messages["counter"] += 1
            await websocket.send('{"dtype":"ping", "data": {"counter": '+str(messages["counter"])+'}}')
            next_ping = time.time() + ping_interval

        try:
            rx_frames = kclient.read(readmode=False)
            print(f"rx_frame count: {len(rx_frames)}")
            if len(rx_frames) == 0:
                # potentially no data RX, return No
                raise Exception("Wa wa wa wa")
            for frame in rx_frames:
                _on_message(frame)
        except socket.timeout as e:
            print("timeout")

        while len(messages["msgs"]) > 0:
            msg = messages["msgs"].pop(0)
            print("Deque Message", len(msg))
            await websocket.send('{"dtype":"raw_aprs", "data": {"payload": "' + binascii.hexlify(msg).decode('ascii') + '" }}')
        await asyncio.sleep(0.1)



async def hello(uri, kclient):
    beb_time = 1

    while True:
        try:
            websocket = await connect(uri)
        except (ConnectionRefusedError, TimeoutError) as e:
            print("could not connect:", type(e).__name__, e)
            print(f"waiting for {beb_time} secs")
            await asyncio.sleep(beb_time)
            beb_time = beb_time*2
            if beb_time > 60:
                beb_time = 60
            continue 

        # Connected...
        print("Connected!")
        beb_time = 1  # reset BEB timer

        # prepare for messaging    
        messages = {"msgs":[], "counter":1}
        def _on_message(msg):
            print("Got Message")
            messages["msgs"].append(msg)

        
        # Listen to Kiss and loop
        try:
            await send_data_loop(kclient, websocket, messages)
        except ConnectionClosedError:
            print("D/C'd, wait and reconnect...")
            await asyncio.sleep(beb_time)




if __name__ == "__main__":

    parser = argparse.ArgumentParser("ws-client - send KISS data to a websocket for processing")
    parser.add_argument("-ws", type=str, help="websocket address to send data too")
    parser.add_argument("-ip", type=str, default="127.0.0.1", help="ip of kiss modem")
    parser.add_argument("-port", type=int, default=8001, help="port of kiss modem")
    args = parser.parse_args()

    if args.ws is not None:
        ws_url = args.ws

    # connect KISS

    kclient = kiss.TCPKISS(args.ip, port=args.port)

    kclient.start()
    kclient.interface.settimeout(10)
    asyncio.run(hello(ws_url, kclient))
