import _thread
import json
from socket import *
from tkinter import *
from tkinter.scrolledtext import ScrolledText

class ChatBox():
    def __init__(self,sock):
        self.name = "" 
        self.sock = sock


        

    def new_message(self,msg):
        string = msg["Name"] + ": " + msg["msg"]
        self.recvd.insert("end","%s \n"%string)
        self.recvd.see(END)

    
    def send(self,event):
        if self.msg.get().strip() != "":
            message = {"Name":self.name,"msg":self.msg.get()}
            message = json.dumps(message)
            self.sock.sendall(message.encode())
            self.msg.delete(0, 'end')

        
    def start(self,name):
        self.name = name
        self.root = Tk()
        self.frame = Frame(self.root)
        self.msg = Entry(self.frame, width=50, font=('TkDefaultFont', 11)) #Where the Client enters the message
        self.msg.configure(bg='pink')
        self.recvd =ScrolledText(self.frame,height=30,width=50) #The text area where all received messages go.
        self.recvd.configure(bg='lightblue')
        self.root.title("Chat")
        self.root.minsize(500,500)
        self.root.maxsize(500,500)
        self.root.configure(bg='lightblue')
        self.root.bind('<Return>',self.send)
        self.recvd.pack()
        self.msg.pack(ipady=5)
        self.frame.pack()
        self.root.mainloop()
