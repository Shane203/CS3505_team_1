import _thread
import json
from socket import *
from tkinter import *
from tkinter.scrolledtext import ScrolledText


class ChatBox():
    """
    Creates a chat object/window.
    It allows multiple players to chat with each other if they wish to.
    
    :param sock: This is the socket through which messages will be
           sent/received.
    :type sock: python socket
    """
    def __init__(self, sock):
        self.name = ""  # Initially set to empty string
        self.sock = sock  # set socket to a socket already being used
        
    def new_message(self, msg):
        """
        When a message is received this will show it in the chat window.

        :param msg: New message received from other player
        :type msg: String.
        """
        string = msg["Name"] + ": " + msg["msg"]  # concatenate name + message
        # shows the message on the screen
        self.recvd.insert("end", "%s \n" % string)
        self.recvd.see(END)  # always shows last line received
    
    def send(self, event):
        """
        Sends a json message to server when you press "Return" key to send a
        message.

        :param event: Gets called when an event happens (Return Key pressed)
        :type event: Key Press Event.
        """
        if self.msg.get().strip() != "":  # validates empty string
            # sets message to be sent
            message = {"Name": self.name, "msg": self.msg.get()}
            message = json.dumps(message)  # converts it in json form
            self.sock.sendall(message.encode())  # sends message to server
            self.msg.delete(0, 'end')  # clear the variable
        
    def start(self, name):
        """ 
        creates a tkinter window where a person can send/receive messages
        from others.

        :param name: Name of player (self)
        :type name: String.
        """
        self.name = name  # set name to the name entered in form
        self.root = Tk()  # creates tkinter window
        # Create a frame on the window
        self.frame = Frame(self.root)
        # Where the Client enters the message
        self.msg = Entry(self.frame, width=50, font=('TkDefaultFont', 11))
        # Set background colour of textfield
        self.msg.configure(bg='pink')
        # The text area where all received messages go.
        self.recvd = ScrolledText(self.frame, height=30, width=50)
        # set background colour of received messages
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
