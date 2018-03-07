# Team 1
from tkinter import *
import json


class Form:
    def __init__(self, rules_file, connection):
        self.connection = connection
        self.root = Tk()
        self.filename = rules_file
        self.current_page = None
        self.game_id = None
        self.name = None
        self.player_number = None

    def home_page(self):
        # Same setup for each new page
        self.root.destroy()
        self.root = Tk()
        self.root.title("Ludo")
        self.current_page = "home_page"
        frame = Frame(self.root)

        ludo_label = Label(frame, text="Ludo", fg="black")
        blank = Label(frame, text="", fg="black")

        # This is the part that varies between pages
        create_game = Button(
            frame, width=30, text="Create Game", command=self.create_game)
        join_public = Button(
            frame, width=30, text="Join Public Game", command=self.join_public)
        join_private = Button(
            frame, width=30, text="Join Private Game", command=self.join_private)
        rules = Button(frame, width=30, text="Rules", command=self.show_rules)

        # Drawing each widget on to the frame
        self.root.minsize(width=220, height=210)
        self.root.maxsize(width=220, height=210)
        self.root.configure(background="white")

        frame.pack()
        frame.configure(background="white")

        ludo_label.grid(row=1, column=1, columnspan=2)
        ludo_label.configure(font=("Arial", 32), background="white")

        blank.grid(row=2, column=3)
        blank.configure(background="white")

        create_game.grid(row=3, column=1, columnspan=2)
        create_game.configure(background="lightgreen")

        join_public.grid(row=4, column=1, columnspan=2)
        join_public.configure(background="lightblue")

        join_private.grid(row=5, column=1, columnspan=2)
        join_private.configure(background="lightgreen")

        rules.grid(row=6, column=1, columnspan=2)
        rules.configure(background="lightblue")

        self.root.mainloop()

    def create_game(self):
        # Same setup for each new page
        self.root.destroy()
        self.root = Tk()
        self.root.title("Ludo")
        self.current_page = "create_game"
        frame = Frame(self.root)

        ludo_label = Label(frame, text="Ludo", fg="black")
        blank = Label(frame, text="", fg="black")
        back = Button(frame, text="Back", command=self.back)

        # This is the part that varies between pages
        label = Label(frame, width=30, text="Create New Game", fg="black")
        room_label = Label(frame, text="Room Code:", fg="black")
        room_entry = Entry(frame, width=20)
        leave_blank = Label(
            frame, width=30, text="Leave blank for Public Game")
        create = Button(frame, width=30, text="Create",
                        command=lambda: self.check_room_code("create", room_entry.get()))

        # Drawing each widget on to the frame
        self.root.minsize(width=220, height=210)
        self.root.maxsize(width=220, height=210)
        self.root.configure(background="white")

        frame.pack()
        frame.configure(background="white")

        ludo_label.grid(row=1, column=1, columnspan=2)
        ludo_label.configure(font=("Arial", 32), background="white")

        blank.grid(row=2, column=3)

        label.grid(row=3, column=1, columnspan=2)
        label.configure(background="white")

        room_label.grid(row=4, column=1)
        room_label.configure(background="white")

        room_entry.grid(row=4, column=2)
        room_entry.configure(background="white")

        leave_blank.grid(row=5, column=1, columnspan=2)
        leave_blank.configure(background="white")

        create.grid(row=6, column=1, columnspan=2)
        create.configure(background="lightgreen")

        back.grid(row=7, column=1)
        back.configure(background="red")
        self.root.mainloop()

    def on_double_click(self, event):
        widget = event.widget
        selection = widget.curselection()
        string = widget.get(selection[0])
        print(string)
        self.game_id = string.split(" ")[1]
        self.player_number = string.split(" ")[3]
        print(self.game_id)
        print(self.player_number)

    def check_conflict(self, name, game_id):
        self.connection.send_check_if_game_is_started(int(game_id))
        # decodes received data.
        data = self.connection.sock.recv(4096).decode()
        msg = json.loads(data)
        if "result" in msg and msg["result"]:
            self.public_room_is_full()
        else:
            self.start_game(name, int(game_id))

    def check_selected(self):
        if self.player_number is not None:
            self.connection.send_check_if_game_is_started(int(self.game_id))
            # decodes received data.
            data = self.connection.sock.recv(4096).decode()
            msg = json.loads(data)
            if msg["result"]:
                self.public_room_is_full()
            else:
                self.player_number = int(msg["player_number"])+1
                self.connection.send_join_lobby_message (self.game_id)
                self.lobby("public", "", self.player_number, self.game_id)

    def public_room_is_full(self):
        self.root.destroy()
        self.root = Tk()
        self.root.title("Ludo")
        self.current_page = "public_room_is_full"
        frame = Frame(self.root)

        ludo_label = Label(frame, text="Ludo", fg="black")
        blank = Label(frame, text="", fg="black")
        back = Button(frame, text="Back", command=self.back)

        # This is the part that varies between pages
        no_room = Label(frame, width=30,
                        text="Current Room is full or deleted", fg="black")
        try_again = Label(
            frame, width=30, text="Please try another room", fg="black")

        # Drawing each widget on to the frame
        self.root.minsize(width=220, height=210)
        self.root.maxsize(width=220, height=210)
        self.root.configure(background="white")

        frame.pack()
        frame.configure(background="white")

        ludo_label.grid(row=1, column=1, columnspan=2)
        ludo_label.configure(font=("Arial", 32), background="white")

        blank.grid(row=2, column=3)
        blank.configure(background="white")

        no_room.grid(row=3, column=1, columnspan=2)
        no_room.configure(background="white")

        try_again.grid(row=4, column=1, columnspan=2)
        try_again.configure(background="white")

        back.grid(row=7, column=1)
        back.configure(background="red")
        self.root.mainloop()

    def join_public(self):
        # Same setup for each new page
        self.root.destroy()
        self.root = Tk()
        self.root.title("Ludo")
        self.current_page = "join_public"
        frame = Frame(self.root)

        ludo_label = Label(frame, text="Ludo", fg="black")
        blank = Label(frame, text="", fg="black")
        back = Button(frame, text="Back", command=self.back)

        # This is the part that varies between pages
        list_label = Label(frame, width=30, text="List of Games", fg="black")
        list_box = Listbox(frame, width=30)

        # send message to the server
        self.connection.send_join_public_game()

        # receive message from the server
        # decodes received data.
        data = self.connection.sock.recv(4096).decode()
        msg = json.loads(data)
        print(msg)
        id_array = msg["game_id"]
        num_array = msg["num"]
        is_public_array = msg["is_public"]
        # Accept public games from server

        # put them in the local connection attribute
        if msg["game_id"]:
            for index in range(len(id_array)):
                if is_public_array[index]:
                    list_box.insert("end", "Game %s --- %s / 4 in lobby" %
                                    (id_array[index], num_array[index]))
        list_box.bind("<Double-Button-1>", self.on_double_click)
        # list_box.pack(side="top", fill="both", expand=True)
        join_game = Button(frame, width=30, text="Join Game",
                           command=lambda: self.check_selected())
        # Drawing each widget on to the frame
        self.root.minsize(width=220, height=345)
        self.root.maxsize(width=220, height=345)
        self.root.configure(background="white")

        frame.pack()
        frame.configure(background="white")

        ludo_label.grid(row=1, column=1, columnspan=2)
        ludo_label.configure(font=("Arial", 32), background="white")

        blank.grid(row=2, column=3)
        blank.configure(background="white")

        list_label.grid(row=3, column=1, columnspan=2)
        list_label.configure(background="white")

        list_box.grid(row=4, column=1, rowspan=3)

        join_game.grid(row=7, column=1, columnspan=2)
        join_game.configure(background="lightblue")

        back.grid(row=8, column=1)
        back.configure(background="red")
        self.root.mainloop()

    def join_private(self):
        # Same setup for each new page
        self.root.destroy()
        self.root = Tk()
        self.root.title("Ludo")
        self.current_page = "join_private"
        frame = Frame(self.root)

        ludo_label = Label(frame, text="Ludo", fg="black")
        blank = Label(frame, text="", fg="black")
        back = Button(frame, text="Back", command=self.back)

        # This is the part that varies between pages
        label = Label(frame, width=30, text="Join Private Game", fg="black")
        room_label = Label(frame, text="Enter Room Code:", fg="black")
        room_entry = Entry(frame, width=20)
        join_game = Button(frame, text="Join Game", width=30,
                           command=lambda: self.check_room_code("join", room_entry.get()))

        # Drawing each widget on to the frame
        self.root.minsize(width=220, height=210)
        self.root.maxsize(width=220, height=210)
        self.root.configure(background="white")

        frame.pack()
        frame.configure(background="white")

        ludo_label.grid(row=1, column=1, columnspan=2)
        ludo_label.configure(font=("Arial", 32), background="white")

        blank.grid(row=2, column=3)
        blank.configure(background="white")

        label.grid(row=3, column=1, columnspan=2)
        label.configure(background="white")

        room_label.grid(row=4, column=1)
        room_label.configure(background="white")

        room_entry.grid(row=4, column=2)
        room_entry.configure(background="white")

        join_game.grid(row=5, column=1, columnspan=2)
        join_game.configure(background="lightblue")

        back.grid(row=7, column=1)
        back.configure(background="red")
        self.root.mainloop()

    def update(self,lobby_type, room_code, player_number, game_id):
        # send message to the server
        self.connection.send_join_public_game ()

        # receive message from the server
        # decodes received data.
        data = self.connection.sock.recv (4096).decode ()
        msg = json.loads (data)
        print (msg)
        id_array = msg["game_id"]
        num_array = msg["num"]
        num = num_array[id_array.index(int(game_id))]
        self.lobby(lobby_type,room_code,num,game_id)

    def lobby(self, lobby_type, room_code, player_number, game_id):

        """One function for each type of lobby becasue they're all so similar."""
        # Same setup for each new page
        self.root.destroy()
        self.root = Tk()
        self.root.title("Ludo")
        frame = Frame(self.root)

        # This is the part that varies between pages
        name_label = Label(frame, text="Player Name:", fg="black")
        name_entry = Entry(frame, width=20)
        if lobby_type == "create":
            self.current_page = "create_lobby"
            if len(room_code) == 0:
                label = Label(frame, width=30,
                              text="New Public Game created", fg="black")
                room_label = Label(frame, width=30, text="", fg="black")
            else:
                label = Label(frame, width=30,
                              text="New Private Game created", fg="black")
                room_label = Label(frame, width=30, text=(
                    "Room Code: " + str(room_code)), fg="black")
        elif lobby_type == "public":
            self.current_page = "public_lobby"
            label = Label(frame, width=30, text=("Game " + str(room_code)))
            room_label = Label(frame, width=30, text="", fg="black")
        elif lobby_type == "private":
            self.current_page = "private_lobby"
            label = Label(frame, width=30, text=(
                "Room Code: " + str(room_code)))
            room_label = Label(frame, width=30, text="", fg="black")

        ludo_label = Label (frame, text="Ludo", fg="black")
        blank = Label (frame, text="", fg="black")
        back = Button (frame, text="Back", command=lambda: self.back (game_id))
        in_lobby = Label(frame, width=30, text=("In Lobby: %s/4" % (str(player_number))),
                         fg="black")  # take in number of players in that game
        print(game_id)
        start_game = Button(frame, width=30, text="Start Game",
                            command=lambda: self.check_conflict(name_entry.get(), int(game_id)))

        update = Button(frame, width=30, text="Updating Message",
                            command=lambda: self.update(lobby_type, room_code, player_number, game_id))

        # Drawing each widget on to the frame
        self.root.minsize(width=220, height=260)
        self.root.maxsize(width=220, height=260)
        self.root.configure(background="white")

        frame.pack()
        frame.configure(background="white")

        ludo_label.grid(row=1, column=1, columnspan=2)
        ludo_label.configure(font=("Arial", 32), background="white")

        blank.grid(row=2, column=3)
        blank.configure(background="white")

        name_label.grid(row=3, column=1)
        name_label.configure(background="white")
        name_entry.grid(row=3, column=2)
        name_entry.configure(background="white")

        label.grid(row=4, column=1, columnspan=2)
        label.configure(background="white")

        room_label.grid(row=5, column=1, columnspan=2)
        room_label.configure(background="white")

        in_lobby.grid(row=6, column=1, columnspan=2)
        in_lobby.configure(background="white")

        start_game.grid(row=7, column=1, columnspan=2)
        start_game.configure(background="lightgreen")

        update.grid (row=8, column=1, columnspan=2)
        update.configure (background="lightgreen")

        back.grid(row=9, column=1)
        back.configure(background="red")
        self.root.mainloop()

    def no_room(self):
        # Same setup for each new page
        self.root.destroy()
        self.root = Tk()
        self.root.title("Ludo")
        self.current_page = "no_room"
        frame = Frame(self.root)

        ludo_label = Label(frame, text="Ludo", fg="black")
        blank = Label(frame, text="", fg="black")
        back = Button(frame, text="Back", command=self.back)

        # This is the part that varies between pages
        no_room = Label(frame, width=30,
                        text="Room Code doesn't exist", fg="black")
        try_again = Label(
            frame, width=30, text="Please try another room code", fg="black")

        # Drawing each widget on to the frame
        self.root.minsize(width=220, height=210)
        self.root.maxsize(width=220, height=210)
        self.root.configure(background="white")

        frame.pack()
        frame.configure(background="white")

        ludo_label.grid(row=1, column=1, columnspan=2)
        ludo_label.configure(font=("Arial", 32), background="white")

        blank.grid(row=2, column=3)
        blank.configure(background="white")

        no_room.grid(row=3, column=1, columnspan=2)
        no_room.configure(background="white")

        try_again.grid(row=4, column=1, columnspan=2)
        try_again.configure(background="white")

        back.grid(row=7, column=1)
        back.configure(background="red")
        self.root.mainloop()

    def already_exists(self, code):
        # Same setup for each new page
        self.root.destroy()
        self.root = Tk()
        self.root.title("Ludo")
        self.current_page = "already_exists"
        frame = Frame(self.root)

        ludo_label = Label(frame, text="Ludo", fg="black")
        blank = Label(frame, text="", fg="black")
        back = Button(frame, text="Back", command=self.back)

        # This is the part that varies between pages
        exists = Label(frame, width=30, text=(
            "Room Code %s already exists" % (str(code))), fg="black")
        try_again = Label(
            frame, width=30, text="Please try another room code", fg="black")

        # Drawing each widget on to the frame
        self.root.minsize(width=220, height=210)
        self.root.maxsize(width=220, height=210)
        self.root.configure(background="white")

        frame.pack()
        frame.configure(background="white")

        ludo_label.grid(row=1, column=1, columnspan=2)
        ludo_label.configure(font=("Arial", 32), background="white")

        blank.grid(row=2, column=3)
        blank.configure(background="white")

        exists.grid(row=3, column=1, columnspan=2)
        exists.configure(background="white")

        try_again.grid(row=4, column=1, columnspan=2)
        try_again.configure(background="white")

        back.grid(row=7, column=1)
        back.configure(background="red")
        self.root.mainloop()

    def start_game(self, name, game_id):
        if len(name) != 0:
            self.connection.send_start_the_game(game_id, name)
            self.root.destroy()

    def check_room_code(self, check_type, code):
        if code != "":  # for private game
            data = {"check_room_code": str(code), "check_type": check_type}
            data = json.dumps(data)
            self.connection.sock.sendall(data.encode())
            # only get game.num when you go to lobby
            # decodes received data.
            data = self.connection.sock.recv(4096).decode()
            print(data)
            msg = json.loads(data)
            exists = msg["exists"]
            if exists:
                if check_type == "create":
                    self.already_exists(code)
                elif check_type == "join":
                    self.connection.send_join_lobby_message(msg["game_id"])
                    self.lobby("private", msg["room_code"],
                               msg["num_of_players"]+1, msg["game_id"])
            else:
                if check_type == "create":
                    # Automatically creates new game server-side if one didn't exist
                    self.connection.send_join_lobby_message (msg["new_game_id"])
                    self.lobby("create", code, 1, msg["new_game_id"])
                elif check_type == "join":
                    self.no_room()
        else:  # for public game
            self.connection.send_create_game(code)
            # accepts the id of your newly created game
            data = self.connection.sock.recv(4096).decode()
            msg = json.loads(data)
            print(msg)
            self.connection.send_join_lobby_message (msg["game_id"])
            self.lobby("create", code,
                       msg["player_number"]+1, msg["game_id"], )

    def show_rules(self):
        # Produces a document of the rules of the ludo game.
        # Pops up a separate page, so there's no self.root.destroy()
        file = open(self.filename, "r")
        data = file.read()
        self.root = Tk()
        self.root.title("Rules")
        w = Label(self.root, text=data, fg="black", bg="red")
        w.pack()
        self.root.mainloop()

    def back(self, game_id=None):
        if self.current_page == "create_game" or self.current_page == "join_public" or \
                self.current_page == "join_private":
            self.home_page()
        elif self.current_page == "no_room":
            self.join_private()
        elif self.current_page == "private_lobby":
            self.connection.send_leave_lobby(game_id)
            self.join_private()
        elif self.current_page == "already_exists":
            self.create_game()
        elif self.current_page == "create_lobby":
            self.connection.send_leave_lobby (game_id)
            self.create_game ()
        elif self.current_page == "public_lobby":

            self.connection.send_leave_lobby(game_id)
            self.join_public()
        elif self.current_page == "public_room_is_full":
            self.home_page()

    def run(self):
        self.home_page()
