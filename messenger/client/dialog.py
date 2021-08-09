import tkinter as tk
from tkinter import StringVar
from messenger.client import network
from messenger.server.messages import Message
import datetime
from messenger.client import support, chats_menu
from messenger.client.sql import create_connection, create_tables


def current_time():
    return datetime.datetime.utcnow().timestamp() * 1000


class Chat:
    def __init__(self, with_user_id, messages):
        self.with_user_id = with_user_id
        self.messages = messages  # TODO CHECK: list is required


def get_chat(with_user_id):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM messages
                WHERE from_user_id = %s
                OR to_user_id = %s;
                """,
                (with_user_id, with_user_id)
            )
            messages = cursor.fetchall()
            final_messages = []
            for message in messages:
                formatted_message = Message(
                    message[1], message[2], message[3], message[4],
                )
                final_messages.append(formatted_message)
            return Chat(with_user_id, final_messages)


def populate_dialog(frame, chat, root):
    if not frame.winfo_exists():
        return
    support.remove_all(frame)
    row = 0
    if chat:
        for message in chat.messages:  # TODO this [OK]
            message_text = str(message.from_user_id) + ": " + message.message + " " + str(message.date)
            tk.Label(frame, text=message_text).grid(row=row, column=0)
            row = row + 1

    root.after(3000, populate_dialog, frame, chat, root)


def return_to_chats(root):
    support.remove_all(root)
    chats_menu.display_chats_ui(root)


def open_dialog(root, entry):
    result_text = StringVar()
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
    print('with_user_id:', with_user_id)
    chat = get_chat(with_user_id)  # TODO this [OK]

    support.remove_all(root)

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

        with create_connection() as connection:
            with connection.cursor() as cursor:
                date = current_time()
                cursor.execute(
                    '''
                    INSERT INTO messages (from_user_id, to_user_id, message, date)
                    VALUES (%s, %s, %s, %s);
                    ''',
                    (
                        network.global_user_id,
                        to_user_id,
                        message_to_send,
                        date,
                    )
                )
                connection.commit()

                cursor.execute(
                    '''
                    SELECT id FROM messages
                    WHERE from_user_id = %s
                    AND date = %s;
                    ''',
                    (network.global_user_id, date)
                )

                new_message_id = cursor.fetchone()[0]

                cursor.execute(
                    '''
                    SELECT * FROM chats
                    WHERE with_user_id = %s;
                    ''',
                    (to_user_id,)
                )
                chat = cursor.fetchone()
                if chat:
                    cursor.execute(
                        '''
                        UPDATE chats
                        SET last_message_id = %s
                        WHERE with_user_id = %s;
                        ''',
                        (new_message_id, to_user_id)
                    )
                else:
                    cursor.execute(
                        '''
                        INSERT INTO chats
                        VALUES (with_user_id, last_message_id);
                        ''',
                        (to_user_id, new_message_id)
                    )
                connection.commit()

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
                        command=lambda: return_to_chats(root))
    back_button.place(x=220, y=525, width=50, height=25)

    chat_canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
    chat_frame = tk.Frame(chat_canvas, background="#ffffff")
    chat_scroll_bar = tk.Scrollbar(root, orient="vertical", command=chat_canvas.yview)
    chat_canvas.configure(yscrollcommand=chat_scroll_bar.set)
    chat_scroll_bar.place(x=300, y=25, width=20, height=440)
    chat_canvas.place(x=0, y=25, width=300, height=440)
    chat_canvas.create_window((4, 4), window=chat_frame, anchor="nw")
    chat_frame.bind(
        "<Configure>",
        lambda event,
        canvas=chat_canvas: support.on_frame_configure(chat_canvas),
    )

    populate_dialog(chat_frame, chat, root)
