from flask import Flask, jsonify
from flask_cors import CORS
import json, os, datetime, requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

FILE = "leaderboard_cache.json"
INTERVAL = 600
VERSION = "0.6.0"
AMOUNT = 500
LEADERBOARD_IDS = [
    "5803f9e963625804e3de3246d043dc7dde847aa32e991f7f7326b0453f1fa038",
    "7eac4fee1111152cfba4d3737410264ca0f22c7f5a2211e79f0099589b8b48c0",
]
API_BASE = "https://vps.kodub.com/v6/leaderboard"

cache = {"data": [], "updated_at": None}

if os.path.exists(FILE):
    try:
        with open(FILE) as f:
            cache = json.load(f)
        print(f"Loaded cache from file, last updated {cache.get('updated_at')}")
    except Exception as e:
        print(f"Failed to load cache file: {e}")


def is_stale():
    if not cache.get("updated_at"):
        return True
    last = datetime.datetime.fromisoformat(cache["updated_at"].rstrip("Z"))
    return (datetime.datetime.utcnow() - last).total_seconds() > INTERVAL


def fetch_leaderboards():
    print(f"[{datetime.datetime.utcnow()}] Fetching leaderboards...")
    results = []
    for i, board_id in enumerate(LEADERBOARD_IDS):
        try:
            r = requests.get(
                f"{API_BASE}?version={VERSION}&trackId={board_id}&skip=0&amount={AMOUNT}",
                timeout=10,
                verify=False
            )
            r.raise_for_status()
            results.append(r.json())
            print(f"  ✓ {board_id[:12]}...")
        except Exception as e:
            print(f"  ✗ {board_id[:12]}... failed: {type(e).__name__}: {e}")
            old = cache["data"][i] if i < len(cache["data"]) else {"error": "unavailable"}
            results.append(old)
    cache["data"] = results
    cache["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    try:
        with open(FILE, "w") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Failed to save cache file: {e}")


@app.route("/")
def index():
    if is_stale():
        fetch_leaderboards()
    updated_at = datetime.datetime.fromisoformat(cache["updated_at"].rstrip("Z"))
    next_update = updated_at + datetime.timedelta(seconds=INTERVAL)
    return jsonify({
        "updated_at": cache["updated_at"],
        "next_update": next_update.isoformat() + "Z",
        "track_count": len(cache["data"]),
    })


@app.route("/leaderboard/<int:index>")
def single(index):
    if is_stale():
        fetch_leaderboards()
    if index < 0 or index >= len(cache["data"]):
        return jsonify({"error": "index out of range"}), 404
    updated_at = datetime.datetime.fromisoformat(cache["updated_at"].rstrip("Z"))
    next_update = updated_at + datetime.timedelta(seconds=INTERVAL)
    return jsonify({
        "updated_at": cache["updated_at"],
        "next_update": next_update.isoformat() + "Z",
        "data": cache["data"][index]
    })


@app.route("/leaderboards")
def all_leaderboards():
    if is_stale():
        fetch_leaderboards()
    updated_at = datetime.datetime.fromisoformat(cache["updated_at"].rstrip("Z"))
    next_update = updated_at + datetime.timedelta(seconds=INTERVAL)
    return jsonify({
        "updated_at": cache["updated_at"],
        "next_update": next_update.isoformat() + "Z",
        "data": cache["data"]
    })


if __name__ == "__main__":
    app.run(debug=False)
