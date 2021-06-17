from flask import Flask, request, jsonify, render_template, redirect
import numpy as np
import cv2
from matplotlib import pyplot as plt
import glob
from werkzeug.utils import secure_filename
import os
import csv
import dbase

app = Flask(__name__)

UPLOAD_FOLDER = '/home/arushshah/imagematcher/imagesToMatch/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
user_choice = None
cur_screen = None
choice_received = False
screen_files = []

database = "blindtouchbot.db"

conn = dbase.create_connection(database)
cur = conn.cursor()

def getImg(imgName):
	#MIN_MATCH_COUNT = 10
	MIN_MATCH_COUNT = 5
	FLANN_INDEX_KDTREE = 0
	MAX_MATCHES = 0
	MAX_GOOD = []
	MAX_KP1 = None
	MAX_KP2 = None
	MAX_DES1 = None
	MAX_DES2 = None
	# Initiate SIFT detector
	sift = cv2.xfeatures2d.SIFT_create()

	index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
	search_params = dict(checks = 50)

	flann = cv2.FlannBasedMatcher(index_params, search_params)

	imgName = "imagesToMatch/" + str(imgName)
	img1 = cv2.imread(imgName,0) # trainImage

	img1 = cv2.rotate(img1, cv2.ROTATE_180)

	IMG2BEST = None
	imgName = ""

	dst = None

	for filepath in glob.iglob('imagesToMatch/templates/*'):
		img2 = cv2.imread(filepath,0)
		# find the keypoints and descriptors with SIFT
		kp1, des1 = sift.detectAndCompute(img1,None)
		kp2, des2 = sift.detectAndCompute(img2,None)

		matches = flann.knnMatch(des1,des2,k=2)
		# store all the good matches as per Lowe's ratio test.
		good = []
		for m,n in matches:
			if m.distance < 0.7*n.distance:
					good.append(m)
	  if (len(good) > MAX_MATCHES):
			MAX_MATCHES = len(good)
			MAX_GOOD = good
			IMG2BEST = img2
			MAX_KP1 = kp1
			MAX_KP2 = kp2
			MAX_DES1 = des1
			MAX_DES2 = des2
			imgName = filepath

	if len(MAX_GOOD)>MIN_MATCH_COUNT:
	    src_pts = np.float32([ MAX_KP1[m.queryIdx].pt for m in MAX_GOOD ]).reshape(-1,1,2)
	    dst_pts = np.float32([ MAX_KP2[m.trainIdx].pt for m in MAX_GOOD ]).reshape(-1,1,2)

	    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
	    matchesMask = mask.ravel().tolist()

	    h,w = img1.shape
	    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
	    dst = cv2.perspectiveTransform(pts,M)

	    img2 = cv2.polylines(IMG2BEST,[np.int32(dst)],True,255,3, cv2.LINE_AA)

	else:
	    print "Not enough matches are found - %d/%d" % (len(MAX_GOOD),MIN_MATCH_COUNT)
	    matchesMask = None


	draw_params = dict(matchColor = (0,255,0), # draw matches in green color
		           singlePointColor = None,
		           matchesMask = matchesMask, # draw only inliers
		           flags = 2)

	img3 = cv2.drawMatches(img1,MAX_KP1,img2,MAX_KP2,MAX_GOOD,None,**draw_params)
	print(dst)
	botLeftX = int(dst[2][0][0])
	botLeftY = int(dst[2][0][1])
	botRightX = int(dst[3][0][0])
	botRightY = int(dst[3][0][1])
	
	img3 = cv2.circle(img2, (botLeftX, botLeftY), 20, (255, 0, 0), 2)
	img3 = cv2.circle(img2, (botRightX, botRightY), 20, (255, 0, 0), 2)
	xPos = int(botLeftX + (botRightX-botLeftX)/2.0 + 30)
	yPos = int((botLeftY + botRightY)/2.0 + 150)
	img3 = cv2.circle(img2, (xPos, yPos), 100, (255, 0, 0), 2)
	plt.imshow(img2, 'gray'),plt.show()

	print(imgName)

	imgName = imgName.split(".")[0]
	
	if imgName == "imagesToMatch/templates/cafe_menu.jpg":
		global screen_files
		screen_files = ["menu.csv", "checkout.csv", "payment.csv"]
		global cur_screen
		cur_screen = "cafe_menu"
	print("current screen is " + str(cur_screen))
	return str(imgName) + "," + str(xPos) + "," + str(yPos)

@app.route('/')
def index():
	return "<h1>Image Matcher</h1>"

@app.route('/match/', methods=['GET'])
def match():
    imgName = request.args.get("imgName", None)
    return getImg(str(imgName))

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
	filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "File uploaded"

@app.route('/selection', methods=['GET'])
def get_input():
	global choice_received
	if cur_screen is None:
		return "Error"
	f = open("imagesToMatch/csv/" + str(cur_screen) + ".csv")
	print("Opened file: " + str(cur_screen))
	options = []
	for line in f:
		print(line)
		args = line.split(',')
		if args[0] == "resolution":
			continue
		options.append(args[0])
	choice_received = False
	return render_template("input.html", selections=options)

@app.route('/select', methods=['POST'])
def process_input():
	global user_choice
	global choice_received
	user_choice = request.form['choice']
	print(user_choice)
	while not choice_received:
		pass
	return get_input()

@app.route('/getUserChoice', methods=['GET'])
def return_choice():
	global user_choice
	if user_choice is None:
		return "Error"
	tmp = user_choice
	user_choice = None

	global cur_screen
	global choice_received
	f = open("imagesToMatch/csv/" + str(cur_screen) + ".csv")
	for line in f:
		args = line.split(',')
		print(str(args))
		print(tmp)
		if args[0] == tmp:
			print(args[3])
			cur_screen = args[3]
			print("cur_screen: " + str(cur_screen))
			choice_received = True
			return str(args[1]) + "," + str(args[2])
	

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
