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

Add this to nginx config:

```nginx
        server {
                server_name summon2scale.alifeee.co.uk;
                location / {
                        proxy_pass http://localhost:9043;
                        proxy_redirect off;
                        proxy_set_header Host $http_host;
                        proxy_set_header X-Real-IP $remote_addr;
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_read_timeout 900;
                }
        }
```

```bash
# set up folder
sudo mkdir -p /usr/alifeee
sudo chown alifeee:alifeee /usr/alifeee
git clone git@github.com:alifeee/gmtk_scoreboard.git
mv gmtk_scoreboard summon2scale
sudo adduser --system --no-create-home --group summon2scale
cd summon2scale
sudo chown -R alifeee:summon2scale .
# set up python
python3 -m venv env
./env/bin/pip install -r requirements.txt
# set up systemds
sudo cp summon2scale_scoreboard.service /etc/systemd/system/summon2scale_scoreboard.service
sudo systemctl enable summon2scale_scoreboard.service
sudo systemctl start summon2scale_scoreboard.service
sudo systemctl status summon2scale_scoreboard.service
```
