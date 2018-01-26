import msvcrt
import zmq
import random
import sys
import time

try:
    port = "5556"
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.setsockopt(zmq.SNDHWM, 3)
    socket.connect("tcp://192.168.1.130:%s" % port) #hedgehog ip

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            print("Key pressed: %s" %key )
            key = str(key)
            if "w" in key:
                test = "fwd|0"
                socket.send_string(test)
            if "s" in key:
                test = "bwd|0"
                socket.send_string(test)
            if "a" in key:
                test = "lft|0"
                socket.send_string(test)
            if "d" in key:
                test = "rgt|0"
                socket.send_string(test)

except Exception as e:
    print(str(e))
    input()
