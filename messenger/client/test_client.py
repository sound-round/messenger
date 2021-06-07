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
#root.title("messenger")

menu = tk.Menu(root)
root.config(menu=menu)
filemenu = tk.Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Quit", command=callback)

frame = tk.Frame(root)
frame.pack()

#TODO refactor, separate UI and Logic and network to multiple files
#TODO advanced - investigate slow response times (measure and log some basic times)

def displayRegisterUi():
    print("Do register, todo show login and password")
    removeAll(frame)
    loginLabel = tk.Label(frame, text="Login")
    loginEntry = tk.Entry(frame)
    passwordLabel = tk.Label(frame, text="Password")
    passwordEntry = tk.Entry(frame)
    resultText = StringVar()
    resultLabel = tk.Label(frame, textvariable=resultText)
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
        resultLabel.pack(side=BOTTOM)

    registerButton = tk.Button(frame,
                               text="do Register",
                               command=doActualRegister)
    loginLabel.pack(side=LEFT)
    loginEntry.pack(side=LEFT)
    passwordLabel.pack(side=RIGHT)
    passwordEntry.pack(side=RIGHT)
    registerButton.pack(side=BOTTOM)
    resultLabel.pack(side=BOTTOM)

def login():
    print("Do login, todo show login and password")
    removeAll(frame)
    #TODO implement login button-logic similar to register button




def get_quit_button():
    quit_button = tk.Button(frame,
                       text="QUIT",
                       command=callback)
    quit_button.pack(side=BOTTOM)
    return quit_button

get_quit_button()

registerButton = tk.Button(frame,
                           text="Register",
                           command=displayRegisterUi)

registerButton.pack(side=tk.LEFT)

loginButton = tk.Button(frame,
                        text="Login",
                        command=login)
loginButton.pack()
registerButton.pack(side=tk.LEFT)

root.mainloop()
