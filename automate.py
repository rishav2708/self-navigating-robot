import RPi.GPIO as io
import base64
import thread
import time
import socket
import os
import thread
def delay1():
	cnt=1
	for in range(70000):
		cnt+=1
def delay2():
	cnt=1
	for i in range(10000):
		cnt+=1
def recvall(sock, count):
    buf = b''
    while count:
    	print "in loop"
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf
def goBack():
	io.output(in1_pin,io.HIGH)
    io.output(in2_pin,io.LOW)
	io.output(in3_pin,io.HIGH)
	io.output(in4_pin,io.LOW)
def goLeft():
	io.output(in1_pin,io.HIGH)
    io.output(in2_pin,io.LOW)
    io.output(in3_pin,io.LOW)
    io.output(in4_pin,io.LOW)
def stop():
	io.output(in1_pin,io.LOW)
	io.output(in2_pin,io.LOW)
	io.output(in3_pin,io.LOW)
	io.output(in4_pin,io.LOW)
def goRight():
	io.output(in1_pin,io.LOW)
	io.output(in2_pin,io.LOW)
	io.output(in3_pin,io.HIGH)
	io.output(in4_pin,io.LOW)
	print "Moved Right"
def goForward():
	io.output(in1_pin,io.LOW)
	io.output(in2_pin,io.HIGH)
	io.output(in3_pin,io.LOW)
	io.output(in4_pin,io.HIGH)
def moveForward():
	goForward()
	time.sleep(3)
	goRight()
	time.sleep(1)
	

io.setmode(io.BCM)
in1_pin=4
in2_pin=17
in3_pin=27
in4_pin=22
io.setup(in1_pin,io.OUT)
io.setup(in2_pin,io.OUT)
io.setup(in3_pin,io.OUT)
io.setup(in4_pin,io.OUT)
TCP_IP = '192.168.0.4'
TCP_PORT = 3333
sock=socket.socket()
sock.connect((TCP_IP,TCP_PORT))
while (1):
	os.system("fswebcam -r 1024x768 -S 10 img.jpg")
	capture=open("img.jpg").read()
	stringData=base64.b64encode(capture)
	sock.send(str(len(stringData)).ljust(16))
	sock.send(stringData)
	length=int(recvall(sock,16))
	flag=recvall(sock,length)
	deg=0
	steps=0
	if flag=="true"
		#do something (send the robot straight)
		goForward()
		for i in range(2000):
			steps+=1
		stop()

	else:
		#do something
		if deg>=60:
			goLeft()
			for i in range(6000):
				deg-=1
			stop()
		else:
			goRight()
			for i in range(6000):
				deg+=1