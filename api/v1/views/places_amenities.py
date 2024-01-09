#!/usr/bin/python3
"""
link between Place objects and Amenity objects that handles
all default RESTFul API actions
"""
from models import storage
from models.place import Place
from models.amenity import Amenity
from api.v1.views import app_views
from flask import abort, jsonify, request
from os import getenv


@app_views.route('/places/<place_id>/amenities', methods=['GET'],
        strict_slashes=False)
def get_amenities(place_id):
    """ Retrieves the list of all Amenity objects of a Place """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    amenities = []

    if getenv("HBNB_TYPE_STORAGE") == "db":
        for amenity in place.amenities:
            amenities.append(amenity.to_dict())
    else:
        for amenity_id in place.amenity_ids:
            amenity = storage.get(Amenity, amenity_id)
            amenities.append(amenity.to_dict())
    return jsonify(amenities)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
        methods=['DELETE'], strict_slashes=False)
def delete_amenity(place_id, amenity_id):
    """ Deletes a Amenity object to a Place """
    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)
    if not place or not amenity:
        abort(404)
    if amenity not in place.amenities:
        abort(404)

    if getenv("HBNB_TYPE_STORAGE") == "db":
        place.amenities.remove(amenity)
    else:
        place.amenity_ids.remove(amenity_id)
    storage.save()
    return jsonify({}), 200


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
        methods=['POST'], strict_slashes=False)
def link_amenity(place_id, amenity_id):
    """ Link a Amenity object to a Place """
    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)
    if not place or not amenity:
        abort(404)
    if getenv("HBNB_TYPE_STORAGE") == "db":
        if amenity in place.amenities:
            return jsonify(amenity.to_dict()), 200
        place.amenities.append(amenity)
    else:
        if amenity_id in place.amenity_ids:
            return jsonify(amenity.to_dict()), 200
        place.amenity_ids.append(amenity_id)
    storage.save()
    return jsonify(amenity.to_dict()), 201
