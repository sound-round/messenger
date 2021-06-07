import urllib.request
import requests
import json

##contents = urllib.request.urlopen("http://localhost:8080/register").read()

# print(contents)


# типы клиента
# 1) Command line client -
# 2) Desktop ui client - tkinter,
# 3) web client - some python web libraries?


import tkinter as tk
from tkinter import LEFT, RIGHT, BOTTOM, StringVar
from tkinter import messagebox as mb

def callback():
    if mb.askyesno('Verify', 'Really quit?'):
        mb.showwarning('Yes', quit())

def removeAll(f):
    for widget in f.winfo_children():
        widget.destroy()


root = tk.Tk()
root.title("messenger")
root.geometry('300x100')


menu = tk.Menu(root)
root.config(menu=menu)
filemenu = tk.Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Quit", command=callback)

#frame = tk.Frame(root)
#frame.pack()

#TODO refactor, separate UI and Logic and network to multiple files
#TODO advanced - investigate slow response times (measure and log some basic times)

def displayRegisterUi():
    print("Do register, todo show login and password")
    removeAll(root)
    loginLabel = tk.Label(root, text="Login")
    loginEntry = tk.Entry(root)
    passwordLabel = tk.Label(root, text="Password")
    passwordEntry = tk.Entry(root)
    resultText = StringVar()
    resultLabel = tk.Label(root, textvariable=resultText)
    get_quit_button()


    def doActualRegister():
        login = loginEntry.get()
        password = passwordEntry.get()
        print("do actual register network request etc..." + login + " " + password)
        requestJson = json.dumps({'login': login, 'password': password})
        response = requests.post("http://localhost:8080/register", data=requestJson)
        responseText = response.text
        print(responseText)

        resultText.set("result= " + json.loads(responseText)['result'])
        #resultLabel.pack(side=BOTTOM)

    registerButton = tk.Button(root,
                               text="do Register",
                               command=doActualRegister)
    loginLabel.grid(row=0,)
    loginEntry.grid(row=0, column=1)
    passwordLabel.grid(row=1)
    passwordEntry.grid(row=1, column=1)
    registerButton.grid(row=2)
    resultLabel.grid(row=2, column=1)

def login():
    print("Do login, todo show login and password")
    removeAll(root)
    #TODO implement login button-logic similar to register button




def get_quit_button():
    quit_button = tk.Button(root,
                       text="QUIT",
                       command=callback)
    return quit_button


loginButton = tk.Button(root,
                        text="Login",
                        command=login)

registerButton = tk.Button(root,
                           text="Register",
                           command=displayRegisterUi)


loginButton.grid(row=0, padx=4)
registerButton.grid(row=0, column=1, pady=10)
get_quit_button().grid(row=1)


root.mainloop()
