import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://face-recogination-43d52-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')
data = {
    "223":
        {
            "name": "sonu samrat",
            "major": "student",
            "starting_year": 2022,
            "total_attendence":4,
            "standing": "s",
            "year":4,
            "last_attendence_time": "2023-10-03 02:31:56"
        },
    "1125":
        {
            "name": "sharban samrat",
            "major": "student",
            "starting_year": 2023,
            "total_attendence":4,
            "standing": "l",
            "year":3,
            "last_attendence_time": "2023-10-03  02:37:56"
        }
}


for key,value in data.items():
    ref.child(key).set(value)