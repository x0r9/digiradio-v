"""
Frame capture is a basic file reader/write of APRS network traffic
"""

def bin_to_hex(bindata):
    return "".join([f"{s:02X}"for s in bindata])

def hex_to_bin(string):
    result = bytearray()
    for n in range(0,len(string), 2):
        s = string[n:n+2]
        n = int(s, 16)
        result.append(n)

    return result 

class FrameWriter(object):
    def __init__(self, fileobj):
        self.f = fileobj

    def write_frame(self, ts, frame):
        line = str(ts) + ","+bin_to_hex(frame)+"\n"
        self.f.write(line)


class FrameReader(object):
    def __init__(self, fileobj):
        self.f = fileobj

    def read_next(self):
        line = ""
        d = self.f.read(1)
        while len(d) != 0:
            if d == "\n":
                break
            line += d
            d = self.f.read(1)
        
        line = line.strip()

        if len(line) == 0:
            return None

        sts, shex = tuple(line.split(","))

        ts = float(sts)
        frame = hex_to_bin(shex)

        return (ts, frame)

