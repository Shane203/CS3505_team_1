from tkinter import *

class Form:
    
    def __init__(self, rules_file):
        self.root = Tk()
        self.root.title("Ludo")
        self.frame1 = Frame(self.root)
        self.label1 = Label(self.frame1, text="Player Name", fg="black")
        self.name = Entry(self.frame1, width=20)
        self.label2 = Label(self.frame1, text="Server IP", fg="black")
        self.label3 = Label(self.frame1, text="", fg="black")
        self.button = Button(self.frame1, text='Join Game', command=self.get_name_and_ip)
        self.ip = Entry(self.frame1, width=20)
        self.button1 = Button(self.frame1, text='Rules', command=self.show_rules)
        self.filename = rules_file

    def get_name_and_ip(self):
        # Gets the name entered by the player in the name box.
        self.player_name = self.name.get()
        self.ip_address = self.ip.get()
        self.root.destroy()

    def show_rules(self):
        # Produces a document of the rules of the ludo game.
        file = open(self.filename, "r")
        data = file.read()
        root1 = Tk()
        root1.title("Rules")
        w = Label(root1, text=data, fg="black", bg="red")
        w.pack()
        root1.mainloop()

    def draw_form(self):
        # draws the form for the player
        self.root.minsize(width=220, height=100)
        self.root.maxsize(width=220, height=100)
        self.root.configure(background='white')

        self.frame1.pack()
        self.frame1.configure(background='white')

        self.label1.grid(row=1, column=1)
        self.label1.configure(background='white')

        self.name.grid(row=1, column=2)
        self.name.configure(background='white')

        self.label2.grid(row=2, column=1)
        self.label2.configure(background='white')

        self.ip.grid(row=2, column=2)
        self.ip.configure(background='white')

        self.label3.grid(row=3, column=3)

        self.button.grid(row=4, column=2)
        self.button.configure(background='lightgreen')

        self.button1.grid(row=4, column=1)
        self.button1.configure(background='lightblue')
        self.root.mainloop()
        # returns the name entered by the player.
        return (self.player_name, self.ip_address)



