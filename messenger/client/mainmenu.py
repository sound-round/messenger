import tkinter as tk
from messenger.client import login, register
from messenger.client import support


def display_mainmenu(root):
    support.add_menu(root)

    login_button = tk.Button(root,
                             text="Login",
                             command=lambda: login.display_login_ui(root))

    register_button = tk.Button(root,
                                text="Register",
                                command=lambda: register.display_register_ui(root))

    login_button.grid(row=0, padx=4)
    register_button.grid(row=0, column=1, pady=10)
    support.get_quit_button(root).grid(row=1)