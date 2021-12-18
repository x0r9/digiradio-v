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
            self.r.hmset(point_key, hpar_curr)

        else:
            print("object already there")
            self.r.hmset(point_key, hpar_curr)

        return hpar_curr

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
