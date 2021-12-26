"""
Class to handle inserting, updating the reading data in a redis system
"""

import redis
import json
import aprs_data


def aprs_to_redis(ts, par):
    """
    change aprslib par onbject to a hash table redis can store
    """
    return {
        "latitude":par.get("latitude", None),
        "longitude": par.get("longitude", None),
        "last_heard": ts,
        "symbol": par["symbol_table"]+par["symbol"],
        "from": par["from"]
    }

def redis_to_native(hpar):
    return {
        "latitude": float(hpar[b"latitude"].decode("utf-8")),
        "longitude": float(hpar[b"longitude"].decode("utf-8")),
        "last_heard": float(hpar[b"last_heard"].decode("utf-8")),
        "symbol": hpar[b"symbol"].decode("utf-8"),
        "from": hpar[b"from"].decode("utf-8")
    }

def read_redis_list(b_list):
    if b_list is None:
        return []
    else:
        return json.loads(b_list.decode("utf-8"))


class RedisConnector(object):
    """
    Connect to a redis server and handle common tasks
    """
    def __init__(self, redis_host="127.0.0.1", redis_port=6379, redis_password=None):
        self.r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
        self.pubsub_key = "ps_livepoints"


    def new_point(self, ts, par):
        """
        A new point has arrived...
        """

        # Get the Object name

        object_name = aprs_data.aprs_object_name(par)

        point_key = "point_"+object_name

        hpar_prev = self.r.hgetall(point_key)
        hpar_curr = aprs_to_redis(ts, par)
        print("hpar_prev", hpar_prev)
        if len(hpar_prev) == 0: # is empty = None
            # Insert a new one?
            print("new instert", hpar_curr)

            # insert new point into cache
            self.r.hmset(point_key, hpar_curr)
            # send a live feed of the update too
            self.r.publish(self.pubsub_key, json.dumps({"dtype": "new_point", "data": {object_name: hpar_curr}}))

        else:
            print("object already there")
            # are we moving?
            natpar_prev = redis_to_native(hpar_prev)
            is_moving = not aprs_data.points_match(natpar_prev, par)
            update_name = "ping_point" # Point isn't moving
            if is_moving:
                # moving...
                print("object has moved")
                update_name = "move_point" # Point is moving
                self.update_move(object_name, ts, [par["latitude"], par["longitude"]])
            else:
                print("object stationary")

            # update new point into cache
            self.r.hmset(point_key, hpar_curr)
            self.r.publish(self.pubsub_key, json.dumps({"dtype": update_name, "data": {object_name: hpar_curr}}))

        return hpar_curr

    def update_move(self, object_name, ts, path_loc):
        """
        Update the data for where to move to
        """
        print(f"Object moved {object_name}")
        move_key = "move_" + object_name
        tdump = json.dumps([ts, path_loc[0], path_loc[1]])
        n = self.r.lpush(move_key, tdump)
        if n > 100:
            # pop
            self.r.rpop(move_key)


    def get_last_points(self, time_after):
        """
        Return list of objects after this time...
        """
        key_points = self.r.keys("point_*")

        result = {}
        for key in key_points:
            data = self.r.hgetall(key)
            print(f"got {key} as {data}")
            npar = redis_to_native(data)

            if npar["last_heard"] > time_after:
                result[key[6:]] = npar
        return result

    def get_last_moves(self, time_after):
        """
        Return list of movements after this time...
        """
        key_points = self.r.keys("move_*")
        print(f" time_after {time_after}")
        result = {}
        for key in key_points:
            data = self.r.lrange(key, 0, -1)
            print(f"{key} - {len(data)}")
            ndata = [json.loads(a.decode("utf-8")) for a in data]
            print(f"{key} + {len(ndata)}, {ndata[0]}")
            ndata = list([x for x in ndata if x[0] > time_after])
            print(f"{key} ? {len(ndata)}")
            if len(ndata) > 0:
                result[key[5:]] = ndata
        return result

"""
            if aprs_data.points_match(hpar_prev, hpar_curr):
                # not moved, update last heard..
                if ts > hpar_prev[b"last_heard"]:
                    self.r.hmset(point_key, hpar_curr)
            else:
                # add to path...
                loc_history = hpar_prev.get(b"loc_history", None)
                loc_history = read_redis_list(hpar_prev.get(b"loc_history", None))
                print("prev loc_history", loc_history)


                loc_history.append([hpar_prev[b"last_heard"].decode("utf-8"), hpar_prev[b"latitude"].decode("utf-8"), hpar_prev[b"longitude"].decode("utf-8")])
                print(f"add to history {len(loc_history)}")
                hpar_curr[b"loc_history"] = json.dumps(loc_history)

"""
