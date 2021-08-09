import sqlite3
import psycopg2


# def create_connection():
#     connection = sqlite3.connect('messenger.db')
#     return

def create_connection():
   # dbName = "clientDb_" + user_id
    connection = psycopg2.connect(
        """
        dbname=messenger_client 
        user=denis 
        password=qwe 
        host=127.0.0.1 
        port=5432
        """
    )
    return connection


def create_tables():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            from_user_id bigint,
            to_user_id bigint,
            message text,
            date numeric
        );''')
    connection.commit()
    cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
            id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            with_user_id bigint UNIQUE,
            last_message_id bigint REFERENCES messages(id)
        );''')
    connection.commit()
    connection.close()
