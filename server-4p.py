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

#Objective: Send colour + 

class Game: #A simple class that keeps a list of current client connections. This allows the threads, which are created by each connection, to broadcast a message to all connections.
    def __init__(self):
        self._clients= []
        self.colours=["red","green","yellow","blue"]
        self._maxPlayers = 4
        self._inGame = [False] * self._maxPlayers
        self.token = 0 #the index of which player's turn it is.
        self._names = []
    def clients(self): #returns list of client connections
        return self._clients
    def maxPlayers(self):
        return self._maxPlayers
    def inGame(self):
        return self._inGame
    def names(self):
        return self._names
    def add(self,connection): #adds "connection" to the list of connections self.clients
        if len(self.clients()) <self.maxPlayers():
            self._clients += [connection]
            self.inGame()[len(self._clients)-1] = True
            print(self.inGame())
            return (self.colours[len(self._clients) - 1],len(self._clients) -1)
    def remove(self,index):
        self._inGame[index] = False
    def numOfPlayers(self):
        return len(self._clients)
                
    def isfull(self):
        print(self.numOfPlayers())
        print(self.maxPlayers())
        return self.numOfPlayers() == self.maxPlayers()
    def forward(self,jsonmsg):
        string = json.dumps(jsonmsg)
        for i in range(self.maxPlayers()):
            if self.inGame()[i]:
                self._clients[i].sendall(string.encode())
                print("goodbye!")
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
        for i in range(self.numOfPlayers()):
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
        return randint(4,6)
        #return 6
    def nextPlayer(self):
        self.token += 1
        if self.token >= self.maxPlayers():
            self.token = 0
        while not self.inGame()[self.token]:
            self.token +=1
            if self.token >= self.maxPlayers():
                self.token = 0
    def ConnectionHandler(self,connection,client_address):
        try:
            print('connection from', client_address)

            colour, index = self.add(connection)
            while True:
                data = connection.recv(4096).decode()
                msg = json.loads(data)
                if "name" in msg:
                    name = msg["name"]
                    self._names += [name]
                    break
            print("is full?")
            print(self.isfull())
            if self.isfull(): #If there are 4 players connected, start a game
                self.StartGame()
            while True:
                data = connection.recv(4096) #Get data from client
                print(data.decode())
                msg = json.loads(data.decode()) #decode and create dict from data
                if "roll" in msg: #If request for roll is sent, call rolldice() function and broadcast the dice roll.
                    num = self.rolldice()
                    genie_status = self.roll_genie()
                    jsonmsg = {"Colour":msg["Colour"],"dicenum":num, "genie_result":genie_status}
                elif "turnOver" in msg: 
                    self.nextPlayer()
                    jsonmsg = {"Colour":self.colours[self.token],"turnToken":True}
                    print("iT is now the turn of   ",self.colours[self.token])
                elif "Movement" in msg: #If the JSON message is Sendout or Movement, simply forward it unchanged to all other clients.
                    jsonmsg = msg
                elif "Player_Won" in msg:
                    print("Player ", msg["Player_Won"], "Won")
                    self.nextplayer()
                    jsonmsg = {"Colour": cons.colours[cons.token], "turnToken": True}
                
                self.forward(jsonmsg)

                
        except sockerr:
            print(colour," left the game")
            bye = {"byebye": True, "Colour":colour}
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
        self._allgames = set()
        self._newestgame = None
    def newGame(self):
        game = Game()
        self._allgames.add(game)
        self._newestgame = game
        return game
    def allgames(self):
        return self._allgames
    def newestgamefull(self):
        return self._newestgame.isfull()
    def newestgame(self):
        return self._newestgame
    def isEmpty(self):
        return len(self._allgames) == 0
    def clean(self,game):
        self.allgames.remove(game)
        if self._newestgame == game:
            self._newestgame = None
            
    
    

if __name__ == "__main__":#If this file is being executed as the top layer, start the server.
    games = Games() #Creates instance of class
    try:
        sock = socket(AF_INET, SOCK_STREAM) #Creates TCP server socket.
        server_address = (getfqdn(), 10001)#Sets values for host- the current domain name and port number 10000.
        ipaddr = gethostbyname(gethostname()) # IP Address of the current machine.
        print('*** Server starting on %s port %s ***' % server_address)
        print('IP address is %s' % ipaddr)
        sock.bind(server_address) # Bind Socket to the host and port
        sock.listen(5) # Listens for incoming connections.

        while True: #Server always running.
            print('*** Waiting for a connection ***')
            connection, client_address = sock.accept() # Accepts connection between client and server.
            if games.isEmpty() or games.newestgamefull():
                game = games.newGame()
            else:
                game = games.newestgame()
            try:
                _thread.start_new_thread ( game.ConnectionHandler, (connection, client_address) ) #Starts a new thread for each connection.
            except InterruptedError:
                print("Error! The signal has been interrupted.")
                connection.close()
                    
                
    except  OSError:
        print("OS Error: Port number already in use or another server process may be running")
        sys.exit()
    except:
            print("Error! An error has occured. Please try again later.")
            sys.exit()
    sock.close();



