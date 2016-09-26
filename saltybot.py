
# coding: utf-8

# In[1]:

import json
import requests
import bs4 as BeautifulSoup
from socketIO_client import SocketIO
import sqlite3
import datetime


# In[2]:

#Define URL
MAIN_URL = "http://www.saltybet.com"
LOGIN_URL = "http://www.saltybet.com/authenticate?signin=1"
LOGOUT_URL = "http://www.saltybet.com/logout"
BET_URL = "http://www.saltybet.com/ajax_place_bet.php"
STATE_URL = "http://www.saltybet.com/state.json"


# In[3]:

#Define URL headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'
}


# In[4]:

#Define WebSocket
WS_URL = "www-cdn-twitch.saltybet.com"
WS_PORT = 1337 # :)


# In[5]:

#Define SQLite DB path
SQLITE_PATH = "db/pysbbot.sqlite"


# In[6]:

#Special Function


# In[7]:

def connect(session, email, password, user):
    """
    Login to saltybet
    Return True if ok
    """
    payload = {
        "email" : email,
        "pword" : password,
        "authenticate" : "signin"
    }
    response = session.post(LOGIN_URL, data=payload)
    return user in response.text


# In[8]:

def place_bet(session, player, wager):
    """
    Place wager (str not rounded) for player
    Return True if ok
    """
    payload = {
        "radio":"on",
        "selectedplayer":player,
        "wager": wager
    }
    response = session.post(BET_URL, data=payload)
    return "1" in response.text


# In[9]:

def get_balance(session, user):
    """
    Get amount of wager
    Return float
    """
    response = session.get(MAIN_URL)
    soup = BeautifulSoup.BeautifulSoup(response.text, "lxml")
    res_html = soup.find("span", {"id": "balance"})
    return float(res_html.replace(",", "."))


# In[10]:

def allready_connected(session, user):
    """
    Check if user is allready connected
    Return True if of
    """
    response = session.get(MAIN_URL)
    return user in response.text


# In[11]:

def get_state(session):
    """
    Get the state
    Return JSON
    """
    response = session.get(STATE_URL)
    return response.json()


# In[22]:

def insert_event_to_db(p1name, p2name, pwon):
    """
    Insert into db data ...
    """
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    data = {
        "event_date" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        "p1_name" : p1name,
        "p2_name" : p2name,
        "p1_win" : 1 if pwon == 1 else 0,
        "p2_win" : 1 if pwon == 2 else 0,
    }
    cursor.execute("""INSERT INTO events(event_date, p1_name, p2_name, p1_win, p2_win) VALUES(:event_date, :p1_name, :p2_name, :p1_win, :p2_win)""", data)
    conn.commit()
    conn.close()


# In[13]:

def on_ws_msg(*args):
    """
    Do something each time you receive msg from websocket
    """ 
    global lastStatus
    global p1
    global p2
    
    current_state = get_state(session)
    status = current_state['status']
    
    changed = lastStatus != status
    
    p1 = current_state['p1name']
    p2 = current_state['p2name']
    
    if p1 == "" or p2 == "":
        pass
    
    if changed:
        if status == 'open':
            print("New game start")
        elif status == 'locked':
            print("Game is lock")
        elif status == '1':
            print("Player1 won the match (P1 : %s vs P2 : %s)" %(p1, p2))
            insert_event_to_db(p1, p2, pwon=1)
        elif status == '2':
            print("Player2 won the match (P1 : %s vs P2 : %s)" %(p1, p2))
            insert_event_to_db(p1, p2, pwon=2)
    lastStatus = status


# In[14]:

#Create Request session
session = requests.session()
session.headers.update(headers)


# In[23]:

#Connect to websocket
socket = SocketIO(WS_URL, WS_PORT)

#Attach function to message
socket.on('message', on_ws_msg)
lastStatus = ""
p1 = ""
p2 = ""

#Loop !
while True:
  socket.wait(seconds=1)
