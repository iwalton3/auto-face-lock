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
import re

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

def approved_others(faces_in_photo, list_of_approved_faces):
    all_users_approved = False
    for img in list_of_approved_faces:
        face_comp = face_recognition.compare_faces(img, faces_in_photo, tolerance=settings.tolerance)
        if face_comp[0] == True:
            if len(faces_in_photo) > 1:
                all_users_approved = approved_others(faces_in_photo[1:], list_of_approved_faces)
            else:
                all_users_approved = True
            break
    return all_users_approved

face_data = []
if not os.path.isfile(face_data_path):
    print("You do not have an authorized face in the system.")
    train = True
    while train:
        input("Please press enter to capture your face information.")
        img = get_img()
        data = face_recognition.face_encodings(img)
        if not data:
            log.error("Could not detect a face. Exiting...")
            sys.exit(1)
        face_data.append(data[0])
        with open(face_data_path, 'w') as json_file:
            for entry in face_data:
                json_file.write(numpy.array2string(entry) + "\n")
        res = input("Would you like to train the model more? (y/n): ")
        if not res or not res.lower()[0] == 'y':
            train = False
else:
    with open(face_data_path, 'r') as json_file:
        strings = json_file.read().split(']\n')
        for entry in strings:
            entry = entry.replace('\n',"")
            entry = re.sub(' +', ',', entry)
            face_data.append(numpy.fromstring(entry[1:], dtype=float, sep=','))
    del face_data[-1]

while True:
    time.sleep(settings.interval)
    try:
        img = get_img()
    except RuntimeError:
        log.error("Cannot capture image for verification.")
        continue

    is_present = False
    is_unauth_present = False

    faces_in_photo = face_recognition.face_encodings(img)
    if faces_in_photo:
        log.debug(f"Detected {len(faces_in_photo)} face(s) in photo.")
        for stored_face in face_data:
            face_comp = face_recognition.compare_faces(stored_face, faces_in_photo, tolerance=settings.tolerance)
            if True in face_comp:
                is_present = True
                is_unauth_present = not approved_others(faces_in_photo, face_data)
            else:
                is_unauth_present = not approved_others(faces_in_photo, face_data)
            if is_present:
                break

    log.debug(f"is_present: {is_present}, is_unauth_present: {is_unauth_present}")

    should_blank = False
    should_unblank = False
    should_lock = False

    if is_present and not is_unauth_present:
        should_unblank = True

    if is_unauth_present and settings.blank_if_unknown:
        should_blank = True
        should_unblank = False

    if is_unauth_present and settings.lock_if_unknown:
        should_lock = True
        should_unblank = False

    if is_unauth_present and not is_present and settings.lock_if_np_unkn:
        should_lock = True
        should_unblank = False

    if not is_present and settings.lock_if_not_present:
        should_lock = True

    if not is_present and settings.blank_if_not_present:
        should_blank = True
        should_unblank = False

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
