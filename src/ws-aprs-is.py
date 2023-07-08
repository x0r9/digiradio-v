"""
Connect to APRS-IS and listen for data to feed into application
"""
import argparse
import aprslib
import logging



if __name__ == "__main__":
    parser = argparse.ArgumentParser("ws-aprs-is - send APRS-IS data to a websocket for processing")
    # parser.add_argument("-ws", type=str, help="websocket address to send data too")

    args = parser.parse_args()

    #kiss.LOG_LEVEL = logging.debug
    logging.basicConfig(level=logging.DEBUG)

    # Try and connect
    def p(x): print(x)

    host = "rotate.aprs.net"
    port = 14580 # this is for filters
    #filter = "r/33.25/-96.5/500"

    ##
    ## filter rules: http://www.aprs-is.net/javAPRSFilter.aspx
    ##

    # Stations near home...
    filter = "r/53.92/-1.39/200"
    filter = "d/RS0ISS"


    AIS = aprslib.IS("N0CALL", host=host, port=port)
    AIS.filter = filter
    AIS.connect()
    AIS.consumer(p, raw=True)
