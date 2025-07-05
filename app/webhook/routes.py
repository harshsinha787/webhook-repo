from flask import Blueprint, request, jsonify, send_from_directory,current_app
from ..extensions import mongo
from datetime import datetime
import os

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

# Route when Action-Repo Git triggers an Action
@webhook.route('/receiver', methods=["POST"])
def receiver():
    # Access "events" collection in "webhook_db" database
    collection = mongo.db.events
    # Get body from json request
    data = request.json
    # Get Action from json request-header
    action_type = request.headers.get("GitHubEvent")

    if action_type == "push":
        # Prepare in format to store PUSH info on webhook_db
        event = {
            "request_id": data.get("head_commit", {}).get("id", ""),
            "author": data.get("pusher", {}).get("name", "unknown"),
            "action": "PUSH",
            "from_branch": "",
            "to_branch": data.get("ref", "refs/heads/unknown").split("/")[-1],
            "timestamp": datetime.now()
        }
        # Store to webhook_db
        collection.insert_one(event)

    elif action_type == "pull_request":
        # Get Pull/Merge Request Data from request body
        pr_data = data.get("pull_request", {})
        # Prepare in format to store PULL/MERGE info on webhook_db
        event = {
            "request_id": str(pr_data.get("id", "")),
            "author": pr_data.get("user", {}).get("login", "unknown"),
            "action": "PULL_REQUEST" if not pr_data.get("merged") else "MERGE",
            "from_branch": pr_data.get("head", {}).get("ref", ""),
            "to_branch": pr_data.get("base", {}).get("ref", ""),
            "timestamp": datetime.now()
        }
        # Store to webhook_db
        collection.insert_one(event)
    # Respond with Success in JSON format
    return jsonify({"status": "success"}), 200

# Route when Webpage-UI requests a read from webhook_db
@webhook.route("/UI_ReadEvents", methods=["GET"])
def get_events():
    # Access "events" collection in "webhook_db" database
    collection = mongo.db.events
    # Sort last 10 events in decending order of time
    events = list(collection.find().sort("timestamp", -1).limit(10))
    for e in events:
        # Convert ID to string
        e["_id"] = str(e["_id"])
        # Convert datetime Timestamp to ISO format string
        e["timestamp"] = e["timestamp"].isoformat()
    # Return as JSON
    return jsonify(events)

# Route when opening Webpage-UI on browser
@webhook.route("/webpage", methods=["GET"])
def index():
    # Points to 'index.html' which is for Webpage-UI on browser.
    # Run http://localhost:5000/webhook/webpage on browser to see
    return send_from_directory(os.path.join(current_app.root_path, "frontend"), 'index.html')
