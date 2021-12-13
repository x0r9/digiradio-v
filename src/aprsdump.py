"""
APRSDump, a simple utility to connect to a KISS modem (direwolf)
and save all packets into a file for later analysis
"""

import argparse
import kiss
#import aprs
import framecap
import time

if __name__ == "__main__":

    parser = argparse.ArgumentParser("APRSDump - save KISS data into a file for later reading")
    parser.add_argument("-ip", type=str, default="127.0.0.1", help="ip of kiss modem")
    parser.add_argument("-port", type=int, default=8001, help="port of kiss modem")
    parser.add_argument("-out", type=str, required=True, help="file to write output")
    args = parser.parse_args()

    # Open up the file for writing
    f = open(args.out, "w")
    capture = framecap.FrameWriter(f)

    # Call back of each Frame to write
    def _on_aprs_frame(frame):
        capture.write_frame(time.time(), frame)

    # Start up the KISS client
    kclient = kiss.TCPKISS(args.ip, port=args.port)

    kclient.start()
    kclient.read(callback=_on_aprs_frame) 

