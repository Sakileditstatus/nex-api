from flask import Flask, request, jsonify
import requests
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

REMOTE_API = "https://nexapk.in/getcat.php"

def clean_app_data(app_data):
    cleaned = dict(app_data)
    if isinstance(cleaned.get("tags"), list):
        cleaned["tags"] = ", ".join(cleaned["tags"])
    return cleaned

@app.route("/", methods=["GET"])
def get_app_details():
    package = request.args.get("package")
    if not package:
        return jsonify({
            "success": False,
            "error": "Missing ?package=",
            "developer": "NexAPK x ENZO"
        }), 400

    try:
        response = requests.get(REMOTE_API, timeout=10)
        response_data = response.json()
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Remote API unreachable",
            "details": str(e),
            "developer": "NexAPK x ENZO"
        }), 500

    if not response_data.get("success"):
        return jsonify({
            "success": False,
            "error": "Remote API failure",
            "developer": "NexAPK x ENZO"
        }), 502

    apks = response_data.get("apks", [])
    for app_data in apks:
        if app_data.get("slug") == package or app_data.get("package_name") == package:
            return jsonify({
                "success": True,
                "developer": "NexAPK x ENZO",
                "data": clean_app_data(app_data)
            })

    return jsonify({
        "success": False,
        "error": "Package not found",
        "developer": "NexAPK x ENZO"
    }), 404

app.wsgi_app = ProxyFix(app.wsgi_app)

def handler(environ, start_response):
    return app(environ, start_response)
