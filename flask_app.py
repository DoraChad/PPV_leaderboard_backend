from flask import Flask, jsonify
from flask_cors import CORS
import json, os, datetime, requests, threading
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

FILE = "leaderboard_cache.json"
INTERVAL = 120
VERSION = "0.6.0"
AMOUNT = 500
LEADERBOARD_IDS = [
  "20ea0dbd62c28316ee86e20b04bb14f3acb89d036c5da16b3cb4a9b19a9232e4",
  "35794467f853b175704c32193ee5f329b5fb68274168f336a5054bf6264b1558",
  "736b2fa1b10b4fe208f41e9ddd1f2dd74eeb424fc15b3e612d4929649f60508a",
  "82125bc5d07e32951b52ae7fa885d1ef25618bc861f9fd6334eb3500dd440e34",
  "3583b7427394e5e2a641f274b8df5de6aab2de65c2286b14e312565df86ca885",
  "10971f1719821603d8c1a0a454da10cf60ea5d0a3c1caab3455d46e36b416dd3",
  "6628ac96adf10a46d25e30947b9b5685d3c2285209e0b0d40f7e9b240046c03d",
  "ea89139a2174dd5126dd1bf7f052168ebab3830abcde7fa9c2a8da4b1c560e54",
  "bd379d3b9000a2f71988ab15bf6947f61c392c269760a87a3555338be5d1886b",
  "e8bddc248df6500693a0a3e6bc6a0b8a6402651f5c80f9f07b658be851656c56",
  "16c7b10b85e60edfb77b7abeb60a41309028e16c111e2f98a45b82dda4521d80",
  "0628e2f4048caecbf046101e752e6882f33718cfe7b44621e7af998b994637e8",
  "d732e13555164f4bb04c131d97aca6dfb201876f4999bc4f3da4d3995ce90c76",
  "5cd274a01ebb26e79257207b9dc4b96ec33b468b2322eee37341eafb227bf097",
  "5188224e1d00283d6b356ce0923b372ed0152122fe7a9ae98b4782ec1c5a3df4",
  "b93526c71fcb7495a93e4389a2a42d9423d2c79fc160b9f17db6a272e8b6c3ed",
  "5b91db62c77e459a117c8fc70dd03a4c7475a14885e0dcbf5c97a3774222b0e2",
  "de13cc263d749ced2d58d592d8aa780580656d688c6bf1fc4b8dc983a9901859",
  "63beb77d3c6a890ddf75c52bb67d92903348d753ff5d728da19d05a3c72236da",
  "c527bf9068717a38cdcf74518bebea99dea4ff2a8628226dab00405dd689ac25",
  "ea9a772843483576928c47f3ccf5d56b5424be602f8f0bf36a2f5ff6c48cc36f",
  "cc2375750a8cec6591404dadb96dfb63d9f137b5b0a4bb523c8bbf431ab7ed02",
  "d17f7999a1730ff62e76673d224a49d3c8f755490039dadd110c602ad24efafe",
  "16288b12a2e25524f4883fa7366d97b0f636f8c01709023d3376bd4944b6f0cc",
  "20ff8de46a7eb6e9b5c4403ad138a8e9d030edd3ec77a3f02aa39258b5f0292b",
  "8fb027b02209b911d1a56d862afe735bfc03c5d18721a5f295173a8fde64c267",
  "96cb4398554ef8062e9c0aee738704030e73a03250c252a559dfc09718cf1603",
  "43c73c0e3f307d4a7df01e3d90f9af8784f98881e5650c856e1a169daa8c2d65",
  "17efc8131e4696371497fcd355915bf5091efe1314705426d44a140ce109174f",
  "a982c7be5f836075f253fb4d40d0af9b7c4e05d93e349256a7f14681b2df157c",
  "361935298abe8dee7d95ad5776016f0eaab16a408d705110fafa4041563e5da0",
  "2b2b97180e2b3087ab5f3bcef3ff7616e328d56f13a51290fad2f06bd7f03c38",
  "6ba8f6297960b668f1ce98be1ae8a8cf491a15792e6ac30c74fd9217d8a50b95",
  "866bca1f1d2aedc5dbbefcda30d76e60c2019e7b3362f152336ad23156b24fc1",
  "01d7d36ef021d6680b12faea78e9278f6bfcf63a55ea2c7d48a38cd2122791db",
  "fcc6b8817c801eaaeea0455130e592ff5989eb97bb2aad6fb975f4d709460daf",
  "360016a9ccaf42cbb5bbe90b36069e3ba615c640b451d25bf7b14a091bb15140",
  "691ff65d547d079608217b19616c70cb102691956cf344b73d0267b9328e489d",
  "ddd8808544dd1b719f397b51bd7374455737e0c8d2d2e77274ac407da161ec1c",
  "ca2c575bca007e4f1670526538700cd1ce2df7527d90f32e9d761dd0db8027f1",
  "ccdaee0539402f633b13ddf1b2100c6a56bfcbbdca6053050c283bfc7959a331",
  "5dbf4bb61a4ffe14c25ba3173ccc2c548d4b5a28292b215b44d0ed4fc0f74463",
  "68f600b30716f430818b7f5165c28e54c5925bfeaa9d9bf3a84f402fa766fdfd",
  "90cda57f339684d20961765c16cb4ad49dcdb28db1cf474bbc691614b5396c47",
  "0bad92a5eac84fcc1e01e6c1d89353aca73e12d1a598f5607f4ee3130316dcbb",
  "17f82495bddf50a6610ad1874a184cd4bf635b269d1aa1df4abfcfd8b8aed847",
  "ff8e2dfb0b6056b3e785ff6e383ca004352d193cdad1f5ff0cea847b65ba174d",
  "caf1784817929f44c3d847582928862560d8e448f89190afe52bf832116fd7f9",
  "6cb20e2a983f5518b9fa0351b798781e272e8f1b227484a24dd10d37be122374",
  "0fcff40be442f4acedc9383c1ae927b4c6488683772061352045f17d00cc150c"
]
API_BASE = "https://vps.kodub.com/v6/leaderboard"

API_BASE = "https://vps.kodub.com/v6/leaderboard"

cache = {"data": [], "updated_at": None}
cache_lock = threading.Lock()

if os.path.exists(FILE):
    try:
        with open(FILE) as f:
            cache = json.load(f)
        print(f"Loaded cache from file, last updated {cache.get('updated_at')}")
    except Exception as e:
        print(f"Failed to load cache file: {e}")

def fetch_one(args):
    board_id, i = args
    try:
        r = requests.get(
            f"{API_BASE}?version={VERSION}&trackId={board_id}&skip=0&amount={AMOUNT}",
            timeout=5
        )
        r.raise_for_status()
        print(f"  ✓ {board_id[:12]}...")
        return r.json()
    except Exception as e:
        print(f"  ✗ {board_id[:12]}... failed: {type(e).__name__}: {e}")
        with cache_lock:
            return cache["data"][i] if i < len(cache["data"]) else {"error": "unavailable"}

def fetch_leaderboards():
    print(f"[{datetime.datetime.utcnow()}] Fetching leaderboards...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_one, [(bid, i) for i, bid in enumerate(LEADERBOARD_IDS)]))

    with cache_lock:
        cache["data"] = results
        cache["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"

        try:
            with open(FILE, "w") as f:
                json.dump(cache, f)
        except Exception as e:
            print(f"Failed to save cache file: {e}")

def updater():
    while True:
        try:
            fetch_leaderboards()
        except Exception as e:
            print(f"Updater error: {e}")
        time.sleep(INTERVAL)

def start_background_thread():
    thread = threading.Thread(target=updater, daemon=True)
    thread.start()

start_background_thread()

def build_meta():
    with cache_lock:
        updated_at = cache.get("updated_at")

    if not updated_at:
        return None, None

    updated_dt = datetime.datetime.fromisoformat(updated_at.rstrip("Z"))
    next_update = updated_dt + datetime.timedelta(seconds=INTERVAL)

    return updated_at, next_update.isoformat() + "Z"

@app.route("/")
def index():
    updated_at, next_update = build_meta()
    return jsonify({
        "updated_at": updated_at,
        "next_update": next_update,
        "track_count": len(cache["data"])
    })

@app.route("/leaderboard/<int:index>")
def single(index):
    with cache_lock:
        if index < 0 or index >= len(cache["data"]):
            return jsonify({"error": "index out of range"}), 404
        data = cache["data"][index]

    updated_at, next_update = build_meta()

    return jsonify({
        "updated_at": updated_at,
        "next_update": next_update,
        "data": data
    })

@app.route("/leaderboards")
def all_leaderboards():
    with cache_lock:
        data = cache["data"]

    updated_at, next_update = build_meta()

    return jsonify({
        "updated_at": updated_at,
        "next_update": next_update,
        "data": data
    })

if os.environ.get("GUNICORN_CMD_ARGS") is not None:
    start_background_thread()
elif __name__ == "__main__":
    start_background_thread()
