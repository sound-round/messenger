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


def get_chats():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT * FROM chats;
                '''
            )
            chats = cursor.fetchall()

            return chats


def get_last_message_text(last_message_id):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT message FROM messages
                WHERE id = %s;
                ''',
                (last_message_id,)
            )
            last_message_text = cursor.fetchone()[0]
            return last_message_text


def add_message(
    from_user_id, to_user_id, message, date
):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO messages (from_user_id, to_user_id, message, date)
                VALUES (%s, %s, %s, %s);''',
                (
                    from_user_id, to_user_id, message, date
                )
            )
            connection.commit()

            cursor.execute(
                '''
                SELECT id FROM messages
                WHERE from_user_id = %s
                AND date = %s;
                ''',
                (from_user_id, date)
            )

            new_message_id = cursor.fetchone()[0]

            cursor.execute(
                '''
                SELECT * FROM chats
                WHERE with_user_id = %s;
                ''',
                (from_user_id,)
            )
            chat = cursor.fetchone()
            if chat:
                cursor.execute(
                    '''
                    UPDATE chats
                    SET last_message_id = %s
                    WHERE with_user_id = %s;
                    ''',
                    (new_message_id, from_user_id)
                )
            else:
                cursor.execute(
                    '''
                    INSERT INTO chats (with_user_id, last_message_id)
                    VALUES (%s, %s);
                    ''',
                    (from_user_id, new_message_id)
                )
            connection.commit()
