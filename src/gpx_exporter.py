"""
Export a GPX for a given source in a APRS dump
"""

import argparse
import aprs
import aprslib
import framecap
import gpxpy.gpx

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Export GPS(GPX) Data from APRS frame capture")

    parser.add_argument("-cap", type=str, required=True, help="capture file to read")
    parser.add_argument("-gpx", type=str, required=True, help="gpx file to create")
    parser.add_argument("-source", type=str, required=True, help="source name to filter")
    args = parser.parse_args()


    # Open up the capture file
    f_cap = open(args.cap, "r")
    reader = framecap.FrameReader(f_cap)


    # Setup the gpx oject
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)



    # Setup the on_frame
    def _on_frame(ts, frame):
        aprs_frame = aprs.parse_frame(frame)
        try:
            par = aprslib.parse(str(aprs_frame))
        except (aprslib.exceptions.ParseError, aprslib.exceptions.UnknownFormat) as e:
            return

        # filter source
        if par['from'] != args.source:
            return

        #This is the packet
        lat_lon = [par.get("latitude", None), par.get("longitude", None)]
        if None in lat_lon:
            return

        kwargs = {}
        if "altitude" in par:
            kwargs["elevation"] = par["altitude"]

        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(*lat_lon, **kwargs))
        print(par)

    # Read through the whole file.....
    d = reader.read_next()
    while d is not None:
        ts, frame = d
        _on_frame(ts, frame)
        d = reader.read_next()

    # file all done, write output
    with open(args.gpx, "w") as f_gpx:
        f_gpx.write(gpx.to_xml())
