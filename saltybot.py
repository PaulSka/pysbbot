# coding: utf-8
#SaltyBot

#Import module
import json
import requests
import bs4 as BeautifulSoup
from socketIO_client import SocketIO
import sqlite3
import datetime
import config_sb
import random
import sys


#Special Function
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
    response = session.post(config_sb.LOGIN_URL, data=payload)
    return user in response.text

def place_bet(session, player, wager):
    """
    Place wager (str not rounded) for player (1 or 2)
    Return True if ok
    """
    payload = {
        "radio":"on",
        "selectedplayer":player,
        "wager": wager
    }
    response = session.post(config_sb.BET_URL, data=payload)
    return "1" in response.text

def get_balance(session, user):
    """
    Get amount of wager
    Return float
    """
    response = session.get(config_sb.MAIN_URL)
    soup = BeautifulSoup.BeautifulSoup(response.text, "html.parser")
    res_html = soup.find("span", {"id": "balance"})
    return int(res_html.text.replace(",", ""))

def allready_connected(session, user):
    """
    Check if user is allready connected
    Return True if of
    """
    response = session.get(config_sb.MAIN_URL)
    return user in response.text

def get_state(session):
    """
    Get the state
    Return JSON
    """
    response = session.get(config_sb.STATE_URL)
    return response.json()

def insert_event_to_db(p1name, p2name, pwon):
    """
    Insert into db data ...
    """
    conn = sqlite3.connect(config_sb.SQLITE_PATH)
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
    
def insert_bet_to_db(cash):
    """
    Insert into db data ...
    """
    conn = sqlite3.connect(config_sb.SQLITE_PATH)
    cursor = conn.cursor()
    data = {
        "date" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        "cash" : cash,
    }
    cursor.execute("""INSERT INTO history(date, cash) VALUES(:date, :cash)""", data)
    conn.commit()
    conn.close()
    
def getPlayerWin(player):
    """
    Get all win for player
    getPlayerWin("AA")
    """
    conn = sqlite3.connect(config_sb.SQLITE_PATH)
    cursor = conn.cursor()
    p1_win = cursor.execute("""
        SELECT
        SUM(p1_win)
        FROM events
        WHERE p1_name = :player""", {"player" : player}).fetchone()[0]
    p1_win = 0 if p1_win == None else p1_win
    p2_win = cursor.execute("""
        SELECT
        SUM(p2_win)
        FROM events
        WHERE p2_name = :player""", {"player" : player}).fetchone()[0]
    p2_win = 0 if p2_win == None else p2_win
    conn.close()
    return(p1_win + p2_win)
    
def getPlayerWinVS(p1, p2):
    """
    Get all win for p1 vs p2
    print(getPlayerWinVS("Spera", "Kull"))
    """
    conn = sqlite3.connect(config_sb.SQLITE_PATH)
    cursor = conn.cursor()
    p1_win_1, p2_win_1 = cursor.execute("""
        SELECT 
        SUM(p1_win), 
        SUM(p2_win)
        FROM events 
        WHERE p1_name = :p1_name and p2_name = :p2_name""", {'p1_name' : p1, 'p2_name' : p2}).fetchall()[0]
    p1_win_1 = 0 if p1_win_1 == None else p1_win_1
    p2_win_1 = 0 if p2_win_1 == None else p2_win_1
    p2_win_2, p1_win_2 = cursor.execute("""
        SELECT 
        SUM(p1_win), 
        SUM(p2_win)
        FROM events 
        WHERE p1_name = :p1_name and p2_name = :p2_name""", {'p1_name' : p2, 'p2_name' : p1}).fetchall()[0]
    p1_win_2 = 0 if p1_win_2 == None else p1_win_2
    p2_win_2 = 0 if p2_win_2 == None else p2_win_2
    conn.close()
    return({"p1" : p1_win_1 + p1_win_2, "p2" : p2_win_1 + p2_win_2})
    
def getStatPlayer(p1, p2):
    """
    Get some stat for each player
    Return potential winner
    """
    potential_winner = None
    res_vs = getPlayerWinVS(p1,p2)
    if res_vs["p1"] > res_vs["p2"]:
        potential_winner = "player1"
    elif res_vs["p1"] < res_vs["p2"]:
        potential_winner = "player2"
    elif res_vs["p1"] == res_vs["p2"]:
        #check for each player stat
        p1_win = getPlayerWin(p1)
        p2_win = getPlayerWin(p2)
        if p1_win > p2_win:
            potential_winner = "player1"
        elif p1_win < p2_win:
            potential_winner = "player2"
        elif p1_win == p2_win:
            #Invok god of RNG
            potential_winner = random.choice(["player1", "player2"])
        else:
            return potential_winner
    else:
        return potential_winner
    return potential_winner
    
def bet(session, p1, p2):
    """
    Bet !
    """
    #Get stat db for each player
    #get potential winner
    potential_winner = getStatPlayer(p1, p2)
    #get gold balance
    gold_balance = get_balance(session, config_sb.USER)
    #Bet
    if allready_connected(session, config_sb.USER):
        print("I place %s for player %s" %(gold_balance, potential_winner))
        if place_bet(session, potential_winner, gold_balance):
            print("Bet accepted !")
        else:
            print("Bet refused !")
    else:
        print("Cannot logged, abort !")

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
            bet(session, p1, p2)
        elif status == 'locked':
            print("Game is lock")
        elif status == '1':
            print("Player1 won the match (P1 : %s vs P2 : %s)" %(p1, p2))
            insert_event_to_db(p1, p2, pwon=1)
        elif status == '2':
            print("Player2 won the match (P1 : %s vs P2 : %s)" %(p1, p2))
            insert_event_to_db(p1, p2, pwon=2)
    lastStatus = status

def main_lopp():
print("Saltybot is running ...")
#Create Request session
session = requests.session()
session.headers.update(config_sb.headers)


#Connect to SB
if connect(session, config_sb.EMAIL, config_sb.PASSWORD, config_sb.USER):
    print("Login OK !")
else:
    sys.exit("Unable to login ! Check your conf !")

#Connect to websocket
socket = SocketIO(config_sb.WS_URL, config_sb.WS_PORT)

#Attach function to message
socket.on('message', on_ws_msg)
lastStatus = ""
p1 = ""
p2 = ""

#Loop !
while True:
  socket.wait(seconds=1)
