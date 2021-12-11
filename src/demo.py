import kiss
import aprs
import framecap
import time


f = open("delete-me.txt", "a")
capture = framecap.FrameWriter(f)


def on_aprs_frame(frame):
    """
    callback from Kiss client
    """
    print(type(frame), frame)
    a = aprs.Frame(frame)
    print(a)
    capture.write_frame(time.time(), frame)

if __name__ == "__main__":
    kclient = kiss.TCPKISS("0.0.0.0", port=8001)

    kclient.start()
    kclient.read(callback=on_aprs_frame)
