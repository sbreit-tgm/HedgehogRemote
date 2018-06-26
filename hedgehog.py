import zmq
import json
import sys
from datetime import datetime
onHedgehog = False
inIDE = False
if not inIDE:
    hedgehogId = sys.argv[1]
else:
    hedgehogId = 0
    
if onHedgehog:
    from hedgehog.client import connect

#creates socket to receive messages
port = '733' + str(hedgehogId)
context = zmq.Context()
recvSocket = context.socket(zmq.PAIR)
recvSocket.bind('tcp://*:%s' % port)

#creates poller to create non blocking receive
poller = zmq.Poller()
poller.register(recvSocket, zmq.POLLIN)

controllerData = {}

#hedgehog data
if onHedgehog:
    hedgehog = connect(emergency=15)
leftWheelPort = 0
rightWheelPort = 1
standardSpeed = 500
stopTimer = 2000
speeds = {'left':0,'right':0}

#time deltas
lastControllerPacket = ''
lastReset = ''

def deltaTime(otherTime) -> int:
    now = datetime.now()
    if otherTime != '':
        delta = now - otherTime
        delta = int(delta.total_seconds() * 1000)
        return int(delta)
    else:
        return int(0)

def calcSpeed(leftX, leftTrigger, rightTrigger):
    if float(rightTrigger) > 0.0 and float(leftTrigger) == 0.0:
        return forwards(leftX,rightTrigger)
    elif float(leftTrigger) > 0.0 and float(rightTrigger) == 0.0:
        return backwards(leftX,leftTrigger)
    else:
        setSpeed(0,0)

def forwards(leftX, rightTrigger):
    #left: x<0
    #right: x>0
    if float(leftX) < 0.0:
        right = float(standardSpeed) * float(rightTrigger)
        left = float(right) * float(1.05 - float(leftX) * float(-1)) #1.05 because it should not become 0 at all
        
        setSpeed(left,right)
        
    elif float(leftX) > 0.0:
        left = float(standardSpeed) * float(rightTrigger)
        right = float(left) * float(1.05 - float(leftX))
        
        setSpeed(left,right)
        
    else:
        speed = float(standardSpeed) * float(rightTrigger)
        
        setSpeed(speed,speed)

def backwards(leftX, leftTrigger):
    #left: x<0
    #right: x>0
    if float(leftX) < 0.0:
        right = float(standardSpeed) * float(leftTrigger) * float(-1)
        left = float(right) * float(1.05 - float(leftX) * float(-1)) #1.05 because it should not become 0 at all
        
        setSpeed(left,right)
        
    elif float(leftX) > 0.0:
        left = float(standardSpeed) * float(leftTrigger) * float(-1)
        right = float(left) * float(1.05 - float(leftX))
        
        setSpeed(left,right)
        
    else:
        speed = float(standardSpeed) * float(leftTrigger) * float(-1)
        
        setSpeed(speed,speed)

def setSpeed(left, right):
    speeds['left'] = int(left)
    speeds['right'] = int(right)

def processPacket(packet):
    #processing order:
    #1. gather info from packet
    
    leftTrigger = packet['left_trigger']
    rightTrigger = packet['right_trigger']
    leftStickX = packet['l_thumb_x']
    leftStickY = packet['l_thumb_y']
    rightStickX = packet['r_thumb_x']
    rightStickY = packet['r_thumb_y']
    aButton = packet['13']
    bButton = packet['14']
    xButton = packet['15']
    yButton = packet['16']
    selectButton = packet['6']
    startButton = packet['5']

    #check for killing order
    if startButton == int(1):
        exit()

    #calculate speed of motor
    calcSpeed(leftStickX, leftTrigger, rightTrigger)

    #overrideSpeed
    if selectButton == int(1):
        setSpeed(0,0)

while True:
    #not necessary but taken from instruction until better understanding
    #zmq.POLLIN allows for non-blocking action
    sockets = dict(poller.poll(zmq.POLLIN))
    if recvSocket in sockets and sockets[recvSocket] == zmq.POLLIN:
        receive = recvSocket.recv_json()
        lastControllerPacket = datetime.now()
        controllerData = json.loads(receive)
        processPacket(controllerData)

    deltaPacket = deltaTime(lastControllerPacket)
    if deltaPacket > stopTimer:         
        setSpeed(0,0)
        print('Reset speeds.')
        
    if onHedgehog:
        hedgehog.move(leftWheelPort, speeds['left'])
        hedgehog.move(rightWheelPort, speeds['right'])
    else:
        print('%s - %s' % (speeds, deltaPacket))
