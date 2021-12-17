"""
Basic set of functions to grab APRS data
"""

import time
import aprs
import framecap
import aprslib

file_path = "file-dump.txt"

def get_last_points(time_window_sec):
    """
    Get a list of the last heard station points
    """
    now = time.time()
    ts_after = now - time_window_sec

    stations = {}

    def _on_frame(ts, frame):
        if ts < ts_after:
            return # too old

        try:
            aprs_frame = aprs.parse_frame(frame)
            par = aprslib.parse(str(aprs_frame))
        except (aprslib.exceptions.ParseError, aprslib.exceptions.UnknownFormat) as e:
            return
        except Exception as e:
            return

        # is it a point?
        curr_lat_lon = [par.get("latitude", None), par.get("longitude", None)]
        if None in curr_lat_lon:
            return

        # Determine the object by source or object name...
        obj_name = par.get("from")
        if "object_name" in par:
            obj_name = par.get("object_name").strip()

        # check if there is a history or not?
        if obj_name in stations:
            # This already exists!
            prev_frame = stations[obj_name]
            prev_lat_lon = [prev_frame.get("latitude", None), prev_frame.get("longitude", None)]
            old_path = None
            if curr_lat_lon != prev_lat_lon:
                # it has moved!
                old_path = prev_frame.get("moving_path", None)
                if old_path is None:
                    old_path = []
                old_path.append([ts]+prev_lat_lon)
            if old_path is not None:
                par["moving_path"] = old_path


        stations[obj_name] = par

    f = open(file_path, "r")

    reader = framecap.FrameReader(f)

    d = reader.read_next()
    while d is not None:
        ts, frame = d

        # print(ts, frame)
        _on_frame(ts, frame)

        d = reader.read_next()

    # All files done...

    return list( stations.values() )
