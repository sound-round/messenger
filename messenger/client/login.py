import tkinter as tk
from tkinter import StringVar
from messenger.client import network
from messenger.client.support import remove_all, add_menu, get_back_button, get_quit_button
from messenger.client import mainmenu
from messenger.client import chats_menu

def display_login_ui(root):
    remove_all(root)
    login_label = tk.Label(root, text="Login")
    login_entry = tk.Entry(root)
    password_label = tk.Label(root, text="Password")
    password_entry = tk.Entry(root)
    result_text = StringVar()
    result_label = tk.Label(root, textvariable=result_text)
    add_menu(root)

    def login():
        login = login_entry.get()
        password = password_entry.get()
        response = network.do_actual_login(
            login, password
        )
        result_text.set(
            ''.join(["result= ", response['result']])
        )
        if response['result'] != "ok":
            return
        chats_menu.display_chats_ui(root)
        # create_tables()???

    login_button = tk.Button(root,
                             text="do Login",
                             command=login)

    login_label.grid(row=0, )
    login_entry.grid(row=0, column=1)
    password_label.grid(row=1)
    password_entry.grid(row=1, column=1)
    login_button.grid(row=2)
    result_label.grid(row=2, column=1)
    get_back_button(root, mainmenu.display_mainmenu).grid(row=3)
    get_quit_button(root).grid(row=3, column=1)