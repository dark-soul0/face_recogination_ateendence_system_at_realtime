import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage



cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://face-recogination-43d52-default-rtdb.firebaseio.com/",
    'storageBucket': "face-recogination-43d52.appspot.com"
})




#importing the student images
folderPath = 'images'
pathlist = os.listdir(folderPath)
# print(pathlist)

imglist = []
studentids = []
for path in pathlist:
    imglist.append(cv2.imread(os.path.join(folderPath, path)))
    studentids.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket =storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


    # print(studentids)
# print(len(imglist))

def findEncodings(imagelist):
    encodeList=[]
    for img in imagelist:
        img= cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("encoding started....")
encodeListKnown = findEncodings(imglist)
encodeListKnownwithids =[encodeListKnown,studentids]

print("encoding complete")
file = open("encoingfile.p",'wb')
pickle.dump(encodeListKnownwithids,file)
file.close()
print(("file close"))