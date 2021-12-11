import aprs
import framecap

def on_frame(frame):
    """
    demo frame decode
    """
    print("---")
    a = aprs.Frame(frame)
    print(a)
    a = aprs.Frame(frame[1:])
    print(a)
    print(dir(a))
    src = a.source
    dst = a.destination
    print(src, dst)

if __name__ == "__main__":
    f = open("delete-me.txt", "r")

    reader = framecap.FrameReader(f)

    d = reader.read_next()
    while d is not None:
        ts, frame = d

        print(ts, frame)
        on_frame(frame)

        d = reader.read_next()
