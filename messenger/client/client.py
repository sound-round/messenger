from messenger.client import network

# contents = urllib.request.urlopen("http://127.0.0.1:8080/register").read()

# print(contents)


# типы клиента
# 1) Command line client -
# 2) Desktop ui client - tkinter,
# 3) web client - some python web libraries?


import tkinter as tk
#from tkinter import ttk
from tkinter import StringVar
from tkinter import messagebox as mb

from messenger.client.network import global_user_id, get_username
from messenger.server.messages import Message


# TODO class Chat(to_user_id, messages: Message[])


class Chat:
    def __init__(self, with_user_id, message):
        self.with_user_id = with_user_id
        self.messages = []
        self.messages.append(message)


class ChatManager:
    store = []

    def add_message(self, message):
        with_user_id = message.to_user_id if message.to_user_id != global_user_id else message.from_user_id
        for chat in self.store:
            if chat.with_user_id == with_user_id:
                chat.messages.append(message)
                print("add message to existing chat " + str(chat.__dict__))
                return
        self.store.append(Chat(with_user_id, message))

    def get_chat(self, with_user_id):
        for chat in self.store:
            if chat.with_user_id == with_user_id:
                return chat


chat_manager = ChatManager()

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

        def populate_dialog(frame, chat):
            if not frame.winfo_exists():
                return
            remove_all(frame)
            row = 0
            if chat:
                for message in chat.messages:
                    message_text = message.message
                    tk.Label(frame, text=message_text).grid(row=row, column=0)
                    date = message.date
                    tk.Label(frame, text=date).grid(row=row + 1, column=1)
                    #TODO draw thin line separator
                    tk.Label(frame, text="----------").grid(row=row + 2, column=0)
                    row = row + 3

            root.after(3000, populate_dialog, frame, chat)

        def return_to_chats():
            remove_all(root)
            display_chats_ui()

        def open_dialog():
            login = entry.get()
            if not login:
                result_text.set(
                    'login_is_missing'
                )
                return
            response = network.find_user_id(login)
            result_text.set(
                ''.join(["result= ", response['result']])
            )
            if response['result'] != "ok":
                return
            with_user_id = response['user_id']
            chat = chat_manager.get_chat(with_user_id)

            remove_all(root)

            def send_message():
                to_user_id = with_user_id
                message_to_send = message_text.get(1.0, tk.END)
                message_text.delete(1.0, tk.END)

                response = network.send_message(
                    to_user_id, message_to_send
                )
                if response['result'] != "ok":
                    return
                result_text = StringVar()
                result_text.set(
                   ''.join(["result= ", response['result']])
                )

                result_label = tk.Label(root, textvariable=result_text)
                result_label.place(x=10, y=470, width=250, height=20)

            dialog_label = tk.Label(root, text=f"Chat with {login}")
            dialog_label.place(x=10, y=0, width=100, height=20)
            message_text = tk.Text(root)
            message_text.place(x=10, y=490, width=200, height=65)
            scrollbar = tk.Scrollbar(message_text, command=message_text.yview)
            scrollbar.pack(side="right", fill="y")
            message_text.configure(yscrollcommand=scrollbar.set)
            send_button = tk.Button(root, text="Send", command=send_message)
            send_button.place(x=220, y=490, width=50, height=25)
            back_button = tk.Button(root,
                                text="Back",
                                command=return_to_chats)
            back_button.place(x=220, y=525, width=50, height=25)


            chat_canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
            chat_frame = tk.Frame(chat_canvas, background="#ffffff")
            chat_scroll_bar = tk.Scrollbar(root, orient="vertical", command=chat_canvas.yview)
            chat_canvas.configure(yscrollcommand=chat_scroll_bar.set)
            chat_scroll_bar.place(x=300, y=25, width=20, height=440)
            chat_canvas.place(x=0, y=25, width=300, height=440)
            chat_canvas.create_window((4, 4), window=chat_frame, anchor="nw")
            chat_frame.bind("<Configure>", lambda event, canvas=chat_canvas: on_frame_configure(chat_canvas))

            populate_dialog(chat_frame, chat)

        def populate_chats(frame):
            if not frame.winfo_exists():
                return
            remove_all(frame)
            row = 0
            for chat in chat_manager.store:
                response = get_username(chat.with_user_id)
                if response['result'] != "ok":
                    result_text.set(
                        ''.join(["result= ", response['result']])
                    )
                    return
                with_user_login = response['login']
                tk.Label(frame, text=with_user_login).grid(row=row, column=0)
                last_message_text = chat.messages[-1].message
                tk.Label(frame, text=last_message_text).grid(row=row + 1, column=0)
                #TODO draw thin line separator
                tk.Label(frame, text="----------").grid(row=row + 2, column=0)
                #separator = ttk.Separator(frame, orient='horizontal')
                #separator.pack(fill='x')
                row = row + 3

            root.after(3000, populate_chats, frame)

        remove_all(root)
        

        chat_label = tk.Label(root, text="ChatManager")
        login_label = tk.Label(root, text="Enter user login: ")
        start_chat = tk.Button(root, text="Start chat", command=open_dialog)
        back_button = get_back_button()

        chat_label.place(x=10, y=0, width=100, height=20)
        login_label.place(x=10, y=25, width=120, height=20)
        start_chat.place(x=10, y=50, width=100, height=20)
        back_button.place(x=10, y=528, width=100, height=30)

        entry = tk.Entry()
        entry.place(x=130, y=25)
        result_text = StringVar()
        result_label = tk.Label(root, textvariable=result_text)
        result_label.place(x=120, y=50, width=188, height=20)
        run_update_loop(result_text)



        def on_frame_configure(canvas):
            '''Reset the scroll region to encompass the inner frame'''
            canvas.configure(scrollregion=canvas.bbox("all"))

        #TODO resize root window
        canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        frame = tk.Frame(canvas, background="#ffffff")
        scroll_bar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll_bar.set)

        scroll_bar.place(x=300, y=70, width=20, height=455)
        canvas.place(x=0, y=70, width=300, height=455)
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
            if response['result'] != "ok":
                return
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

    def run_update_loop(result_text):
        print("TODO call server readMessages")
        response = network.read_messages()
        if response['result'] != "ok":
            result_text.set(
                ''.join(["result= ", response['result']])
            )
            return
        for message in response["messages"]:
            new_message = Message(message["from_user_id"], global_user_id, message["message"], message["date"])
            chat_manager.add_message(new_message)
            print("got new message " + str(new_message.__dict__))

        root.after(3000, run_update_loop, result_text)

    root = tk.Tk()
    root.title("messenger")
    root.geometry('320x568')

    display_mainmenu()

    root.mainloop()


if __name__ == '__main__':
    main()
