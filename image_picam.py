from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
import numpy as np

from picamera import PiCamera
from picamera.array import PiRGBArray

import time
import call

import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) 
GPIO.setup(12, GPIO.OUT)
p = GPIO.PWM(12, 1000)
p.start(50)

# Raspberry Pi pin configuration:
lcd_rs        = 25
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 18
lcd_d7        = 22
lcd_backlight = 4
lcd_columns = 16
lcd_rows    = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)

    
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

cam = PiCamera()


flag = 0
reset = False
while True:
    imgResp = PiRGBArray(cam)
    cam.capture(imgResp, format="bgr")
    frame = imgResp.array
    frame = imutils.resize(frame, width=450)
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
                            lcd.clear()
                            lcd.message('Alert!!! SOS')
                            cv2.putText(frame, "****************ALERT!****************", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.putText(frame, "****************ALERT!****************", (10,325),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            if not reset:
                                    reset = True
                                    call.call("SOS!!! You've been registered as the emergency contact for <Person>")
                    else:
                        lcd.clear()
                        lcd.message('Detecting...')
            else:
                    flag = 0
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("x"):
            cv2.destroyAllWindows()
            cap.release()
            break
