import tkinter as tk
from tkinter import StringVar
from messenger.client import network
from messenger.client.network import get_username
from messenger.server.messages import Message
from messenger.client import support, mainmenu, dialog
from messenger.client.sql import create_connection


def display_chats_ui(root):

    def populate_chats(frame):
        if not frame.winfo_exists():
            return
        support.remove_all(frame)
        row = 0
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT * FROM chats;
                    '''
                )
                chats = cursor.fetchall()
                for chat in chats: # TODO this
                    with_user_id = chat[1]
                    last_message_id = chat[2]
                    response = get_username(with_user_id)
                    if response['result'] != "ok":
                        result_text.set(
                            ''.join(["result= ", response['result']])
                        )
                        return
                    with_user_login = response['login']

                    cursor.execute(
                        '''
                        SELECT message FROM messages
                        WHERE id = %s;
                        ''',
                        (last_message_id,)
                    )

                    last_message_text = cursor.fetchone()[0]

                    last_message_text = with_user_login + ": " + last_message_text
                    tk.Label(frame, text=last_message_text).grid(row=row , column=0)
                    row = row + 1

        root.after(3000, populate_chats, frame)

    support.remove_all(root)

    chat_label = tk.Label(root, text="ChatManager")
    login_label = tk.Label(root, text="Enter user login: ")
    start_chat = tk.Button(root, text="Start chat", command=lambda: dialog.open_dialog(root, entry))
    back_button = support.get_back_button(root, mainmenu.display_mainmenu)

    chat_label.place(x=10, y=0, width=100, height=20)
    login_label.place(x=10, y=25, width=120, height=20)
    start_chat.place(x=10, y=50, width=100, height=20)
    back_button.place(x=10, y=528, width=100, height=30)

    entry = tk.Entry()
    entry.place(x=130, y=25)
    result_text = StringVar()
    result_label = tk.Label(root, textvariable=result_text)
    result_label.place(x=120, y=50, width=188, height=20)
    run_update_loop(result_text, root)

    #TODO resize root window
    canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
    frame = tk.Frame(canvas, background="#ffffff")
    scroll_bar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scroll_bar.set)

    scroll_bar.place(x=300, y=70, width=20, height=455)
    canvas.place(x=0, y=70, width=300, height=455)
    canvas.create_window((4, 4), window=frame, anchor="nw")

    frame.bind("<Configure>", lambda event, canvas=canvas: support.on_frame_configure(canvas))

    populate_chats(frame)


def run_update_loop(result_text, root):
    print("TODO call server readMessages")
    response = network.read_messages()
    if response['result'] != "ok":
        result_text.set(
            ''.join(["result= ", response['result']])
        )
        return
    for message in response["messages"]:
        new_message = Message(
            message["from_user_id"],
            network.global_user_id,
            message["message"],
            message["date"],
        )
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''INSERT INTO messages (from_user_id, to_user_id, message, date)
                    VALUES (%s, %s, %s, %s);''',
                    (
                        message['from_user_id'],
                        message['to_user_id'],
                        message['message'],
                        message['date'],
                     )
                )
                connection.commit()

                cursor.execute(
                    '''
                    SELECT id FROM messages
                    WHERE from_user_id = %s
                    AND date = %s;
                    ''',
                    (message["from_user_id"], message['date'])
                )

                new_message_id = cursor.fetchone()[0]

                cursor.execute(
                    '''
                    SELECT * FROM chats
                    WHERE with_user_id = %s;
                    ''',
                    (message["from_user_id"],)
                )
                chat = cursor.fetchone()
                if chat:
                    cursor.execute(
                        '''
                        UPDATE chats
                        SET last_message_id = %s
                        WHERE with_user_id = %s;
                        ''',
                        (new_message_id, message["from_user_id"],)
                    )
                else:
                    cursor.execute(
                        '''
                        INSERT INTO chats (with_user_id, last_message_id)
                        VALUES (%s, %s);
                        ''',
                        (message["from_user_id"], new_message_id)
                    )
                connection.commit()
        print("got new message " + str(new_message.__dict__))

    root.after(3000, run_update_loop, result_text, root)