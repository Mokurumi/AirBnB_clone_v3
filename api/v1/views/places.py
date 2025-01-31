#!/usr/bin/python3
"""
handles all default RESTFul API actions for Place objects
"""
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.state import State
from api.v1.views import app_views
from flask import jsonify, abort, request


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places(city_id):
    """ Retrieves the list of all Place objects of a City """
    city = storage.get(City, city_id)
    if city:
        places = []
        for place in city.places:
            places.append(place.to_dict())
        return jsonify(places)
    abort(404)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """ Retrieves a Place object """
    place = storage.get(Place, place_id)
    if place:
        return jsonify(place.to_dict())
    abort(404)


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """ Deletes a Place object """
    place = storage.get(Place, place_id)
    if place:
        storage.delete(place)
        storage.save()
        return jsonify({}), 200
    abort(404)


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """ Creates a Place """
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    if not request.get_json():
        abort(400, "Not a JSON")
    if "user_id" not in request.get_json():
        abort(400, "Missing user_id")
    user = storage.get(User, request.get_json()["user_id"])
    if not user:
        abort(404)
    if "name" not in request.get_json():
        abort(400, "Missing name")
    place = Place(**request.get_json())
    place.city_id = city_id
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """ Updates a Place object """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    if not request.get_json():
        abort(400, "Not a JSON")
    for key, value in request.get_json().items():
        attributes = ["id", "user_id", "city_id", "created_at", "updated_at"]
        if key not in attributes:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def search_places():
    """ Retrieves all Place objects depending of the JSON in the body """
    # Check if request contains JSON data
    if request.get_json() is None:
        abort(400, description="Not a JSON")

    # Retrieve JSON data from request
    data = request.get_json()

    # Extract states, cities, and amenities from the JSON data
    states = data.get('states', None)
    cities = data.get('cities', None)
    amenities = data.get('amenities', None)

    # If no filter criteria provided, return all places
    if not data or not (states or cities or amenities):
        places = [place.to_dict() for place in storage.all(Place).values()]
        return jsonify(places)

    # Filter places based on states, cities, and amenities criteria
    places_list = []
    if states:
        for state_id in states:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            places_list.append(place)

    if cities:
        for city_id in cities:
            city = storage.get(City, city_id)
            if city:
                for place in city.places:
                    if place not in places_list:
                        places_list.append(place)

    if amenities:
        if not places_list:
            places_list = storage.all(Place).values()
        amenities_objs = []
        for amenity_id in amenities:
            amenity = storage.get(Amenity, amenity_id)
            if amenity:
                amenities_objs.append(amenity)
        for place in places_list:
            if all(amenity in place.amenities for amenity in amenities_objs):
                places_list.append(place)

    # Prepare places to be returned in the response
    places = []
    for place in places_list:
        place_dict = place.to_dict()
        place_dict.pop('amenities', None)
        places.append(place_dict)

    return jsonify(places)
