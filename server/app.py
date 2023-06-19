#!/usr/bin/env python3

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance/app.db')}")

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Activity, Camper, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        try:
            campers = [c.to_dict( only=("age", "name", "id")) for c in Camper.query.all()]
            return campers, 200
        except:
            return {"error": "Bad request"}, 400
    
    def post(self):
        try:
            new_camper = Camper(
                name = request.json['name'],
                age = request.json['age']
            )
            db.session.add(new_camper)
            db.session.commit()

            new_camper_dict = new_camper.to_dict(only=("id", "name", "age"))

            return make_response(new_camper_dict, 201)
        except:
            return {"error": "400, ValidationError"}, 400

api.add_resource(Campers, "/campers")

class CamperById(Resource):
    def get(self, id):
        try:
            camper = Camper.query.filter(Camper.id == id).first().to_dict( only=("campers_activities", "age", "name", "id"))
            return make_response(camper, 200)
        except:
            return {"error": "404: Camper not found"}, 404

api.add_resource(CamperById, "/campers/<int:id>")
        
class Activities(Resource):
    def get(self):
        try:
            activities = [a.to_dict() for a in Activity.query.all()]
            return make_response(activities, 200)
        except:
            return {"error": "Bad request"}, 400
    
api.add_resource(Activities, "/activities")

class ActivityById(Resource):
    def patch(self, id):
        try:
            data = request.get_json()
            activity = Activity.query.filter(Activity.id == id).first()
            for attr in data:
                setattr(activity, attr, data.get(attr))
            db.session.add(activity)
            db.session.commit()
            return make_response(activity.to_dict(), 202)
        except:
            return {"error": "Bad request"}, 400

    def delete(self, id):
        try:
            activity = Activity.query.filter(Activity.id == id).first()

            db.session.delete(activity)
            db.session.commit()

            return make_response({}, 204)
        except:
            return {"error": "Bad request"}, 404

api.add_resource(ActivityById, "/activities/<int:id>")

class Signups(Resource):
    def post(self):
        try:
            signup = Signup(
                time = request.json["time"],
                camper_id = request.json["camper_id"],
                activity_id = request.json["activity_id"],
            )

            db.session.add(signup)
            db.session.commit()
            return make_response(signup.to_dict(), 201)
        except:
            return {"error": "400, Validation error"}, 400
        
api.add_resource(Signups, "/signups")


if __name__ == '__main__':
    app.run(port=5555, debug=True)
