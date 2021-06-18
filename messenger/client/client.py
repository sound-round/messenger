from messenger.client import network

# contents = urllib.request.urlopen("http://127.0.0.1:8080/register").read()

# print(contents)


# типы клиента
# 1) Command line client -
# 2) Desktop ui client - tkinter,
# 3) web client - some python web libraries?


import tkinter as tk
from tkinter import StringVar
from tkinter import messagebox as mb

from messenger.server.messages import Message

from messenger.client.network import global_user_id




# TODO class Chat(to_user_id, messages: Message[])


class Chat:
    def __init__(self, with_user_id, message):
        self.with_user_id = with_user_id
        self.messages = []
        self.messages.append(message)


class ChatManager:  #TODO move to client
    store = []

    def add_message(self, message):
        with_user_id = message.to_user_id if message.to_user_id != global_user_id else message.from_user_id
        for chat in self.store:
            if chat.with_user_id == with_user_id:
                chat.messages.append(message)
                print("add message to existing chat " + str(chat.__dict__))
                return
        self.store.append(Chat(with_user_id, message))

def get_username(user_id):
    # TODO this in network
    return "Test"

chatManager = ChatManager()

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


    def display_chats_ui():
        remove_all(root)
        
        run_update_loop()
        login_label = tk.Label(root, text="ChatManager")

        start_chat = tk.Button(root, text="Start chat")
        #TODO open dialog with Login input -
        # находит юзера по логину
        # или показывает ошибку
        # если нашло тогда показывает UI чата, где видны сообщения и можно отправить новое сообщение

        login_label.place(x=10, y=0, width=100, height=20)
        start_chat.place(x=10, y=25, width=100, height=20)

        def populate_chats(frame):
            if not frame.winfo_exists():
                return
            remove_all(frame)
            row = 0
            for chat in chatManager.store:
                tk.Label(frame, text=get_username(chat.with_user_id)).grid(row=row, column=0)
                last_message_text = chat.messages[-1].message
                tk.Label(frame, text=last_message_text).grid(row=row + 1, column=0)
                #TODO draw thin line separator
                tk.Label(frame, text="----------").grid(row=row + 2, column=0)
                row = row + 3

            root.after(3000, populate_chats, frame)

        def on_frame_configure(canvas):
            '''Reset the scroll region to encompass the inner frame'''
            canvas.configure(scrollregion=canvas.bbox("all"))

        #TODO resize root window
        canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        frame = tk.Frame(canvas, background="#ffffff")
        scroll_bar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll_bar.set)

        scroll_bar.place(x=300, y=45, width=20, height=480)
        canvas.place(x=0, y=45, width=300, height=480)
        canvas.create_window((4, 4), window=frame, anchor="nw")

        frame.bind("<Configure>", lambda event, canvas=canvas: on_frame_configure(canvas))

        populate_chats(frame)



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

            response = network.register(
                login, password
            )
            result_text.set(
                ''.join(["result= ", response['result']])
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
            response = network.do_actual_login(
                login, password
            )
            result_text.set(
                ''.join(["result= ", response['result']])
            )
            display_chats_ui()

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

    def run_update_loop():
        print("TODO call server readMessages")
        response = network.read_messages()
        for dict in response["messages"]:
            newMessage = Message(dict["from_user_id"], global_user_id, dict["message"], dict["date"])
            chatManager.add_message(newMessage)
            print("got new message " + str(newMessage.__dict__))

        root.after(3000, run_update_loop)

    root = tk.Tk()
    root.title("messenger")
    root.geometry('320x568')

    display_mainmenu()

    root.mainloop()


if __name__ == '__main__':
    main()
