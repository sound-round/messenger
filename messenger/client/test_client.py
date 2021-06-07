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

def remove_all(f):
    for widget in f.winfo_children():
        widget.destroy()

def get_quit_button():
    quit_button = tk.Button(root,
                       text="QUIT",
                       command=callback)
    return quit_button


root = tk.Tk()
root.title("messenger")
root.geometry('300x130')


menu = tk.Menu(root)
root.config(menu=menu)
filemenu = tk.Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Quit", command=callback)

#frame = tk.Frame(root)
#frame.pack()

#TODO refactor, separate UI and Logic and network to multiple files
#TODO advanced - investigate slow response times (measure and log some basic times)

def display_register_ui():
    #print("Do register, todo show login and password")
    remove_all(root)
    login_label = tk.Label(root, text="Login")
    login_entry = tk.Entry(root)
    password_label = tk.Label(root, text="Password")
    password_entry = tk.Entry(root)
    result_text = StringVar()
    result_label = tk.Label(root, textvariable=result_text)

    def doActualRegister():
        login = login_entry.get()
        password = password_entry.get()
        request_output = '\n'.join([
            "do actual register network request...",
            f'login: {login}',
            f'password: {password}',
        ])
        print(request_output)
        request_json = json.dumps({'login': login, 'password': password})
        response = requests.post("http://localhost:8080/register", data=request_json)
        response_text = response.text  # How does it work?
        print(response_text)

        result_text.set(''.join(["result= ", json.loads(response_text)['result']]))

    register_button = tk.Button(root,
                               text="do Register",
                               command=doActualRegister)
    login_label.grid(row=0,)
    login_entry.grid(row=0, column=1)
    password_label.grid(row=1)
    password_entry.grid(row=1, column=1)
    register_button.grid(row=2)
    result_label.grid(row=2, column=1)
    get_quit_button().grid(row=3)


#def login():
 #   print("Do login, todo show login and password")
 #   removeAll(root)
    #TODO implement login button-logic similar to register button


def display_login_ui():
    remove_all(root)
    login_label = tk.Label(root, text="Login")
    login_entry = tk.Entry(root)
    password_label = tk.Label(root, text="Password")
    password_entry = tk.Entry(root)
    result_text = StringVar()
    result_label = tk.Label(root, textvariable=result_text)

    def do_actual_login():
        login = login_entry.get()
        password = password_entry.get()
        request_output = '\n'.join([
            "do actual login network request...",
            f'login: {login}',
            f'password: {password}',
        ])
        print(request_output)
        request_json = json.dumps({'login': login, 'password': password})
        response = requests.post("http://localhost:8080/login", data=request_json)
        response_text = response.text
        print(response_text)

        result_text.set(''.join(["result= ", json.loads(response_text)['result']]))

    login_button = tk.Button(root,
                               text="do Login",
                               command=do_actual_login)
    login_label.grid(row=0,)
    login_entry.grid(row=0, column=1)
    password_label.grid(row=1)
    password_entry.grid(row=1, column=1)
    login_button.grid(row=2)
    result_label.grid(row=2, column=1)
    get_quit_button().grid(row=3)




login_button = tk.Button(root,
                         text="Login",
                         command=display_login_ui)

register_button = tk.Button(root,
                            text="Register",
                            command=display_register_ui)


login_button.grid(row=0, padx=4)
register_button.grid(row=0, column=1, pady=10)
get_quit_button().grid(row=1)


root.mainloop()
