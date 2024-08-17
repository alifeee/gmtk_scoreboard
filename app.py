"""Scoreboard server"""

import sqlite3
import os
from typing import Tuple
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
SQLITE_FILENAME = os.environ["SQLITE_FILENAME"]

app = Flask(__name__)


def db_connect() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Connect to database and get cursor"""
    con = sqlite3.connect(SQLITE_FILENAME)
    return con, con.cursor()


@app.route("/")
def hello_world():
    """Test endpoint"""
    return "<p>Hello, World!</p>"


@app.route("/scoreboard/top", methods=["GET"])
def scoreboard_top():
    """get the top scores for a timeframe
    can specify:
    - timeframe
    - total number
    e.g.,
      curl -s "http://127.0.0.1:5000/scoreboard/top?total=10&timeframe=daily"
    """
    total = request.args.get("total")
    timeframe = request.args.get("timeframe")
    unique = request.args.get("unique")
    if unique in [None, True, 1, "1"]:
        unique = True
    elif unique in ["0", 0, False]:
        unique = False
    else:
        unique = True

    if timeframe == "daily":
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        earliest_date = today
    if timeframe == "weekly":
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        start = today - timedelta(days=today.weekday())
        earliest_date = start
    if timeframe == "alltime":
        earliest_date = datetime(1970, 1, 1)

    earliest_date_str = earliest_date.strftime("%Y-%m-%d %H:%M:%S.%f")

    _, cur = db_connect()
    if unique is False:
        res_obj = cur.execute(
            """
        SELECT name, max_height, time_building_s, time_scaling_s FROM scores
        WHERE
            timestamp > ?
        LIMIT ?
    """,
            [
                earliest_date_str,
                total,
            ],
        )
    else:
        res_obj = cur.execute(
            """
        SELECT name, MAX(max_height), time_building_s, time_scaling_s FROM scores
        WHERE
            timestamp > ?
              and
            spurious = 0
        GROUP BY name
        LIMIT ?
    """,
            [
                earliest_date_str,
                total,
            ],
        )

    res = res_obj.fetchall()
    results = [
        {
            "name": r[0],
            "max_height": r[1],
            "time_building_s": r[2],
            "time_scaling_s": r[3],
        }
        for r in res
    ]
    return jsonify(results)
    # return f"tot: {total}\ntimeframe: {timeframe}\nbefore: {earliest_date_str}\n"


@app.route("/score/new", methods=["POST"])
def score_new():
    """add a new score to the board!
    e.g.,
      curl -s -H "Content-Type: application/json" --request POST "http://127.0.0.1:5000/score/new" --data "@score.json"
    """
    json = request.get_json()

    con, cur = db_connect()
    cur.execute(
        """
    INSERT INTO scores VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """,
        [
            json["timestamp"],
            json["name"],
            json["max_height"],
            json["time_total_s"],
            json["time_building_s"],
            json["time_scaling_s"],
            json["blocks_placed"],
            json["jumps"],
            json["distance_fallen"],
        ],
    )
    con.commit()
    id_ = cur.lastrowid
    return jsonify({"success": True, "id": id_})
