"""
Listen to a TNC and process the data, this processed data will be fed into a Reddis
"""

import argparse
import kiss
import dr5_aprs
import aprs_data
import framecap
import time

if __name__ == "__main__":

    parser = argparse.ArgumentParser("reddis_feeder - save KISS data into a redis cache")
    parser.add_argument("-file", type=str, help="dump file to replay (dev option)")
    parser.add_argument("-ip", type=str, default="127.0.0.1", help="ip of kiss modem")
    parser.add_argument("-port", type=int, default=8001, help="port of kiss modem")
    args = parser.parse_args()

    # init the redis connector
    rc = dr5_aprs.RedisConnector()


    # Call back of each Frame to write



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

    if args.file is not None:
        with open(args.file, "r") as f:
            reader = framecap.FrameReader(f)
            d = reader.read_next()
            while d is not None:
                ts, frame = d
                _on_aprs_redis(ts, frame)
                d = reader.read_next()


    def _on_aprs_kiss(frame):
        ts = time.time()
        _on_aprs_redis(ts, frame)

    # Start up the KISS client
    kclient = kiss.TCPKISS(args.ip, port=args.port)

    kclient.start()
    kclient.read(callback=_on_aprs_kiss)
