from flask import Flask, render_template, jsonify
from redis import Redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Redis configuration
redis_client = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)), db=int(os.getenv("REDIS_DB", 0)), decode_responses=True)


def initialize_numbers():
    """Initialize the available numbers pool if not exists"""
    if not redis_client.exists("available_numbers"):
        numbers = list(range(1, 14))  # 1 to 13
        redis_client.sadd("available_numbers", *numbers)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/check_availability")
def check_availability():
    try:
        initialize_numbers()
        # Check if there are any numbers available
        count = redis_client.scard("available_numbers")
        return jsonify({"available": count > 0, "remaining": count})
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500


@app.route("/get_number")
def get_number():
    try:
        initialize_numbers()
        number = redis_client.spop("available_numbers")

        if number is None:
            return jsonify({"error": "All numbers have been assigned", "status": "failed"}), 404

        return jsonify({"number": int(number), "status": "success"})

    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500


@app.route("/reset", methods=["GET"])
def reset_numbers():
    try:
        redis_client.delete("available_numbers")
        initialize_numbers()
        return jsonify({"message": "Numbers reset successfully", "status": "success"})

    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500


if __name__ == "__main__":
    app.run(debug=True)
