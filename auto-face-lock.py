#!/usr/bin/env python3

import cv2
import face_recognition
import os
import os.path
import json
import logging
import time
import numpy
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format="%(asctime)s [%(levelname)8s] %(message)s")
log = logging.getLogger('')

from conf import settings
import conffile
import autoblank

settings.load(conffile.get("auto-face-lock",'conf.json'))
face_data_path = conffile.get("auto-face-lock",'face_data.json')
blank = autoblank.AutoBlank()
blank.start()
cam = None

last_lock = False
last_blank = False
last_unblank = False
lock_inactive_ct = 0

def get_img():
    global cam
    if cam is None:
        cam = cv2.VideoCapture(0)
    s, img = cam.read()
    if settings.release_after_img:
        cam.release()
        cam = None
    if not s:
        raise RuntimeError("Cannot capture image.")
    return img

face_data = None
if not os.path.isfile(face_data_path):
    print("You do not have an authorized face in the system.")
    input("Please press enter to capture your face information.")
    img = get_img()
    face_data = face_recognition.face_encodings(img)[0]
    with open(face_data_path, 'w') as json_file:
        json.dump(list(face_data), json_file)
else:
    with open(face_data_path, 'r') as json_file:
        face_data = numpy.array(json.load(json_file))

while True:
    time.sleep(settings.interval)
    try:
        img = get_img()
    except RuntimeError:
        log.error("Cannot capture image for verification.")
        continue
    
    faces = face_recognition.face_encodings(img)
    face_comp = face_recognition.compare_faces(faces, face_data, tolerance=settings.tolerance)

    is_present = False
    is_other_present = False
    for face_match in face_comp:
        if face_match:
            is_present = True
        else:
            is_other_present = True
    
    log.debug(f"is_present: {is_present}, is_other_present: {is_other_present}")

    should_blank = False
    should_unblank = False
    should_lock = False

    if is_present:
        should_unblank = True
    
    if is_other_present and settings.blank_if_unknown:
        should_blank = True
        should_unblank = False
    
    if is_other_present and settings.lock_if_unknown:
        should_lock = True
        should_unblank = False
    
    if not is_present and settings.lock_if_not_present:
        should_lock = True

    lock_tolerance = settings.lock_tolerance
    if lock_tolerance > 0 and should_lock:
        if lock_inactive_ct < lock_tolerance:
            should_lock = False
            lock_inactive_ct += 1
            log.debug(f"Lock tolerance {lock_inactive_ct}/{lock_tolerance}")
    else:
        lock_inactive_ct = 0

    if should_lock and not last_lock:
        log.info("Locking...")
        os.system(settings.lock_cmd)
        blank.blank()
    elif should_blank and not last_blank:
        log.info("Blanking screen...")
        blank.blank()
    elif should_unblank and not last_unblank:
        log.info("Unblanking screen...")
        blank.unblank()

    last_lock = should_lock
    last_blank = should_blank
    last_unblank = should_unblank
