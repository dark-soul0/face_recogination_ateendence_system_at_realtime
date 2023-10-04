import cvzone
import os
import pickle
import cv2
import face_recognition
import numpy as np
from datetime import datetime

# it is imported at the time of setud of database
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recogination-43d52-default-rtdb.firebaseio.com/",
    'storageBucket': "face-recogination-43d52.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread('Resources/background.png')

folderModePath = 'Resources/Modes'
modepathlist = os.listdir(folderModePath)
imgModelist = []
for path in modepathlist:
    imgModelist.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModelist))

# import the encoding file
print("loading encode file.............")

file = open("encoingfile.p", 'rb')
encodeListKnownwithids = pickle.load(file)
file.close()
encodeListKnown, studentids = encodeListKnownwithids
# print(studentids)
print("encode file loaded")

modetype = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgs = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgs)
    encodeCurrentFrame = face_recognition.face_encodings(imgs, faceCurrentFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[modetype]

    for encodeface, faceLoc in zip(encodeCurrentFrame, faceCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeface)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeface)
        # print("matches",matches)
        # print("faceDis",faceDis)

        matchindex = np.argmin(faceDis)
        # print(matchindex)

        if matches[matchindex]:
            # print("known face detected: ")
            # print(studentids[matchindex])
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentids[matchindex]
            if counter == 0:
                cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                # cv2.imshow("Face Attendance", imgBackground)
                cv2.waitKey(1)
                counter = 1
                modetype = 1


    if counter !=0:
        if counter == 1:
            studentsinfo = db.reference(f'Students/{id}').get()
            print(studentsinfo)

            # get image form database
            blob = bucket.get_blob(f'images/{id}.png')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)


            # update the data of attendance

            datetimeObject = datetime.strptime(studentsinfo['last_attendence_time'],
                                             "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
            print(secondsElapsed)
            if secondsElapsed>30:
                ref = db.reference(f'Students/{id}')
                studentsinfo['total_attendence'] += 1
                ref.child('total_attendence').set(studentsinfo['total_attendence'])
                ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else :
                modetype = 3
                counter = 0
                imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[modetype]

        if modetype != 3:

            if 10< counter <20:
                modetype=2
                imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[modetype]



            if counter <=10:
                cv2.putText(imgBackground, str(studentsinfo['total_attendence']), (861, 125),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                cv2.putText(imgBackground, str(studentsinfo['major']), (1006, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(id), (1006, 493),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentsinfo['standing']), (910, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentsinfo['starting_year']), (1125, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                cv2.putText(imgBackground, str(studentsinfo['year']), (1025, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                (w, h), _ = cv2.getTextSize(studentsinfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)

                offset = (414 - w) // 2

                cv2.putText(imgBackground, str(studentsinfo['name']), (808 + offset, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (100, 100, 100), 1)

                imgBackground[175:175 + 218, 909:909 + 216] = imgStudent

            counter += 1

            if counter>=20:
                counter =0
                modetype= 0
                studentsinfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[modetype]

        else:
            print("unknown face")
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("you ch00se to exit.....")
        break

    cv2.imshow('face recogination', imgBackground)
    # cv2.imshow("web cam", img)

    # cv2.waitKey(1)
cap.release()
cv2.destroyAllWindows()
