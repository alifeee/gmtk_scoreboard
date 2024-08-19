"""Scoreboard server"""

import sqlite3
import os
from typing import Tuple
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
SQLITE_FILENAME = os.environ["SQLITE_FILENAME"]

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


def db_connect() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Connect to database and get cursor"""
    con = sqlite3.connect(SQLITE_FILENAME)
    return con, con.cursor()


@app.route("/")
@cross_origin()
def hello_world():
    """Test endpoint"""
    return render_template("index.html")


@app.route("/scoreboard/top", methods=["GET"])
@cross_origin()
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

    if unique in ["0", 0, False, "False"]:
        unique = False
        sqlformat = {
            "height": "max_height",
            "groupby": "",
        }
    else:
        unique = True
        sqlformat = {
            "height": "MAX(max_height)",
            "groupby": "GROUP BY name",
        }

    _, cur = db_connect()

    sql = """
    SELECT name, {height}, timestamp FROM scores
        WHERE
            timestamp > ?
              and
            spurious = 0
        {groupby}
        ORDER BY
          {height} DESC
        LIMIT ?
    """.format(
        **sqlformat
    )

    res_obj = cur.execute(
        sql,
        [
            earliest_date_str,
            total,
        ],
    )

    res = res_obj.fetchall()
    results = [{"name": r[0], "max_height": r[1], "timestamp": r[2]} for r in res]
    data = {"scores": results}

    all_accepts = request.headers.get("Accept", "")
    accepts = all_accepts.split(",")
    if "text/html" in accepts:
        return render_template(
            "scoreboard.html",
            scores=data["scores"],
            total=total,
            timeframe=timeframe,
            unique=unique,
        )
    return data


@app.route("/scoreboard/new", methods=["GET"])
@cross_origin()
def scoreboard_new():
    """get the most recent scores
    can specify:
    - total
    e.g.,
      curl -s "http://127.0.0.1:5000/scoreboard/new?total=10"
    """
    total = request.args.get("total")
    _, cur = db_connect()

    res_obj = cur.execute(
        """
        SELECT name, max_height, timestamp FROM scores
        ORDER BY
            timestamp DESC
        LIMIT ?
    """,
        [total],
    )
    res = res_obj.fetchall()
    results = [
        {
            "name": r[0],
            "max_height": r[1],
            "timestamp": r[2],
        }
        for r in res
    ]
    data = {"scores": results}

    all_accepts = request.headers.get("Accept", "")
    accepts = all_accepts.split(",")
    if "text/html" in accepts:
        return render_template(
            "scores.html",
            scores=data["scores"],
            total=total,
        )
    return data


@app.route("/score/new", methods=["POST"])
@cross_origin()
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
