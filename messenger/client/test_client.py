import requests
import json
from messenger.client import network

# contents = urllib.request.urlopen("http://localhost:8080/register").read()

# print(contents)


# типы клиента
# 1) Command line client -
# 2) Desktop ui client - tkinter,
# 3) web client - some python web libraries?


import tkinter as tk
from tkinter import LEFT, RIGHT, BOTTOM, StringVar
from tkinter import messagebox as mb


def main():

    def callback():
        if mb.askyesno('Verify', 'Really quit?'):
            mb.showwarning('Yes', quit())

    def return_back():
        remove_all(root)
        display_mainmenu()

    def remove_all(f):
        for widget in f.winfo_children():
            widget.destroy()

    def get_quit_button():
        quit_button = tk.Button(root,
                                text="QUIT",
                                command=callback)
        return quit_button

    def get_back_button():
        back_button = tk.Button(root,
                                text="Back",
                                command=return_back)
        return back_button

    def add_menu():
        menu = tk.Menu(root)
        root.config(menu=menu)
        filemenu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Quit", command=callback)

    # TODO refactor, separate UI and Logic and network to multiple files
    # TODO advanced - investigate slow response times (measure and log some basic times)

    def display_register_ui():
        remove_all(root)
        login_label = tk.Label(root, text="Login")
        login_entry = tk.Entry(root)
        password_label = tk.Label(root, text="Password")
        password_entry = tk.Entry(root)
        result_text = StringVar()
        result_label = tk.Label(root, textvariable=result_text)
        add_menu()

        def register():
            login = login_entry.get()
            password = password_entry.get()
            response_text = network.do_actual_register(
                login, password
            )
            result_text.set(
                ''.join(["result= ", json.loads(response_text)['result']])
            )

        register_button = tk.Button(root,
                                    text="do Register",
                                    command=register)

        login_label.grid(row=0,)
        login_entry.grid(row=0, column=1)
        password_label.grid(row=1)
        password_entry.grid(row=1, column=1)
        register_button.grid(row=2)
        result_label.grid(row=2, column=1)
        get_back_button().grid(row=3)
        get_quit_button().grid(row=3, column=1)

        # TODO implement login button-logic similar to register button

    def display_login_ui():
        remove_all(root)
        login_label = tk.Label(root, text="Login")
        login_entry = tk.Entry(root)
        password_label = tk.Label(root, text="Password")
        password_entry = tk.Entry(root)
        result_text = StringVar()
        result_label = tk.Label(root, textvariable=result_text)
        add_menu()

        def login():
            login = login_entry.get()
            password = password_entry.get()
            response_text = network.do_actual_login(
                login, password
            )
            result_text.set(
                ''.join(["result= ", json.loads(response_text)['result']])
            )

        login_button = tk.Button(root,
                                 text="do Login",
                                 command=login)

        login_label.grid(row=0,)
        login_entry.grid(row=0, column=1)
        password_label.grid(row=1)
        password_entry.grid(row=1, column=1)
        login_button.grid(row=2)
        result_label.grid(row=2, column=1)
        get_back_button().grid(row=3)
        get_quit_button().grid(row=3, column=1)

    def display_mainmenu():
        add_menu()

        login_button = tk.Button(root,
                                 text="Login",
                                 command=display_login_ui)

        register_button = tk.Button(root,
                                    text="Register",
                                    command=display_register_ui)

        login_button.grid(row=0, padx=4)
        register_button.grid(row=0, column=1, pady=10)
        get_quit_button().grid(row=1)

    root = tk.Tk()
    root.title("messenger")
    root.geometry('300x150')

    display_mainmenu()

    root.mainloop()


if __name__ == '__main__':
    main()
