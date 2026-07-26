#!/usr/bin/env python3
"""QuakeWatch: recent earthquake monitor, focused on the Lake Kivu /
Albertine Rift region (Rwanda / eastern DRC border) with a worldwide view.

Data source: USGS Earthquake Hazards Program (public, no API key needed).
https://earthquake.usgs.gov/fdsnws/event/1/
"""
import socket
from datetime import datetime, timedelta, timezone

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.after_request
def add_server_header(response):
    """Tag every response with the hostname that served it (for demos)."""
    response.headers["X-Served-By"] = socket.gethostname()
    return response

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Rough bounding box covering Rwanda, Burundi, Lake Kivu and the
# Virunga volcanic area of eastern DRC (the seismically active part
# of the Albertine Rift closest to Rwanda).
KIVU_BOUNDS = {
    "minlatitude": -4.0,
    "maxlatitude": 0.5,
    "minlongitude": 27.0,
    "maxlongitude": 31.0,
}

WINDOWS = {
    "day": timedelta(days=1),
    "week": timedelta(days=7),
    "month": timedelta(days=30),
    "year": timedelta(days=365),
}


def felt_note(magnitude):
    """Return a short plain-language note about a quake's likely impact."""
    if magnitude is None:
        return "Magnitude unknown"
    if magnitude < 2.5:
        return "Usually not felt"
    if magnitude < 4.5:
        return "Often felt, damage unlikely"
    if magnitude < 6.0:
        return "Can damage weak structures"
    if magnitude < 7.0:
        return "Can be destructive in populated areas"
    return "Major earthquake, serious damage likely"


@app.route("/")
def index():
    """Serve the QuakeWatch single-page frontend."""
    return render_template("index.html")


@app.route("/api/quakes")
def quakes():
    """Proxy the USGS earthquake feed with the filters the frontend asks for."""
    region = request.args.get("region", "kivu")
    window = request.args.get("window", "week")
    sort = request.args.get("sort", "time")
    try:
        min_mag = float(request.args.get("min_mag", "0"))
    except ValueError:
        min_mag = 0.0

    delta = WINDOWS.get(window, WINDOWS["week"])
    end = datetime.now(timezone.utc)
    start = end - delta

    params = {
        "format": "geojson",
        "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": end.strftime("%Y-%m-%dT%H:%M:%S"),
        "minmagnitude": min_mag,
        "orderby": "magnitude" if sort == "magnitude" else "time",
        "limit": 200,
    }
    if region == "kivu":
        params.update(KIVU_BOUNDS)

    try:
        response = requests.get(USGS_URL, params=params, timeout=10)
    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Couldn't reach the earthquake data source. Try again shortly."
        }), 503

    if response.status_code != 200:
        return jsonify({
            "error": "The earthquake data source returned an error."
        }), 502

    try:
        data = response.json()
        features = data.get("features", [])
    except ValueError:
        return jsonify({"error": "Received an unexpected response."}), 502

    results = []
    for feature in features:
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [None, None, None])
        magnitude = props.get("mag")
        quake_time = props.get("time")
        iso_time = None
        if quake_time:
            iso_time = datetime.fromtimestamp(
                quake_time / 1000, tz=timezone.utc
            ).isoformat()
        results.append({
            "place": props.get("place", "Unknown location"),
            "magnitude": magnitude,
            "time": iso_time,
            "depth_km": coords[2] if len(coords) > 2 else None,
            "lat": coords[1] if len(coords) > 1 else None,
            "lon": coords[0] if len(coords) > 0 else None,
            "url": props.get("url"),
            "note": felt_note(magnitude),
        })

    return jsonify({"count": len(results), "quakes": results})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
