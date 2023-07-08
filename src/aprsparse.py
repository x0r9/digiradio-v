"""
Basic Parser
"""




class APRSRaw( object ):
    def __init__(self) -> None:
        self.flag = 0x00
        self.dst = None
        self.src = None
        self.digip_adr = None 
        self.control = 0
        self.proto_id = 0
        self.info = 0
        self.fcs = 0
        self.flag_end = 0 

    def parse(self, bin):
        self.flag = bin[0]
