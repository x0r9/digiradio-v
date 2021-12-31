import aprs
import framecap
import aprslib

out_file = open("out.csv", "w")

def on_frame(ts, frame):
    """
    demo frame decode
    """
    #print("---")

    a = aprs.parse_frame(frame)
    #print(type(a), a)
    #print(a.source, a.destination, a.path, "!!!", a.info)
    #print(type(a.info))
    #print(a.info.data, a.info.data_type, a.info.safe)

    try:
        par = aprslib.parse(str(a))
        #print(par)
    except aprslib.exceptions.ParseError as e:
        print("No parse")
        return
    except aprslib.exceptions.UnknownFormat as e:
        print("unkown format")
        return

    # Does it contain all the following?
    s = f"{ts}, {par['from']}, {par.get('latitude','')}, {par.get('longitude','')}, {par.get('comment', '')}"
    print(s)
    out_file.write(s+"\n")
    #a = aprs.Frame(frame)
    #print(a)
    #a = aprs.Frame(frame[1:])
    #print(a)
    #print(dir(a))
    #src = a.source
    #dst = a.destination
    #print(src, dst)

if __name__ == "__main__":
    f = open("delete-me.txt", "r")

    reader = framecap.FrameReader(f)

    d = reader.read_next()
    while d is not None:
        ts, frame = d

        #print(ts, frame)
        on_frame(ts, frame)

        d = reader.read_next()
