import json
import threading
from datetime import datetime

import requests
from flask import Blueprint, abort, jsonify, request
from flask_cors import CORS
from flask_login import login_required
from sites.models import Website

from .models import Click
from .utils import get_data_for_a_period, referrer_count

api = Blueprint("api", __name__, url_prefix="/api")
CORS(api, resources={r"/api/click": {"origins": "*", "headers": "Content-Type"}})


def get_country_from_ip(ip: str) -> str:
    endpoint = f"http://ip-api.com/json/{ip}"
    result = requests.get(endpoint).json()
    location = {
        "country": result.get("countryCode"),
        "location": {
            "latitude": result.get("lat"),
            "longitude": result.get("lon"),
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
    # run in background
    threading.Thread(
        target=get_location_and_create_click,
        args=(
            ip,
            data,
        ),
    ).start()

    return jsonify(hello="world")


@api.get("/<path:website>/analytics")
@login_required
def analytics_data(website: str):
    data = Click.get_click_data(website)
    if data is None:
        return jsonify(None)
    result = dict()
    result.update(
        {"referrer": referrer_count(data)},
        {"click_count": get_data_for_a_period(data)},
    )
    return jsonify(data)
