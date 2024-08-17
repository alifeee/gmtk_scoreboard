# A scoreboard server for Summon2Scale

Using:

- [Flask](https://flask.palletsprojects.com/en/3.0.x/)
- [SQLite](https://www.sqlite.org/index.html)
- [sqlite3 for Python](https://docs.python.org/3/library/sqlite3.html)

## Development

### Install

```bash
git clone ...
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
# create new SQLITE DB
python tools.py createdb --force
py .\tools.py create --example-data 0 1 2
```

### Development Server

```bash
flask --app server run
```

### Production
