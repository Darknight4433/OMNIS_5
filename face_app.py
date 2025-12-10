#!/usr/bin/env python3

import os
import pickle
from datetime import datetime
import sys
import threading
from time import sleep
import queue
import time
import cv2
import numpy as np
import cvzone
import face_recognition

from speaker import speak, is_speaking

imgBackground = cv2.imread('Resources/background.png')

def import_modes() -> list:
    # Importing the mode images to a list
    folderModePath = 'Resources/Modes'
    modePathList = os.listdir(folderModePath)
    imgModeList = []

    # print(modePathList)
    for path in sorted(modePathList):
        imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

    return imgModeList


def import_encodings():
    print('Reading Encoding Files..')
    with open(r'images/encoded_file.p', 'rb') as fp:
        encode_list_known_with_ids = pickle.load(fp)
    encode_list_known, studentNames = encode_list_known_with_ids
    print("Loaded Encoding File.")
    return encode_list_known, studentNames


def mark_faces(face_location, backgroundImage, success: bool):
    y1, x2, y2, x1 = face_location
    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
    # set offset for imgBackground
    bbox = (55+x1, 162+y1, x2 - x1, y2 - y1)
    if success:
        backgroundImage = cvzone.cornerRect(backgroundImage, bbox=bbox, rt=0)
        return backgroundImage
    
    cv2.rectangle(backgroundImage, (55+x1, 162+y1), (x2, y2), (0, 0, 255), 2, cv2.LINE_AA)
    return backgroundImage


def update_mode(backgroundImage, modeType):
    modeImage = import_modes()[modeType]
    backgroundImage[44:44 + 633, 808:808 + 414] = modeImage
    return backgroundImage


def update_student_details(studentImage, studentName, backgroundImage):
    (w, h), _ = cv2.getTextSize(studentName, cv2.FONT_HERSHEY_COMPLEX, 1, 1)
    offset = (414 - w) / 2
    cv2.putText(backgroundImage, str(studentName), (808 + int(offset), 445),
                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
    backgroundImage[175:175 + 216, 909:909 + 216] = studentImage

    return backgroundImage


def load_face_image(id: str):
    return cv2.imread(f'images/faces/{id}.jpg')


def main_task():
    global imgBackground
    previous_id = None
    speaker_task_timer = time.time() - 20
    cap = cv2.VideoCapture(0)

    imgModeList = import_modes()
    mode_type = 0
    encode_list_known, studentNames = import_encodings()

    while True:
        
        if not cap.isOpened():
            cap.release()
            sleep(1)
            cap = cv2.VideoCapture(0)
            continue

        _, img = cap.read()

        if not _:
            print('[OpenCV] Error: Cap object error')
            break

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        face_current_frame = face_recognition.face_locations(imgS)
        encode_current_frame = face_recognition.face_encodings(imgS, face_current_frame)

        imgBackground[162:162+480, 55:55+640] = img
        imgBackground[44:44+633, 808:808+414] = imgModeList[mode_type]

        if face_current_frame:
            for encodeFace, faceLoc in zip(encode_current_frame, face_current_frame):
                matches = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.4)
                face_distance = face_recognition.face_distance(encode_list_known, encodeFace)
                # print(f'Matches: {matches}')
                # print(f'Face Distance: {face_distance}')

                match_index = np.argmin(face_distance)
                # print("Match Index: ", match_index)
                if matches[match_index]:
                    # print(f"Known Face Detected: {studentNames[match_index]}")
                    mode_type = 1
                    name = studentNames[match_index]
                    # Update Student details 
                    studentImage = load_face_image(name)
                    imgBackground = mark_faces(faceLoc, imgBackground, 1)
                    imgBackground = update_mode(imgBackground, mode_type)
                    imgBackground = update_student_details(studentImage=studentImage, 
                                                           studentName=name, 
                                                           backgroundImage=imgBackground)
                    
                    print(f'Speaker Status: {is_speaking()}')
                    if previous_id != name and time.time() - speaker_task_timer > 15 and not is_speaking():
                        previous_id = name
                        speaker_task_timer = time.time()
                        speak([f'Hello {name}. Welcome to MGM Model school'])

                else:
                    # Reset Student Details when face is not recognised.
                    mode_type = 0
                    imgBackground = update_mode(imgBackground, mode_type)
                    imgBackground = mark_faces(faceLoc, imgBackground, False)
                    
        else:
            # Reset Student details when no face founds
            mode_type = 0
            speaker_flag = 1
            imgBackground = update_mode(imgBackground, mode_type)

        output = cv2.resize(imgBackground, (0, 0), None, 1.5, 1.5)
        # output = cv2.resize(imgBackground, (0, 0), None, 1.245, 1.245)
        window_name = 'Face Application'
        cv2.namedWindow(window_name)
        cv2.moveWindow(window_name, 1, 1)
        cv2.imshow(window_name, output)
        if cv2.waitKey(1) == ord('q') & 0xff:
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':

    
    main_task()
