import argparse
import dr5_aprs
import aprs_data
import framecap
import time

if __name__ == "__main__":

    parser = argparse.ArgumentParser("file_out - read out data from CSV dump")
    parser.add_argument("-file", type=str, help="dump file to replay (dev option)")

    args = parser.parse_args()

    def _on_aprs_redis(ts, frame):
        par = aprs_data.process_raw_frame(frame)
        #
        if par is None:
            return

        print(f"from:{par['from']}, to:{par['to']}, path {par['path']}, via {par['via']}, raw: {par['raw']}")
        #print(f"{str(par)}")
        if par is None:
            return
        obj_name = aprs_data.aprs_object_name(par)
        #print(f"new frame {obj_name}")


    if args.file is not None:
        with open(args.file, "r") as f:
            reader = framecap.FrameReader(f)
            d = reader.read_next()
            while d is not None:
                ts, frame = d
                _on_aprs_redis(ts, frame)
                d = reader.read_next()