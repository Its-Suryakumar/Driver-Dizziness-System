from sys import argv
from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
import time
import call
import requests
import numpy as np

t = 0.01
def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear

thresh = 0.25
frame_check = 5
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

#cap=cv2.VideoCapture(0)
flag=0
reset = False

try:
    ip = argv[1]
except:
    print("Enter IP of webcam!")
    exit(1)
    
#ip = "http://192.168.43.1:8080"
url = ip + "/shot.jpg"

while True:
	imgResp = requests.get(url)
	imgNp = np.array(bytearray(imgResp.content),  dtype=np.uint8)
	frame = cv2.imdecode(imgNp, -1)
	#ret, frame=cap.read()
	frame = imutils.resize(frame, width=450)
	frame = imutils.rotate(frame, 180)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	subjects = detect(gray, 0)
	for subject in subjects:
		shape = predict(gray, subject)
		shape = face_utils.shape_to_np(shape)#converting to NumPy Array
		leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart:rEnd]
		leftEAR = eye_aspect_ratio(leftEye)
		rightEAR = eye_aspect_ratio(rightEye)
		ear = (leftEAR + rightEAR) / 2.0
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
		if ear < thresh:
			flag += 1
			print (flag)
			if flag >= frame_check:
				cv2.putText(frame, "****************ALERT!****************", (10, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
				cv2.putText(frame, "****************ALERT!****************", (10,325),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
				if not reset:
					reset = True
					call.call("SOS!!! You've been registered as the emergency contact for <Person>","+919884026065")
		else:
			flag = 0
			reset = False
	#cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("x"):
		cv2.destroyAllWindows()
		#cap.release()
		break