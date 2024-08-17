"""Utilities for the scoreboard"""

import argparse
from typing import Tuple
import sqlite3
import os
import sys
import dateutil.parser
import subprocess
from dotenv import load_dotenv

load_dotenv()
SQLITE_FILENAME = os.environ["SQLITE_FILENAME"]


def db_connect() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Connect to database and get cursor"""
    con = sqlite3.connect(SQLITE_FILENAME)
    return con, con.cursor()


def command_one(args):
    """Do the first thing"""
    print(args)


def command_two(args):
    """Do the second thing"""
    print(args)


# ▄█████░█████▄░▄█████░▄████▄░████████░▄█████
# ██░░░░░██░░██░██░░░░░██░░██░░░░██░░░░██░░░░
# ██░░░░░█████▀░█████░░██░░██░░░░██░░░░█████░
# ██░░░░░██░░██░██░░░░░██████░░░░██░░░░██░░░░
# ▀█████░██░░██░▀█████░██░░██░░░░██░░░░▀█████
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░


def createdb(args):
    """Create the SQLite database
    Will do nothing and warn if it already exists
    """
    if os.path.exists(SQLITE_FILENAME):
        if args.force is False:
            print(
                f"Cannot create db: {SQLITE_FILENAME} already exists. Use --force to force."
            )
        else:
            os.remove(SQLITE_FILENAME)

    # os.system(f"sqlite3 {SQLITE_FILENAME} < table_schema.sql")

    _, cur = db_connect()
    cur.execute(
        """
        CREATE TABLE scores (
            timestamp TEXT,
            name TEXT,
            max_height REAL,
            time_total_s REAL,
            time_building_s REAL,
            time_scaling_s REAL,
            blocks_placed INTEGER,
            jumps INTEGER,
            distance_fallen REAL,
            spurious INTEGER
        );
    """
    )


DUMMY_DATA = [
    "2024-08-17 16:02:23.144;alifeee;124.22;120;102.40;17.60;63;78;29.4;0",
    "2024-08-17 16:06:11.007;jman;112.45;120;90.00;30.00;47;65;18.5;0",
    "2024-08-17 16:52:56.614;somebody909;96.54;120;86.55;33.45;39;49;14.6;0",
]


def create(args):
    """load create data (separated by ";")"""
    if args.example_data is not None and args.data is not None:
        raise ValueError("Cannot set data and placeholder at the same time")
    if args.example_data is None:
        data = [args.data]
    else:
        data = [DUMMY_DATA[i % len(DUMMY_DATA)] for i in args.example_data]

    data = [d.split(";") for d in data]

    con, cur = db_connect()
    for datum in data:
        cur.execute(
            """
        INSERT INTO scores VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            datum,
        )
        con.commit()
        id_ = cur.lastrowid
        print(f"added new row with id {id_}")


# █████▄░▄█████░▄████▄░██████▄
# ██░░██░██░░░░░██░░██░██░░░██
# █████▀░█████░░██░░██░██░░░██
# ██░░██░██░░░░░██████░██░░░██
# ██░░██░▀█████░██░░██░██████▀
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░


def dump(_):
    """Dump all scores"""
    _, cur = db_connect()
    res = cur.execute("SELECT rowid, * FROM scores")
    allres = res.fetchall()
    for r in allres:
        print(r)


def search(args):
    """Search for strings in all columns"""
    gc = "%" + args.generic_query + "%"
    _, cur = db_connect()
    res_obj = cur.execute(
        """
        SELECT rowid, * FROM scores
        WHERE
            timestamp like ?
                or
            name like ?
                or
            max_height like ?
                or
            time_total_s like ?
                or
            time_building_s like ?
                or
            time_scaling_s like ?
                or
            blocks_placed like ?
                or
            jumps like ?
                or
            distance_fallen like ?
    """,
        [
            gc,
            gc,
            gc,
            gc,
            gc,
            gc,
            gc,
            gc,
            gc,
        ],
    )
    res = res_obj.fetchall()
    if len(res) == 0:
        print("no results")
    for r in res:
        print(r)


def filter_(args):
    """Return results with specified max/min heights etc"""
    _, cur = db_connect()
    min_height, max_height = args.min_height, args.max_height
    before_date = dateutil.parser.parse(args.before)
    after_date = dateutil.parser.parse(args.after)
    spurious = args.spurious  # -1, 0, or 1
    if spurious == -1:
        sp1, sp2 = 0, 1
    elif spurious == 0:
        sp1, sp2 = 0, 0
    elif spurious == 1:
        sp1, sp2 = 1, 1
    else:
        raise ValueError(
            f"{spurious} is not a valid value for spurious. -1, 0, or 1 only"
        )
    res_obj = cur.execute(
        """
        SELECT rowid, * FROM scores
        WHERE
            max_height >= ? and max_height <= ?
              and
            timestamp < ? and timestamp > ?
              and
            spurious = ? or spurious = ?
        """,
        [
            min_height,
            max_height,
            before_date,
            after_date,
            sp1,
            sp2,
        ],
    )
    res = res_obj.fetchall()
    if len(res) == 0:
        print("no results")
    for r in res:
        print(r)


# ██░░░██░█████▄░██████▄░▄████▄░████████░▄█████
# ██░░░██░██░░██░██░░░██░██░░██░░░░██░░░░██░░░░
# ██░░░██░█████▀░██░░░██░██░░██░░░░██░░░░█████░
# ██░░░██░██░░░░░██░░░██░██████░░░░██░░░░██░░░░
# ▀█████▀░██░░░░░██████▀░██░░██░░░░██░░░░▀█████
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░


def spurious(args):
    """mark a row as spurious"""
    id_ = args.id
    con, cur = db_connect()
    # check existence
    res_obj = cur.execute("SELECT spurious FROM scores where rowid = ?", [id_])
    res = res_obj.fetchone()
    if res is None:
        print(f"Could not find row with id {id_} to update :(")
        return
    # current spuriosity
    current_spuriosity = res[0]
    if current_spuriosity == 0:
        new_spuriosity = 1
    else:
        new_spuriosity = 0
    # update
    cur.execute(
        "UPDATE scores SET spurious = ? WHERE rowid = ?",
        [
            new_spuriosity,
            id_,
        ],
    )
    con.commit()
    res_obj = cur.execute("SELECT rowid, * FROM scores where rowid = ?", [id_])
    res = res_obj.fetchone()
    print(f"changed spuriousity to {new_spuriosity}: {res}")


# ██████▄░▄█████░██░░░░░▄█████░████████░▄█████
# ██░░░██░██░░░░░██░░░░░██░░░░░░░░██░░░░██░░░░
# ██░░░██░█████░░██░░░░░█████░░░░░██░░░░█████░
# ██░░░██░██░░░░░██░░░░░██░░░░░░░░██░░░░██░░░░
# ██████▀░▀█████░██████░▀█████░░░░██░░░░▀█████
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░


def delete(args):
    """delete row with ID"""
    if args.all is True and args.id is not None:
        raise ValueError("Cannot delete ALL and ID at the same time")
    if args.all is True and args.force is not True:
        print("Must use --force to delete all")

    con, cur = db_connect()

    # delete all
    if args.all is True:
        # how many are we deleting
        res_obj = cur.execute("SELECT COUNT(*) FROM scores")
        res = res_obj.fetchone()
        # deletee
        cur.execute("DELETE FROM scores")
        con.commit()
        print(f"deleted ALL scores ({res} removed)")
        return

    # delete specific id
    id_ = args.id
    # check existence
    res_obj = cur.execute("SELECT rowid, * FROM scores where rowid = ?", [id_])
    res = res_obj.fetchone()
    if res is None:
        print(f"Could not find row with id {id_} to delete :(")
        return
    # delete
    cur.execute("DELETE FROM scores WHERE rowid = ?", [id_])
    con.commit()
    print(f"deleted {res}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    # command one
    parser_command_one = subparsers.add_parser("command_one")
    parser_command_one.add_argument("-x", type=int, default=1)
    parser_command_one.set_defaults(func=command_one)

    # command two
    parser_command_two = subparsers.add_parser("command_two")
    parser_command_two.add_argument("-x", type=int, default=1)
    parser_command_two.set_defaults(func=command_two)

    # createdb
    parser_createdb = subparsers.add_parser("createdb")
    parser_createdb.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
    )
    parser_createdb.set_defaults(func=createdb)

    # dump
    parser_dump = subparsers.add_parser("dump")
    parser_dump.set_defaults(func=dump)

    # create
    parser_create = subparsers.add_parser("create")
    parser_create.add_argument("-d", "--data", type=str)
    parser_create.add_argument("-e", "--example-data", type=int, nargs="+")
    parser_create.set_defaults(func=create)

    # delete
    parser_delete = subparsers.add_parser("delete")
    parser_delete.add_argument("-id", "--id", type=int)
    parser_delete.add_argument("-a", "--all", action="store_true", default=False)
    parser_delete.add_argument("--force", action="store_true", default=False)
    parser_delete.set_defaults(func=delete)

    # search
    parser_search = subparsers.add_parser("search")
    parser_search.add_argument("-q", "--generic-query", type=str)
    parser_search.set_defaults(func=search)

    # filter
    parser_filter = subparsers.add_parser("filter")
    parser_filter.add_argument("--min-height", type=int, default=0)
    parser_filter.add_argument("--max-height", type=int, default=999999)
    parser_filter.add_argument("--after", type=str, default="1970-01-01")
    parser_filter.add_argument("--before", type=str, default="2500-01-01")
    parser_filter.add_argument("-s", "--spurious", type=int, default=-1)
    parser_filter.set_defaults(func=filter_)

    # spurious
    parser_spurious = subparsers.add_parser("spurious")
    parser_spurious.add_argument("-id", "--id", type=int, required=True)
    parser_spurious.add_argument("-s", "--spurious", action="store_false", default=True)
    parser_spurious.set_defaults(func=spurious)

    arguments = parser.parse_args()
    arguments.func(arguments)
