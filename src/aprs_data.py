"""
Basic set of functions to grab APRS data
"""

import time
import aprs
import framecap
import aprslib

import ax253 
AX25Frame = ax253.frame.Frame

file_path = "file-dump.txt"

def clean_raw(raw):
    """Remove any start 0x00 to aid parser"""
    index = 0
    for n, x in enumerate(raw):
        if x != 0:
            index = n
            break
            

    result = raw[index:]
    #print(raw)
    #print(result)
    return result

def aprs_object_name(par):
    """
    Return global name for the aprs object
    """
    if "object_name" in par:
        return par["object_name"].strip()

    return par["from"]


def raw_frame(raw_frame):
    def _inc_stat(name):
        pass

    #ax25 = aprs.functions.parse_frame_ax25(raw_frame)
    raw_frame = clean_raw(raw_frame)
    try:
        ax25 = AX25Frame.from_bytes(raw_frame)
    except Exception as e:
        print(f"Unable to parse X25 due to {e}")
        _inc_stat("datatype-NoParse-X25")
        return
    
    try:
        x = aprs.InformationField.from_bytes(ax25.info)
        _inc_stat(str(x.data_type))
    except:
        x = None
        _inc_stat("datatype-NoParse")
        return 


    result = {}
    p = [str(n) for n in ax25.path]
    result["path"] = p
    result["from"] = ax25.source # This will be updated if it's a third party!
    result["ax25_source"] = ax25.source
    result["to"] = ax25.destination # This will be updated if it's a third party!
    result["ax25_dst"] = ax25.destination
    result["control"] = hex(ax25.control.v[0])
    result["payload-type"] = None
    result["is-third-party"] = False

    print("src:",ax25.source, "dst:",ax25.destination, "path:",p, "control", hex(ax25.control.v[0]), "pid", ax25.pid, "info", ax25.info)
    
    if x is None:
        print(f"   Unable to parse")
    else:
        print(f"   {x.data_type}")
        

    if x is not None and x.data_type == aprs.DataType.THIRD_PARTY_TRAFFIC:
        # reparse the information field?
        result["is-third-party"] = True
        try:
            payload_as_str = ax25.info[1:].decode("ascii")
            ax25_third = AX25Frame.from_str(payload_as_str)
            #print("   ", ax25_third)
            p_third = [str(n) for n in ax25_third.path]
            print("   ", "src:",ax25_third.source, "dst:",ax25_third.destination, "path:",p_third, "control", hex(ax25_third.control.v[0]), "pid", ax25_third.pid, "info", ax25_third.info)
            info = ax25_third.info
            x = aprs.InformationField.from_bytes(info)
            _inc_stat(str(x.data_type))
        except UnicodeDecodeError as e:
            print("unable to ascii decode third party payload")
            x = None
            result["payload-type"] = None
        except:
            x = None
            result["payload-type"] = None
            _inc_stat("datatype-NoParseThirdParty")

        print("datatype:", x)

    # we have X, decode it..
    if x is not None:
        result["payload-type"] = str(x.data_type)

        if  isinstance(x, aprs.PositionReport):
            print("position")

    return result 

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
