"""
Basic set of functions to grab APRS data
"""

import time
import aprs
import framecap
import aprslib

file_path = "file-dump.txt"

def aprs_object_name(par):
    """
    Return global name for the aprs object
    """
    if "object_name" in par:
        return par["object_name"].strip()

    return par["from"]

def process_raw_frame(frame):
    try:
        aprs_frame = aprs.parse_frame(frame)
        par = aprslib.parse(str(aprs_frame))
    except (aprslib.exceptions.ParseError, aprslib.exceptions.UnknownFormat) as e:
        return
    except Exception as e:
        return

    return par

def is_a_point(par):
    # is it a point?
    return "latitude" in par and "longitude" in par

def get_point(par):
    """
    Return lat, lon of point
    """
    return [par.get("latitude", None), par.get("longitude", None)]

def points_match_latlon(par_before, par_after):
    """
        Do points match?
        """

    return (par_before[0] == par_after[0]
            and par_before[1] == par_after[1])


def points_match(par_before, par_after):
    """
    Do points match?
    """

    return (par_before.get("latitude", None) == par_after.get("latitude", None)
           and par_before.get("longitude", None) == par_after.get("longitude", None) )


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

        par = process_raw_frame(frame)
        if par is None:
            return

        # is it a point?
        if not is_a_point(par):
            return

        curr_lat_lon = get_point(par)

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

            # update the last heard..
            last_heard = prev_frame.get("last_heard", None)
            if last_heard is None:
                par["last_heard"] = ts
            elif last_heard < ts:
                par["last_heard"] = ts

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
