#!/usr/bin/python3
"""
create a route /status on the object app_views that returns a JSON:
"status": "OK"
"""
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
from models import storage
from api.v1.views import app_views
from flask import jsonify


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status():
    """ Status of API """
    return jsonify({"status": "OK"})


@app_views.route('/stats', methods=['GET'], strict_slashes=False)
def stats():
    """ Retrieves the number of each objects by type """
    objects = {"amenities": storage.count(Amenity),
               "cities": storage.count(City),
               "places": storage.count(Place),
               "reviews": storage.count(Review),
               "states": storage.count(State),
               "users": storage.count(User)}
    return jsonify(objects)
