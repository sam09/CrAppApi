from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['CrApp']

gcmKey = "AIzaSyAYqpFRv7IbSOxVszGkXxvy61DsEbm6tcU"