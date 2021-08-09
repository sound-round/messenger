import tkinter as tk
from tkinter import messagebox as mb


def on_frame_configure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))


def remove_all(f):
    for widget in f.winfo_children():
        widget.destroy()


def add_menu(root):
    menu = tk.Menu(root)
    root.config(menu=menu)
    filemenu = tk.Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Quit", command=callback)


def get_quit_button(root):
    quit_button = tk.Button(root,
                            text="QUIT",
                            command=callback)
    return quit_button


def get_back_button(root, func):
    back_button = tk.Button(root,
                            text="Back",
                            command=lambda: return_back(root, func))
    return back_button


def callback():
    if mb.askyesno('Verify', 'Really quit?'):
        mb.showwarning('Yes', quit())


def return_back(root, func):
    remove_all(root)
    func(root)
