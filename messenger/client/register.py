import tkinter as tk
#from tkinter import ttk
from tkinter import StringVar
from tkinter import messagebox as mb
from messenger.client import network
from messenger.client.network import get_username
from messenger.server.messages import Message
import sqlite3
import datetime
import psycopg2
from messenger.client import mainmenu
from messenger.client.support import remove_all, add_menu, get_back_button, get_quit_button


def display_register_ui(root):
    remove_all(root)
    login_label = tk.Label(root, text="Login")
    login_entry = tk.Entry(root)
    password_label = tk.Label(root, text="Password")
    password_entry = tk.Entry(root)
    result_text = StringVar()
    result_label = tk.Label(root, textvariable=result_text)
    add_menu(root)

    def register():
        login = login_entry.get()
        password = password_entry.get()

        response = network.register(
            login, password
        )
        result_text.set(
            ''.join(["result= ", response['result']])
        )

    register_button = tk.Button(root,
                                text="do Register",
                                command=register)

    login_label.grid(row=0, )
    login_entry.grid(row=0, column=1)
    password_label.grid(row=1)
    password_entry.grid(row=1, column=1)
    register_button.grid(row=2)
    result_label.grid(row=2, column=1)
    get_back_button(root, mainmenu.display_mainmenu).grid(row=3)
    get_quit_button(root).grid(row=3, column=1)