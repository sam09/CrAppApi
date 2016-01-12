from flask import Flask, jsonify, request
from pymongo import MongoClient
from config import db
from config import gcmKey
import time
from config import parseAppId,parseRestAPIKey
from gcm import GCM
import json,httplib
import imaplib
import hashlib
app = Flask(__name__)
IMAP_SERVER='webmail.nitt.edu'

def hashify(string):
    hash_object = hashlib.sha1(string+"CruzadoMillyhak_DeltaIsGReaT"+str(time.time()))
    hex_dig = hash_object.hexdigest()
    return hex_dig

def verifyKey(username,key):
    usersinfo = db.users.find_one({
        "rollnumber" : username,
        "secret" : key
    })
    if userInfo == None:
        return False
    else:
        return True

@app.route('/' ,methods=['GET'])
def index():
    return "hello"

@app.route('/addCR',methods=['POST'])
def addCR():
    data=request.json
    username=data['username']
    password=data['password']
    a={
    "username": username ,
    "password": password
    }
    db.crlogin.insert(a)
    return "Success"

@app.route('/crlogin', methods=['POST'])
def crlogin():
    data=request.json
    username=data['username']
    password=data['password']
    check=db.crlogin.find_one({
    "username": username ,
    "password": password
    })
    if check is None :
        return jsonify(({"Signed Up" : 0}))
    else:
        secret = hashify(username)
        ab={
        "rollnumber" : username,
        "secret" : secret
        }
        try:
            db.usersInfo.remove({"rollnumber" :username})
            db.usersInfo.insert(ab)
        except:
            print "****cant add*****"
        return jsonify(({"Signed Up" : 1 , "secret" : secret}))

@app.route('/login', methods=['POST'])
def login():

      if request.method == "POST":
               data=request.json
               username = data['username']
               password = data['password']
               try:
                   imap = imaplib.IMAP4(IMAP_SERVER)
                   login = imap.login(username, password)
                   success = login[0]
                   if(success=='OK'):
                       print 'ok\n\n'
                       return jsonify({'logged_in':1})
               except:
                   print 'not ok\n\n\n'
                   return jsonify({'logged_in':0})

@app.route('/register', methods=['POST'])
def add_user():
	if request.method == "POST":
                data=request.json
		rollno = data['rollnumber']
		reg_id = data['regno']
		print request.form
		batch_det = rollno[:-3]
		db.users.insert({
				"rollnumber": rollno,
				"registration_id": reg_id,
				"batch": batch_det
				})
		return jsonify( ( { "Signed Up" : 1 } ) )

@app.route('/setTimeTable', methods=['POST'])
def setTimeTable():
    if request.method == "POST" :
        data = request.json
        rno = data['username']
        secret = data['secret']
        chk = db.usersInfo.find({
        "rollnumber" : rno
        })
        for i in chk:
            if(i["secret"]!=secret):
                return jsonify(({"Success" : 0 , "message" : "Nice Try :P"}))
            break

        batch = data["batch"]
        b={
        "batch": batch
        }
        check = db.fullTT.find_one(b)
        a ={
        "tt" : data["data"],
        "batch" : batch
        }
        if check is None :
            try:
                db.fullTT.insert(a)
            except:
                return jsonify(({"Error" : 1}))
        else:
            try:
                db.fullTT.remove(b)
                db.fullTT.insert(a)
            except:
                return jsonify(({"Error" : 1}))
        connection = httplib.HTTPSConnection('api.parse.com', 443)
        connection.connect()
        connection.request('POST', '/1/push', json.dumps({
               "channels": [
                 'nlr'+data['batch']
               ],
               "data": {"type": "tt"}
             }), {
               "X-Parse-Application-Id": parseAppId,
               "X-Parse-REST-API-Key": parseRestAPIKey,
               "Content-Type": "application/json"
             })
        result = json.loads(connection.getresponse().read())
        print result

        return jsonify(({"Success": 1}))

#getTimetable with batch
@app.route('/getTimetable/<batch>' , methods=['POST','GET'])
def getTimetable(batch):
    data = db.fullTT.find({
    "batch" : batch
    })
    if data is None :
        return jsonify(({"Success" : 0}))
    for i in data :
        return json.dumps(i['tt'])

#parse sending code
@app.route('/updateTT', methods=['POST'])
def update_timetable():
	if request.method == "POST":
		data = request.json
        rno = data['username']
        secret = data['secret']
        chk = db.usersInfo.find({
        "rollnumber" : rno
        })
        for i in chk:
            if(i["secret"]!=secret):
                return jsonify(({"Success" : 0 , "message" : "Nice Try :P"}))
            break

        connection = httplib.HTTPSConnection('api.parse.com', 443)
        connection.connect()
        connection.request('POST', '/1/push', json.dumps({
               "channels": [
                 'nlr'+data['batch']
               ],
               "data": data
             }), {
               "X-Parse-Application-Id": parseAppId,
               "X-Parse-REST-API-Key": parseRestAPIKey,
               "Content-Type": "application/json"
             })
        result = json.loads(connection.getresponse().read())
        print result
        return "YOLO"+"\n"

# Route is for backing up attendance
@app.route('/backup', methods= ['POST'] )
def backup():
	if request.method == "POST":
		data_array = request.json
        rno = data['username']
        secret = data['secret']
        chk = db.usersInfo.find({
        "rollnumber" : rno
        })
        for i in chk:
            if(i["secret"]!=secret):
                return jsonify(({"Success" : 0 , "message" : "Nice Try :P"}))
            break
        print data_array
        for data in data_array:
			attendance = db.attendance.find_one( {
						 "rollno" : data['rollno'],
						 "date-time" : data['date-time'],
						 "subject" : data['subject']
					 	})
			if attendance is None:
				try:
					db.attendance.insert(data)
				except:
					return jsonify( ( { "BackedUp": 0 } ) )
			else:
				try:
					db.attendance.remove(attendance)
					db.attendance.insert(data)
				except:
					return jsonify( ( { "BackedUp": 0 } ) )
        return jsonify( ( { "BackedUp": 1 } ) )



# To get attendance of a particular user
@app.route('/attendance', methods = ['POST'])
def get_attendance():
	if request.method == "POST":
		rollno = request.json['rollno']
		try:
			attendance = db.attendance.find( { "rollno" : rollno } )
			a = []
			for i in attendance:
				temp = {
					"rollno" : i['rollno'],
					"subject" : i['subject'],
					"date-time" : i['date-time'],
					"present" : i['present']
				}
				a.append(temp)
			a = json.dumps(a)
			return a
		except:
			return jsonify ( ( { "Error": 1 } ) )


if __name__ =="__main__":
  app.run(debug=True)
