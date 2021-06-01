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


def removeAll(f):
    for widget in f.winfo_children():
        widget.destroy()


root = tk.Tk()

frame = tk.Frame(root)
frame.pack()

#TODO refactor, separate UI and Logic and network to multiple files
#TODO advanced - investigate slow response times (measure and log some basic times)

def displayRegisterUi():
    print("Do register, todo show login and password")
    removeAll(frame)
    loginLabel = tk.Label(text="Login")
    loginEntry = tk.Entry(frame)
    passwordLabel = tk.Label(text="Password")
    passwordEntry = tk.Entry(frame)
    resultText = StringVar()
    resultLabel = tk.Label(frame, textvariable=resultText)

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
