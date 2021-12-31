import socket
from websockets import connect
import socket
import binascii
import asyncio
import kiss
import argparse
import time

ws_url = "ws://127.0.0.1:8080/streamapi/push-aprs/super-secret-key/ws"

async def hello(uri, kclient):
    counter = 1
    websocket = await connect(uri)
    ping_interval = 10
    next_ping = time.time() + ping_interval
    messages = {"msgs":[]}
    await websocket.send('{"dtype":"ping", "data": {"counter": '+str(counter)+'}}')
    def _on_message(msg):
        print("Got Message")
        messages["msgs"].append(msg)

    while True:
        n = time.time()
        if n > next_ping:
            print("Send ping")
            counter += 1
            await websocket.send('{"dtype":"ping", "data": {"counter": '+str(counter)+'}}')
            next_ping = time.time() + ping_interval

        try:
            kclient.read(callback=_on_message)

        except socket.timeout as e:
            pass
        while len(messages["msgs"]) > 0:
            msg = messages["msgs"].pop(0)
            print("Deque Message", len(msg))
            await websocket.send('{"dtype":"raw_aprs", "data": {"payload": "' + binascii.hexlify(msg).decode('ascii') + '" }}')
        await asyncio.sleep(0.1)




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
    kclient.interface.settimeout(0.1)
    asyncio.run(hello(ws_url, kclient))
