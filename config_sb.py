# coding: utf-8
#SaltyBot Config

import os

#Define URL
MAIN_URL = "http://www.saltybet.com"
LOGIN_URL = "http://www.saltybet.com/authenticate?signin=1"
LOGOUT_URL = "http://www.saltybet.com/logout"
BET_URL = "http://www.saltybet.com/ajax_place_bet.php"
STATE_URL = "http://www.saltybet.com/state.json"

#Define URL headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'
}

#Define WebSocket
WS_URL = "www-cdn-twitch.saltybet.com"
WS_PORT = 1337 # :)

#Define SQLite DB path
SQLITE_PATH = os.path.join("/data", "pysbbot", "db", "pysbbot.sqlite")

#Define User
USER = "XXXX"
EMAIL = "XXXX"
PASSWORD = "XXXX"