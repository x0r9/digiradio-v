"""
Simple Kiss3 Async module to mimic the dr5 kiss module
"""

import kiss
import asyncio



class TCPAsyncKISS():
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port

        self.transport = None
        self.kiss_protocol = None
        self.timeout = 1 # TODO

    async def start_async(self):
        transport, kiss_protocol = await kiss.create_tcp_connection(
                host=self.ip,
                port=self.port,
            )
        self.transport = transport
        self.kiss_protocol = kiss_protocol

    async def read(self, readmode=False):
        result = []
        if self.kiss_protocol.frames.empty():
            return result
        async for r in self.kiss_protocol.read():
            result.append(r)
            if self.kiss_protocol.frames.empty():
                return result
            

        return result
    
