import cv2
import numpy
import json
import os
import collections
import operator
import glob
import sys
from flask import Flask,render_template
from PIL import Image
import socket
import thread
import base64
import time
lb=100
last=""
place=""
cascadePath="haarcascade_frontalface_default.xml"
label={1:"Rishu",2:"Bholu",3:"Mom",100:"None"}
detail={1:"Drawing Room",2:"Couch",3:"Kitchen"}
# Used for timing
FLANN_INDEX_KDTREE=1
files = []
stack=[]
matcher = None
def handler():
	os.system("python move.py img.jpg")
def get_image(image_path):
	print image_path
	return cv2.imread(image_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def get_image_features(image):
	# Workadound for missing interfaces
	sift = cv2.SIFT()
	surf = cv2.FeatureDetector_create("SURF")
	surf.setInt("hessianThreshold", 60)
	surf_extractor = cv2.DescriptorExtractor_create("SURF")
	#kp1, des1 = sift.detectAndCompute(img1,None)
	# Get keypoints from image
	keypoints = surf.detect(image, None)
	# Get keypoint descriptors for found keypoints
	keypoints, descriptors = surf_extractor.compute(image, keypoints)
	#keypoints,descriptors=sift.detectAndCompute(image,None)
	return keypoints, numpy.array(descriptors)
	#return keypoints,descriptors
def trained_index():
	flann_params = dict(algorithm = 1, trees = 4)
	matcher = cv2.FlannBasedMatcher(flann_params, {})
	l=glob.glob("*.npy")
	for i in l:
		f=i.split(".jpg")[0]
		files.append(f)
		descriptors=numpy.load(i)
		matcher.add([descriptors])
	matcher.train()
	return matcher
def train_index():
	# Prepare FLANN matcher
	flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 3)
	matcher = cv2.FlannBasedMatcher(flann_params, dict(checks=50))
	#fp=open("abc.xml","wb")
	# Train FLANN matcher with descriptors of all images
	co=0
	for f in os.listdir("img/"):
		co+=1
		print "Processing " + f
		print f
		image = get_image("./img/%s" % (f,))
		keypoints, descriptors = get_image_features(image)
		#print descriptors
		numpy.save(f+".npy",descriptors)
		matcher.add([descriptors])
		files.append(f)

	print "Training FLANN."
	matcher.train()
	#matcher.save_index("record.xml")
	#matcher.save("record.xml")
	#fp.write(matcher)
	print "Done."
	return matcher

def match_image(index, image,lb):
	lb1=lb
	# Get image descriptors
	image = get_image(image)
	keypoints, descriptors = get_image_features(image)
	# Find 2 closest matches for each descriptor in image
	matches = index.knnMatch(descriptors, k=2)
	
	# Cound matcher for each image in training set
	print "Counting matches..."
	count_dict = collections.defaultdict(int)
	for match in matches:
		# Only count as "match" if the two closest matches have big enough distance
		if match[0].distance < 0.7 * match[1].distance:
			image_idx = match[0].imgIdx

			count_dict[files[image_idx]] += 1
		
	#message="espeak 'hi "+label[lb]+"'"
	#os.system(message)
	# Get image with largest count
	matched_image = max(count_dict.iteritems(), key=operator.itemgetter(1))[0]
	size=len(count_dict.keys())
	# Show results
	print "Images", files
	print "Counts: ", count_dict
	print "==========="
	print "Hit: ", matched_image,count_dict[matched_image]
	print "==========="
	count=count_dict[matched_image]
	#mapping=int(matched_image.split(".")[0].replace("scene",""))
	return matched_image,count,size
flann_matcher=train_index()
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
udpsock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
addr=('',33333)
udpsock.bind(addr)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("192.168.0.2",3333))
s.listen(True)
#place,add=udpsock.recvfrom(1024)
place=raw_input("Place: ")
print place
conn,add=s.accept()
timeout=time.time()+120
while True:
	print place
	length=int(recvall(conn,16))
	data=recvall(conn,length)
	print data
	if time.time()>timeout:
		flag="back"
		conn.send(str(len(flag)).ljust(16))
		conn.send(flag)
	img=base64.decodestring(data)
	with open("img.jpg","wb") as f:
		f.write(img)
	matched_image,count,size=match_image(flann_matcher,"img.jpg",lb)
	print matched_image,count
	matched_image=matched_image.split(".")[0]
	if count>=25 and matched_image==place:
		flag="true"
		conn.send(str(len(flag)).ljust(16))
		conn.send(flag)
		print "sent "+flag
	else:
		flag="false"
		conn.send(str(len(flag)).ljust(16))
		conn.send(flag)
		print "sent "+flag
	#if count>=15:
	#	print detail[mapping]
	#thread.start_new_thread(handler,())
print "hello"
#udpsock.sendto("reached "+place,add)