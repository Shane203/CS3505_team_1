# Team 1
import json
from tkinter import *
from tkinter.scrolledtext import ScrolledText


class ChatBox(object):
    """
    Creates a chat object/window.
    It allows multiple player to chat with each other if they wish to.

    :param sock: This is the socket through which messages will be
                 sent/received.
    :type sock: python socket
    """
    def __init__(self, sock):
        self.name = ""  # Initially set to empty string
        self.sock = sock  # set socket to a socket already being used

    def new_message(self, msg):
        """
        When a message is recieved this will show it in the chat window

        :param msg: New message recieved from other player
        :type msg: String.
        """
        # concatenate name + message
        string = msg["name"] + ": " + msg["chat_msg"]
        # shows the message on the screen
        self.recvd.insert("end", "%s \n" % string)
        # always shows last line received
        self.recvd.see(END)

    def send(self, event):
        """
        sends a json message to server when you press "Return" key
        to send a message.
        """
        if self.msg.get().strip() != "":  # validates empty string
            # sets message to be sent
            message = {"name": self.name, "chat_msg": self.msg.get()}
            message = json.dumps(message)  # converts it in json form
            self.sock.sendall(message.encode())  # sends message to server
            self.msg.delete(0, 'end')  # clear the variable
        
    def start(self, name):
        """ 
        creates a tkinter window where a person can send/receive
        messages from others

        :param name: Name of player (self)
        :type name: String.
        """
        self.name = name  # set name to the name entered in form
        self.root = Tk()  # creates tkinter window
        self.root.geometry('+%d+%d' % (1000, 0))
        self.frame = Frame(self.root)  # create a frame on the window
        # Where the Client enters the message
        self.msg = Entry(self.frame, width=50, font=('TkDefaultFont', 11))
        self.msg.configure(bg='pink')  # set background colour of textfield
        # The text area where all received messages go.
        self.recvd = ScrolledText(self.frame, height=29, width=50)
        # Set background colour of received messages
        self.recvd.configure(bg='lightblue')
        self.root.title("Chat")  # set title of window to chat
        self.root.minsize(500, 500)  # minimum size of tkinter window
        self.root.maxsize(500, 500)  # maximum size of tkinter window
        self.root.configure(bg='lightblue')  # set background of tkinter window
        self.root.bind('<Return>', self.send)  # listens for return key press
        self.recvd.pack()  # packs message box
        self.msg.pack(ipady=5)  # packs textfield
        self.frame.pack()  # packs frame
        self.root.mainloop()  # loop for showing new message
