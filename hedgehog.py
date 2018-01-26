from time import sleep
from hedgehog.client import connect
import zmq

with connect(emergency=15) as hedgehog:
    hedgehog.set_input_state(0, True)
    try:
        print("test")
        port = "5556"
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.setsockopt(zmq.RCVHWM, 3)
        socket.bind("tcp://*:%s" % port)
        customSpeed = 500

        while True:
            msg = socket.recv_string()
            msg = msg.split('|')
            lastmsg = msg[0]

            print(msg[0])
            #currently not used, plans to implement  change of speed
            if msg[0] == "setSpeed":
                customSpeed = int(msg[1])
            elif msg[0] == "fwd":
                hedgehog.move(0,500)
                hedgehog.move(2,500)
                sleep(0.1)
            elif msg[0] == "bwd":
                hedgehog.move(0,-500)
                hedgehog.move(2,-500)
                sleep(0.1)
            elif msg[0] == "lft":
                hedgehog.move(0,500)
                hedgehog.move(2,-500)
                sleep(0.2)
                hedgehog.move(0,0)
                hedgehog.move(2,0)

            elif msg[0] == "rgt":
                hedgehog.move(0,-500)
                hedgehog.move(2,500)
                sleep(0.2)
                hedgehog.move(0,0)
                hedgehog.move(2,0)




    except Exception as e:
        print(str(e))
