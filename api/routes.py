import json

import requests
from flask import Blueprint, jsonify, request
from flask_cors import CORS

api = Blueprint("api", __name__, url_prefix="/api")
CORS(api, resources={r"/api/click": {"origins": "*", "headers": "Content-Type"}})


def get_country_from_ip(ip: str) -> str:
    endpoint = f"https://ipapi.co/{ip}/json/"
    result = requests.get(endpoint).json()
    location = {
        "country": result.get("country_code"),
        "location": {
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
        },
    }
    return location


@api.post("/click")
def click():
    data: dict = json.loads(request.data)
    data.update({"ip": request.remote_addr})
    data.update({"location": get_country_from_ip(request.remote_addr)})
    print(data)
    return jsonify(data)
