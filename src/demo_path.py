"""
Demo code to help detect and determine how to add a path onto something
"""

import argparse
import framecap
import aprs_data

class BasicDatabase(object):
    def __init__(self):
        self.points = {}
        self.paths = {}
        self.last_ts = 0

    def update_point(self, name, ts, location):
        self.last_ts = ts
        if name in self.points:
            # Update the point
            prev_point = self.points[name]

            #update location
            self.points[name] = {"loc": location, "last_seen": ts, "heard_count":prev_point['heard_count']+1}

            # are we moving?
            if not aprs_data.points_match_latlon(prev_point['loc'], location):
                # moving...
                self.update_move(name, ts, prev_point['loc'] )

        else:
            # new poisiton
            self.points[name] = { "loc": location, "last_seen": ts ,"heard_count":1}

    def update_move(self, name, ts, prev_location):
        if name in self.paths:
            # update the path
            self.paths[name].append([ts, prev_location])
        else:
            # new path
            self.paths[name] = [[ts, prev_location]]


    def get_points_after(self, ts):
        last_points = {}
        for name, val in self.points.items():
            if val["last_seen"] > ts:
                last_points[name] = val

        return last_points

    def get_paths_after(self, ts):
        last_paths = {}
        for name, val in self.paths.items():
            split_val = list([x for x in val if x[0] > ts])
            if len(split_val) > 0:
                last_paths[name] = split_val
        return last_paths

if __name__ == "__main__":

    parser = argparse.ArgumentParser("demo-path")
    parser.add_argument("-file", type=str, help="dump file to replay (dev option)", required=True)
    args = parser.parse_args()


    bdb = BasicDatabase()

    def _on_frame(ts, frame):
        par = aprs_data.process_raw_frame(frame)
        if par is None or not aprs_data.is_a_point(par):
            return

        bdb.update_point(aprs_data.aprs_object_name(par), ts, aprs_data.get_point(par))


    f = open(args.file, "r")
    reader = framecap.FrameReader(f)
    d = reader.read_next()
    while d is not None:
        ts, frame = d

        #print(ts, frame)
        _on_frame(ts, frame)

        d = reader.read_next()

    last_see = bdb.last_ts - 3600*4

    points = bdb.get_points_after(last_see)

    stations = sorted(points.keys())
    for station in stations:
        p = points[station]
        loc = p["loc"]
        print(f"{station:10} - {loc[0]:8.5f}, {loc[1]:9.5f} [{p['heard_count']:5}]")

    paths = bdb.get_paths_after(last_see)
    path_stations = sorted(paths.keys())
    for station in path_stations:
        p = paths[station]
        print(f"{station:10} - [{len(p):5}]")
        for ts, loc in p:
            print(f"    {loc[0]:8.5f}, {loc[1]:9.5f}")