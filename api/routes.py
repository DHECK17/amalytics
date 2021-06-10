import json
import threading
from datetime import datetime

import requests
from flask import Blueprint, abort, jsonify, request
from flask_cors import CORS
from sites.models import Website

from .models import Click

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


def get_location_and_create_click(ip: str, data: dict):
    extraas = {
        "ip": ip,
        "location": get_country_from_ip(ip),
        "created_at": datetime.now().date().isoformat(),
    }
    data.update(extraas)
    Click.create(data)


@api.post("/click")
def click():
    ip = request.remote_addr
    if ip == "127.0.0.1":
        abort(400, "Local addresses not supported")

    data: dict = json.loads(request.data)
    domain_exist = Website.get_website(data.get("domain"))
    if domain_exist is None or domain_exist == []:
        abort(400, "Domain not registered")
    threading.Thread(target=get_location_and_create_click).start()
    return jsonify(hello="world")
