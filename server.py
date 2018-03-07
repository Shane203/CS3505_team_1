#Team 1
"""A simple server program that acts as half a chat program with a client.

The server listens for any connections to any clients. The server then waits for the client to send
a message to the server. The server keeps a record of all connected clients and broadcasts any message from a client to all clients.
"""      
from socket import *
from socket import error as sockerr
from time import sleep
import _thread, sys
import json
from random import randint
import itertools

#Objective: Send colour + 


class Game:
    """
    A class that keeps a list of current client connections. This allows the
    threads, which are created by each connection, to broadcast a message to all
    connections.

    :param code:
    :type code:

    :var self._clients: list of client sockets
    :type self._clients:
    :var self.colours:
    :type self.colours:
    :var self._max_players:
    :type self._max_players:
    :var self._inGame:
    :type self._inGame:
    :var self.token:
    :type self.token:
    :var self._names:
    :type self._names:
    :var self.room_code:
    :type self.room_code:
    :var self.id:
    :type self.id:

    """
    id_generator = itertools.count (1)
    def __init__(self, code=""):
        self._clients= []
        self.colours=["red","green","yellow","blue"]
        self._max_players = 4
        self._inGame = [False] * self._max_players
        self.token = 0 #the index of which player's turn it is.
        self._names = ["None"]*self._max_players
        self.room_code = code
        self.id = next (self.id_generator)
        self.player_num_enter_lobby = 0
        self.player_num_press_start = 0

    def is_public_game(self):
        if self.room_code == "":
            return True
        else:
            return  False

    def clients(self): #returns list of client connections
        return self._clients
    def max_players(self):
        return self._max_players
    def inGame(self):
        return self._inGame
    def names(self):
        name_array = []
        for i in range (self.num_of_players ()):
            if self._inGame[i]:
                name_array.append (self._names[i])
        return name_array
    def add(self,connection): #adds "connection" to the list of connections self.clients
        if len(self.clients()) <self.max_players():
            self._clients += [connection]
            self.inGame()[len(self._clients)-1] = True
            print(self.inGame())
            return (self.colours[len(self._clients) - 1],len(self._clients) -1)
    def remove(self,index):
        self._inGame[index] = False
    def num_of_players(self):
        return len (self._clients)
                
    def is_full(self):
        return self.num_of_players() == self.max_players()

    def forward(self,jsonmsg):
        string = json.dumps(jsonmsg)
        for i in range(self.max_players()):
            if self.inGame()[i] != False: #Condition accepts True and None(won) players.
                self._clients[i].sendall(string.encode())
    def sendto(self,jsonmsg,index):
        string = json.dumps(jsonmsg)
        print(string)
        self.clients()[index].sendall(string.encode())
    def StartGame(self):
        """A function that starts the game. It assigns a colour to each client by order in which they connected, and gives the turn token to the red player"""
        start = [{"Colour":"red","start":True, "names":self.names()},
             {"Colour":"green","start":True, "names":self.names()},
             {"Colour":"yellow","start":True, "names":self.names()},
             {"Colour":"blue","start":True, "names":self.names()}]
        for i in range(self.num_of_players()):
            self.sendto(start[i],i)
            print("sent start to ",i)
        sleep(1)
        token ={"Colour":self.colours[0],"turnToken":True}
        self.forward(token)
    def roll_genie(self):
        """Roll a "dice"(not a real dice, just a 1 in 6 chance of each result) to get or give back the genie."""
        result = randint(1, 6)
        genie_status = None
        if result == 1:
            genie_status = "take"
            print("GENIE TAKE")
        elif result == 2:
            genie_status = "return"
            print("GENIE RETURN")
        return genie_status

        
    def rolldice(self):
        """Returns a random number between 1 and 6"""
        return randint(1,6)

    def roll_biased_dice(self):
        """Return a random number between 1 and 8.
        On the client side anything over a 5 is considered a 6"""
        return randint(1,8)

    def nextPlayer(self):
        self.token += 1
        if self.token >= self.max_players():
            self.token = 0
        while not self.inGame()[self.token]:
            self.token +=1
            if self.token >= self.max_players():
                self.token = 0
    def ConnectionHandler(self,connection,client_address,name):
        try:
            print('connection from', client_address)

            colour, index = self.add(connection)
            self._names[self.num_of_players()-1]= name
            print("is full?")
            print(self.is_full())
            while self.is_full() != True: #If there are 4 players connected, start a game
                continue
            self.StartGame()
            while True:
                jsonmsg = None
                data = connection.recv(4096).decode() #Get data from client
                print(data)
                data = data.split("}")
                for msg in data:
                    if len(msg) >1:
                        msg += "}"
                        msg = json.loads(msg)
                        if "roll" in msg: #If request for roll is sent, call rolldice() function and broadcast the dice roll.
                            if not msg["bias"]:
                                num = self.rolldice()
                            else:
                                num = self.roll_biased_dice()
                            genie_status = self.roll_genie()
                            jsonmsg = {"Colour":msg["Colour"],"dicenum":num, "genie_result":genie_status}
                        elif "turnOver" in msg and index == self.token: 
                            self.nextPlayer()
                            jsonmsg = {"Colour":self.colours[self.token],"turnToken":True}
                            print("iT is now the turn of   ",self.colours[self.token])
                        elif "Movement" in msg: #If the JSON message is Sendout or Movement, simply forward it unchanged to all other clients.
                            jsonmsg = msg
                        elif "msg" in msg:
                            jsonmsg = msg
                        elif "Player_Won" in msg:
                            print("Player ", msg["Player_Won"], "Won")
                            self.inGame()[index] = None
                            self.nextPlayer()
                            jsonmsg = {"Colour": self.colours[self.token], "turnToken": True}
                        if jsonmsg:
                            self.forward(jsonmsg)

                
        except sockerr:
            print(colour," left the game")
            bye = {"disconnected": True, "Colour":colour}
            self.inGame()[index] = False
            self.forward(bye)
            sleep(.25)
            if index == self.token:
                self.nextPlayer()
                data = {"Colour":self.colours[self.token],"turnToken":True}
                print(data)
                self.forward(data)
                print("Player left, so we moved the token on!")
    

class Games:
    def __init__(self):
        self.all_games = []
        self.lobby_room_player_number = dict()
        self.lobby_room_connection_array = []

    def create_new_game(self,code=""):
        game = Game(code)
        self.all_games.append(game)
        self.lobby_room_player_number[game.id] = 0
        return game
    def check_if_game_started(self,room_id):
        for game in self.all_games:
            if game.id == room_id:
                return game.is_full()
    def get_game_by_id(self,ID):
        for game in self.all_games:
            if game.id == ID:
                return game

    def get_public_games_ids(self):
        id_array = []
        for game in self.all_games:
            if game.is_public_game() and not game.is_full():
                id_array.append(game.id)
        return id_array

    def find_num_of_players_by_id(self, game_id):
        for game in self.all_games:
            if game.id == game_id:
                return game.num_of_players()

    def lobby_send_to_all(self,game_id,num_of_player):
        for connection in self.lobby_room_connection_array[int(game_id)-1]:
            jsonmsg ={"player_number_in_lobby":int(num_of_player)}
            string = json.dumps (jsonmsg)
            connection.sendall(string.encode())



    def join_game_connection(self,connection,client_address):
        print("successfully start the thread")
        try:
            print('Join the Game', client_address)
            while True:
                data = connection.recv (4096)  # Get data from client
                msg = json.loads (data.decode ())  # decode and create dict from data
                print(msg)
                if "create_game" in msg:# it should followed with name
                        this_game = self.create_new_game(msg["create_game"])
                        jsonmsg = {"player_number": this_game.num_of_players(), "room_id": this_game.id, "room_code": this_game.room_code}
                        string = json.dumps (jsonmsg)
                        print (string)
                        connection.sendall(string.encode())
                        continue
                elif "show_game_list" in msg:
                    ID_array = []
                    num_array = []
                    Public_array = []
                    for game in self.all_games:
                        ID_array.append (game.id)
                        num_array.append (game.player_num_enter_lobby)
                        Public_array.append (game.is_public_game ())
                    data = {"ID": ID_array, "NUM": num_array, "IS_PUBLIC": Public_array}
                    print (data)
                    data = json.dumps (data)
                    connection.sendall (data.encode())
                elif "check_game" in msg:
                    data = {"ROOM_ID":msg["check_game"],"RESULT":self.check_if_game_started(msg["check_game"] or self.get_game_by_id (msg["check_game"]).player_num_enter_lobby == 4),"player_number":self.get_game_by_id (msg["check_game"]).player_num_enter_lobby}
                    data = json.dumps (data)
                    connection.sendall (data.encode ())
                elif "check_room_code" in msg:
                    print(msg)
                    exists = False
                    for game in self.all_games:
                        if game.room_code == msg["check_room_code"]:
                            print("t")
                            exists = True
                            data = {"exists": True, "room_code": game.room_code,
                                    "num_of_players": game.player_num_enter_lobby, "game_id": game.id}
                            data = json.dumps(data)
                            connection.sendall(data.encode())
                            break
                    if not exists:
                        if msg["check_type"] == "create":
                            new_game = self.create_new_game(msg["check_room_code"])
                            data = {"exists": False, "new_game_id": new_game.id}
                        else:
                            data = {"exists": False}
                        data = json.dumps(data)
                        connection.sendall(data.encode())
                    continue
                elif "GET_IN_LOBBY" in msg:
                    self.get_game_by_id(msg["ROOM_ID"]).player_num_enter_lobby += 1
                    self.lobby_room_player_number[int(msg["ROOM_ID"])] += 1
                    self.lobby_room_connection_array[int(msg["ROOM_ID"])-1].append(connection)
                    self.lobby_send_to_all(msg["ROOM_ID"],self.lobby_room_player_number[int(msg["ROOM_ID"])])
                elif "LEAVE_THE_LOBBY" in msg:
                    self.get_game_by_id(msg["ROOM_ID"]).player_num_enter_lobby -= 1
                    self.lobby_room_player_number[int (msg["ROOM_ID"])] -= 1
                    self.lobby_room_connection_array[int (msg["ROOM_ID"]) - 1].remove(connection)
                    self.lobby_send_to_all (msg["ROOM_ID"], self.lobby_room_player_number[int (msg["ROOM_ID"])])
                    if self.get_game_by_id (msg["ROOM_ID"]).player_num_press_start == self.get_game_by_id (
                            msg["ROOM_ID"]).player_num_enter_lobby:
                        self.get_game_by_id (msg["ROOM_ID"])._max_players = self.get_game_by_id (
                            msg["ROOM_ID"]).player_num_press_start

                elif "START_THE_GAME" in msg:
                    self.get_game_by_id (msg["ROOM_ID"]).player_num_press_start += 1
                    try:
                        if self.get_game_by_id (msg["ROOM_ID"]).player_num_press_start == self.get_game_by_id(msg["ROOM_ID"]).player_num_enter_lobby:
                            self.get_game_by_id (msg["ROOM_ID"])._max_players = self.get_game_by_id (msg["ROOM_ID"]).player_num_press_start

                        _thread.start_new_thread (self.get_game_by_id(msg["ROOM_ID"]).ConnectionHandler,
                                                  (connection,
                                                   client_address,msg["NAME"]))  # Starts a new thread for each connection.
                    except InterruptedError:
                        print ("Error! The signal has been interrupted.")
                        connection.close ()
                    while True:# i am not sure if i can break here?
                        pass
        except sockerr:
            pass



if __name__ == "__main__":  # If this file is being executed as the top layer, start the server.
    games = Games()  # Creates instance of class
    try:
        sock = socket (AF_INET, SOCK_STREAM)  # Creates TCP server socket.
        server_address = (getfqdn (), 10001)  # Sets values for host- the current domain name and port number 10000.
        ipaddr = gethostbyname (gethostname ())  # IP Address of the current machine.
        print ('*** Server starting on %s port %s ***' % server_address)
        print ('IP address is %s' % ipaddr)
        sock.bind (server_address)  # Bind Socket to the host and port
        sock.listen (10)  # Listens for incoming connections.

        while True:  # Server always running.
            print ('*** Waiting for a connection ***')
            connection, client_address = sock.accept ()  # Accepts connection between client and server.
            try:
                _thread.start_new_thread (games.join_game_connection,
                                          (connection, client_address))  # Starts a new thread for each connection.
            except InterruptedError:
                print ("Error! The signal has been interrupted.")
                connection.close ()
    except  OSError:
        print ("OS Error: Port number already in use or another server process may be running")
        sys.exit ()
    except OSError:
        print ("Error! An error has occured. Please try again later.")
        sys.exit ()
    sock.close ();
