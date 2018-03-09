# Team 1
"""A Server that runs a lobby for Ludo Games

The server listens for any connections to any clients. It allows players to have multiple games running
instantaneously.
"""
from socket import socket, SOCK_STREAM, AF_INET, gethostbyname, gethostname
from socket import error as sockerr
from time import sleep
from random import randint
import sys
import json
import itertools
import _thread


class Game:
    """
    A class that keeps a list of current client connections. This allows the
    threads, which are created by each connection, to broadcast a message to all
    connections.

    :param code: The room-code as chosen by the creator,"" by default.
    :type code: string.

    :var self._clients: list of client connections.
    :type self._clients: list of TCP Socket Connections.
    :var self.colours: list of possible player colours.
    :type self.colours: list of strings.
    :var self._max_players: The number of players needed to start a game.
    :type self._max_players: int.
    :var self._in_game: List representing number of active players.
    :type self._in_game: List of strings
    :var self.token: Index to which client has the Turn Token.
    :type self.token: int.
    :var self._names: List of Player's names.
    :type self._names: List of strings.
    :var self.room_code: The room-code of the game, selected by the creator.
    :type self.room_code: string.
    :var self._game_id: An automatically incremented ID for the game
    :type self._game_id: int.

    """
    id_generator = itertools.count(1)

    def __init__(self, code=""):
        self._clients = []
        self.colours = ["red", "green", "yellow", "blue"]
        self._max_players = 4
        self._in_game = ["disconnected"] * self._max_players
        self.token = 0  # the index of which player's turn it is.
        self._names = ["None"]*self._max_players
        self._room_code = code
        self._game_id = next(self.id_generator)
        self.player_num_enter_lobby = 0
        self.player_num_press_start = 0

    def is_public_game(self):
        """Return True if instance is a public game."""
        return bool(self._room_code == "")

    def clients(self):
        """Return list of client connections."""
        return self._clients

    def max_players(self):
        """Return maximum number of players."""
        return self._max_players

    def game_id(self):
        """Return the Game's ID."""
        return self._game_id

    def room_code(self):
        """ Return the room code for the Game."""
        return self._room_code

    def in_game(self):
        """Return list representing current players."""
        return self._in_game

    def names(self):
        """Return list of names of the players."""
        name_array = []
        for i in range(self.num_of_players()):
            if self._in_game[i]:
                name_array.append(self._names[i])
        return name_array

    def add(self, connection):
        """Add new player/ connection to the game.

        :param connection: Connection Object
        :type connection: instance object
        """
        if len(self.clients()) < self.max_players():
            self._clients += [connection]
            self.in_game()[len(self._clients)-1] = "connected"
            return self.colours[len(self._clients) - 1], len(self._clients) - 1
        return None

    def remove(self, index):
        """Remove player from the game

        :param index: The index of the item representing the player in the ._in_game list.
        :type index: int.
        """
        self._in_game[index] = False

    def num_of_players(self):
        """Return number of players in the game."""
        return len(self._clients)

    def is_full(self):
        """Return True if the Game is full."""
        return self.player_num_press_start == self.max_players()

    def forward(self, jsonmsg):
        """Forward a JSON object to all clients.

        Converts a JSON-standard dictionary to a string and forwards it to each active connection.
        :param jsonmsg: the JSON object to be forwarded.
        :type jsonmsg: dict.
        """
        string = json.dumps(jsonmsg)
        print("Forwarding: ",string)
        for i in range(self.max_players()):
            # If player is connected or finished, forward to them.
            if self.in_game()[i] != "disconnected":
                self._clients[i].sendall(string.encode())

    def sendto(self, jsonmsg, index):
        """Send message to specific client.

        Converts a JSON-standard dictionary to a string and sends it to the client.
        :param jsonmsg: The JSON object to be forwarded.
        :type jsonmsg: dict.
        :param index: The index of the client in self._clients
        :type index: int.
        """
        string = json.dumps(jsonmsg)
        print("%s sent to %s" % (string,self.colours[index]))

        self.clients()[index].sendall(string.encode())

    def start_game(self):
        """Start the game by sending data to clients.

        Assign a colour to each client and give the turn token to the first player.
        """

        start = [{"colour": "red", "start": True, "names": self.names()},
                 {"colour": "green", "start": True, "names": self.names()},
                 {"colour": "yellow", "start": True, "names": self.names()},
                 {"colour": "blue", "start": True, "names": self.names()}]
        print("*Starting Game*")
        print(self.player_num_press_start)
        for i in range(self.player_num_press_start):
            self.sendto(start[i], i)
        token = {"colour": self.colours[0], "turn_token": True}
        self.forward(token)

    def roll_genie(self):
        """Roll the pseudo-dice to determine the genie feature

        :return: Status of the Genie.
        :type: string."""
        result = randint(1, 6)
        genie_status = None
        if result == 1:
            genie_status = "take"
        elif result == 2:
            genie_status = "return"
        return genie_status

    def rolldice(self):
        """Return a random number between 1 and 6.

        :return: returns Dice Roll (1-6)
        :type: int."""
        return randint(1, 6)

    def roll_biased_dice(self):
        """Return a random number between 1 and 8.

        A dice that is called when all client pieces are in their home space.
        Higher percentage of rolling >5 (considered a 6).

        :return: returns Dice Roll (1-8)
        :type: int.
        """
        return randint(1, 8)

    def next_player(self):

        self.token += 1
        if self.token >= self.max_players():
            self.token = 0
        while self.in_game()[self.token] != "connected":
            self.token += 1
            if self.token >= self.max_players():
                self.token = 0

    def connection_handler(self, connection, name):
        """Handle connection with a client.

        Listen for JSON Messages and respond appropriately to the message.
        This can include moving the Turn Token, forwarding the message, or
        rolling the Dice.

        :param connection: The connection to the Clien
        :type connection: TCP Socket Connection.
        :param name: The name of the Client
        :type name: string.
        """
        client_colour, index = self.add(connection)
        try:
            self._names[self.num_of_players()-1] = name
            sleep (1.5)
            if index ==0:
                self.start_game()
            while True:
                jsonmsg = None
                data = connection.recv(4096).decode()  # Get data from client
                print("Received: ",data)
                data = data.split("}")
                for msg in data:
                    if len(msg) > 1:
                        msg += "}"
                        msg = json.loads(msg)
                        # If request for roll is sent, call rolldice() function and broadcast the dice roll.
                        if "roll" in msg:
                            if not msg["bias"]:
                                num = self.rolldice()
                            else:
                                num = self.roll_biased_dice()
                            genie_status = self.roll_genie()
                            jsonmsg = {
                                "colour": msg["colour"], "dicenum": num, "genie_result": genie_status}
                        elif "turn_over" in msg and index == self.token:
                            self.next_player()
                            jsonmsg = {
                                "colour": self.colours[self.token], "turn_token": True}
                        # If the JSON message is for chat or movement, simply forward to all clients.
                        elif "movement" in msg:
                            jsonmsg = msg
                        elif "chat_msg" in msg:
                            jsonmsg = msg
                        elif "finished" in msg:
                            self.in_game()[index] = "finished"
                            self.next_player()
                            jsonmsg = {
                                "colour": self.colours[self.token], "turn_token": True}
                        if jsonmsg:
                            self.forward(jsonmsg)

        except sockerr:
            print(client_colour, " left the game.")
            bye = {"disconnected": True, "colour": client_colour}
            self.in_game()[index] = "disconnected"
            self.forward(bye)
            sleep(.25)
            if index == self.token:
                self.next_player()
                data = {"colour": self.colours[self.token], "turn_token": True}
                self.forward(data)
                print("Player left, so we moved the token on!")


class Lobby:
    """Class that acts as a lobby for a collection of games.

    The class allows clients to connect and join or create games.

    :var self.all_games: A list of all games in the lobby.
    :type all_games: list of Game objects."""
    def __init__(self, port_number):
        self.all_games = []
        self.sock = socket(AF_INET, SOCK_STREAM)
        server_addr = (gethostbyname(gethostname()), port_number)
        self.sock.bind(server_addr)  # Bind Socket to the host and port
        print('*** Server starting on IP ADDRESS: %s ***' % server_addr[0])

    def listen(self):
        """listens for incoming connections and passes them to a new thread."""
        self.sock.listen(10)
        print("***Waiting for connections***")
        while True:
            connection = self.sock.accept()[0]
            try:
                _thread.start_new_thread(self.join_game_connection, (connection,))
            except InterruptedError:
                print("Error! The signal has been interrupted.")
                connection.close()

    def create_new_game(self, code=""):
        """Create a Game instance.

        :param code: The room code of the game.
        :type code: string.
        :return: a new Game with the code 'code'.
        :type: Game object instance.
        """
        game = Game(code)
        self.all_games.append(game)
        return game

    def check_if_game_started(self, room_code):
        """Return True if game with ID "game_id" has started.

        :param room_code: The room id.
        :type room_code: string.
        """
        for game in self.all_games:
            if game.game_id() == room_code:
                return game.is_full()
        return None

    def get_game_by_id(self, game_id):
        """ Returns game with ID "game_id"

        :param game_id: The game ID
        :type game_id: string.
                """
        for game in self.all_games:
            if game.game_id() == game_id:
                return game
        return None

    def get_public_games_ids(self):
        """ Return list of public game ID's."""
        id_array = []
        for game in self.all_games:
            if game.is_public_game() and not game.is_full():
                id_array.append(game.game_id())
        return id_array

    def find_num_of_players_by_id(self, game_id):
        """Return number of players in a game.

        :param game_id: The Game's ID.
        :type game_id: string.
        """
        for game in self.all_games:
            if game.game_id() == game_id:
                return game.num_of_players()
        return None

    def join_game_connection(self, connection):
        """Handles a connection for a client.

        :param connection: The connection to the client.
        :type connection: TCP Socket Connection."""
        try:
            while True:
                data = connection.recv(4096)  # Get data from client
                # decode and create dict from data
                msg = json.loads(data.decode())
                print("Received: ",msg)
                if "create_game" in msg:  # it should followed with name
                    this_game = self.create_new_game(msg["create_game"])
                    jsonmsg = {"player_number": this_game.num_of_players(
                    ), "game_id": this_game.game_id(), "room_code": this_game.room_code()}
                    string = json.dumps(jsonmsg)
                    connection.sendall(string.encode())
                    continue
                elif "show_game_list" in msg:
                    id_array = []
                    num_array = []
                    public_array = []
                    for game in self.all_games:
                        id_array.append(game.game_id())
                        num_array.append(game.player_num_enter_lobby)
                        public_array.append(game.is_public_game())
                    data = {"game_id": id_array, "num": num_array,
                            "is_public": public_array}
                    data = json.dumps(data)
                    connection.sendall(data.encode())
                elif "check_game" in msg:
                    data = {"game_id": msg["check_game"], "result": (self.check_if_game_started(
                        msg["check_game"]) or self.get_game_by_id(msg["check_game"]).player_num_enter_lobby == 4),
                            "player_number": self.get_game_by_id(msg["check_game"]).player_num_enter_lobby}
                    data = json.dumps(data)
                    connection.sendall(data.encode())
                elif "check_room_code" in msg:
                    exists = False
                    for game in self.all_games:
                        if game.room_code() == msg["check_room_code"]:
                            exists = True
                            data = {"exists": True, "room_code": game.room_code(),
                                    "num_of_players": game.player_num_enter_lobby, "game_id": game.game_id()}
                            data = json.dumps(data)
                            connection.sendall(data.encode())
                            break
                    if not exists:
                        if msg["check_type"] == "create":
                            new_game = self.create_new_game(
                                msg["check_room_code"])
                            data = {"exists": False,
                                    "new_game_id": new_game.game_id()}
                        else:
                            data = {"exists": False}
                        data = json.dumps(data)
                        connection.sendall(data.encode())
                    continue
                elif "in_lobby" in msg:
                    self.get_game_by_id(msg["game_id"]).player_num_enter_lobby += 1
                elif "leave_lobby" in msg:
                    cur_game = self.get_game_by_id(msg["game_id"])
                    cur_game.player_num_enter_lobby -= 1
                    if cur_game.player_num_enter_lobby == 0:
                        self.all_games.remove(cur_game)
                    elif (cur_game.player_num_press_start == cur_game.player_num_enter_lobby) and (cur_game.player_num_enter_lobby != 0):
                        cur_game._max_players = cur_game.player_num_press_start
                elif "start_game" in msg:
                    last = False
                    cur_game = self.get_game_by_id (msg["game_id"])
                    cur_game.player_num_press_start += 1
                    if cur_game.player_num_press_start == cur_game.player_num_enter_lobby:
                        last = True
                        cur_game._max_players = cur_game.player_num_press_start
                    while not cur_game.is_full():
                        sleep(2)
                        continue
                    try:
                        _thread.start_new_thread(cur_game.connection_handler,
                                                 (connection, msg["name"]))
                        if last:
                            self.all_games.remove(cur_game)
                        while True:
                            continue
                        # Starts a new thread for each connection.
                    except InterruptedError:
                        print("Error! The signal has been interrupted.")
                        connection.close()

        except sockerr:
            connection.close()


if __name__ == "__main__":
    """Start the Server for Ludo.

    Creates an instance of Games with Port Number 10001 and calls its method to handle requests.
    """

    try:
        games = Lobby(10000)  # Creates instance of class
        games.listen()
    except OSError:
        print("OS Error: Port number already in use or another server process may be running")
        sys.exit()
