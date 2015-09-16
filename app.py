from flask import Flask, jsonify, request
from pymongo import MongoClient
from config import db
from config import gcmKey
from gcm import GCM
import json
app = Flask(__name__)

@app.route('/updateTT', methods=['POST'])
def update_timetable():
	if request.method == "POST":
		data = request.json
		dt = jsonify(data)
		b =  data['batch']
		if data['batch'] == int(b):
			print int(b)
		
		gcm = GCM(gcmKey)
		users = db.users.find({"batch" : b})
		#print users
		reg_ids = []
		for i in users:
			reg_ids.append(i['registration_id'])
			#print i, "lol"

		print len(reg_ids)
		response = gcm.json_request(registration_ids=reg_ids, data=data['data'])
		return "YOLO"+"\n"


@app.route('/register', methods=['POST'])
def add_user():
	if request.method == "POST":
		rollno = request.form['rollnumber']
		reg_id = request.form['regno']
		print request.form
		batch_det = rollno[:-3]
		db.users.insert({
				"rollnumber": rollno,
				"registration_id": reg_id,
				"batch": batch_det
				})
		return jsonify(({"Signed Up" :1}))

if __name__ =="__main__":
  app.run(debug=True)

