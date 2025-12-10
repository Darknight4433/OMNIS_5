import os

import cv2
import face_recognition
import pickle

# Importing the Student images
folderPath = r'images/faces'
PathList = os.listdir(folderPath)
imgList = []
studentIds = []
print(PathList)

for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(path.split('.')[0])

    filename = f'{folderPath}/{path}'

print(studentIds)


def find_encodings(images_list):
    encode_list = []
    for img in images_list:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)

    return encode_list


if __name__ == '__main__':
    print("Encoding Started...")
    encode_list_known = find_encodings(imgList)
    encode_list_known_with_ids = [encode_list_known, studentIds]
    print(f"Encoding complete.")

    with open('images/encoded_file.p', 'wb') as f:
        pickle.dump(encode_list_known_with_ids, f)

    print('Encoding file saved')
