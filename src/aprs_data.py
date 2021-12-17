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

        aprs_frame = aprs.parse_frame(frame)
        try:
            par = aprslib.parse(str(aprs_frame))
        except (aprslib.exceptions.ParseError, aprslib.exceptions.UnknownFormat) as e:
            return

        # is it a point?
        lat_lon = [par.get("latitude", None), par.get("longitude", None)]
        if None in lat_lon:
            return

        stations[aprs_frame.info] = par

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
