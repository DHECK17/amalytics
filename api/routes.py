import json
import threading
from datetime import datetime
from hashlib import sha256
from os import getenv
from urllib.parse import urlparse

import app
import requests
from flask import Blueprint, abort, jsonify, request
from flask_cors import CORS
from sites.models import Website
from user_agents import parse

from .models import Click

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


def hash_sha256(payload: str) -> str:
    m = sha256()
    m.update(payload.encode())
    return m.hexdigest()


def get_location_and_create_click(ip: str, data: dict):
    extraas = {
        "ip": ip,
        "location": get_country_from_ip(ip),
        "created_at": datetime.now().date().isoformat(),
    }
    if data.get("outerWidth") >= 1000:
        data["device"] = "Desktop"
    else:
        data["device"] = "Mobile"

    try:
        del data["outerWidth"]
    except KeyError:
        pass

    # sanitize page url
    page_url: str = data.get("pageURL")
    data["pageURL"] = urlparse(page_url).netloc

    data.update(extraas)
    Click.create(data)


@api.post("/click")
def click():
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    data: dict = json.loads(request.data)
    page = data.get("pageURL")
    referrer = data.get("referrer")
    domain = data.get("domain")

    if referrer == "":
        referrer = "Direct"
    elif urlparse(referrer).netloc == domain:
        referrer = ""
    else:
        referrer = urlparse(referrer).netloc.removeprefix("www.")

    try:
        if referrer[-1] == "/":
            referrer = referrer[:-1]
    except IndexError:
        pass

    data.update(referrer=referrer)

    hashable_string = f"{ip}-{user_agent}-{page}"
    user_hash = hash_sha256(hashable_string)

    if app.redis_client.get(user_hash) is None:
        if ip == "127.0.0.1":
            abort(400, "Local addresses not supported")

        domain_exist = Website.get_website(data.get("domain"))
        if domain_exist is None or domain_exist == []:
            abort(400, "Domain not registered")

        browser, os = None, None

        if user_agent is not None:
            user_agent = parse(user_agent)
            browser = user_agent.browser.family
            os = user_agent.os.family

        data.update(browser=browser, os=os)
        app.redis_client.set(user_hash, "+", getenv("HASH_EXPIRY"))

        # run in background
        threading.Thread(
            target=get_location_and_create_click,
            args=(
                ip,
                data,
            ),
        ).start()
    return jsonify(hello="world")
