import psycopg2
import psycopg2.extras


def create_connection():
    connection = psycopg2.connect(
        """
        dbname=messenger 
        user=denis 
        password=qwe 
        host=127.0.0.1 
        port=5432
        """
    )
    return connection


def get_user(login):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE login = %s;', (login,))
            return cursor.fetchone()


def register_user(login, password):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users (login, password) VALUES (%s, %s);',
                (login, password),
            )
            connection.commit()


def create_auth_token(user_id, user_auth_token):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO auth_tokens (user_id, auth_token) 
                VALUES (%s, %s);
                """,
                (user_id, user_auth_token)
            )
            connection.commit()


def get_user_by_auth_token(auth_token):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT users.id
                FROM users JOIN auth_tokens 
                ON users.id = auth_tokens.user_id
                WHERE auth_tokens.auth_token = %s;
                """,
                (auth_token,)
            )
            return cursor.fetchone()


def add_message(from_user_id, to_user_id, message_text, date):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """          
                INSERT INTO messages (from_user_id, to_user_id, message, date)    
                VALUES (%s, %s, %s, %s)
                """,
                (from_user_id, to_user_id, message_text, date)
            )
            connection.commit()


def update_last_active(cur_time, user_id):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET last_active = %s
                WHERE id = %s
                """, (cur_time, user_id))
            connection.commit()


def get_messages(user_id, since_date):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM messages
                WHERE to_user_id = %s
                AND date >= %s;
                """,
                (user_id, since_date)
            )
            return cursor.fetchall()


def set_avatar(avatar_url, user_id):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE users
                SET avatar_url = %s
                WHERE id = %s
                ''',
                (avatar_url, user_id),
            )
            connection.commit()


def get_user_by_id(user_id_to_get):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT * 
                FROM users
                WHERE id = %s;
                ''',
                (user_id_to_get,)
            )
            return cursor.fetchone()