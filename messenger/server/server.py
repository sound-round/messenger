# tech topics: HTTP (POST request), JSON (http request\response body), ports, python: SimpleHttpServer

# server methods:
# 1) /register - register new user - params: login, password
# 2) /login - login as some user - params: login, password - result: user_id, auth_token
# 3) /sendMessage  - send message to some user - params: auth_token, to_user_id, message: String
# 4) /readMessages - receive messages since date (polling), should be called each 1sec
#                  - params: auth_token, since_date
#                  - result: messages:[Message(message: String, date: Date, from_user_id: Int)], current_time:Date
#                  - additionally updates last_active value for user
# 5) /getUser - get info about user - params: auth_token, user_id
#             - result: login: String, last_active: Date, avatar_url: String
# 6) /getUserByLogin - get info about user - params: auth_token, login,
#             - result: login: String, last_active: Date, avatar_url: String, user_id: String
# 7) /setAvatar - set avatar - params: auth_token, avatar_url
#
# Data types:
# Date - unix time in milliseconds integer

#TODO high priority: use sqlite for storage on both server and client
#TODO add expiring for auth_token
#TODO low priority: create html+javascript (webstorm ide) client?

import decimal
import datetime
import socketserver
from http.server import BaseHTTPRequestHandler
import json

from messenger.server.messages import Message
from messenger.common.user import generate_auth_token, AuthToken, User
import validators
from messenger.common import responses
from messenger.server import sql
# import sqlalchemy as sa
# from sqlalchemy.orm import mapper, relationship, sessionmaker


'''engine = sa.create_engine('postgresql+psycopg2://denis:qwe@127.0.0.1/messenger')
meta = sa.MetaData(engine)
#todo Column('right_id', Integer, ForeignKey('right.id') if it nessasary
users = sa.Table(
    'users', meta, sa.Column(
        "id", sa.BigInteger, primary_key=True
    ), autoload=True
)
auth_token_manager = sa.Table(
    'auth_tokens', meta, sa.Column(
        "id", sa.BigInteger, primary_key=True
    ), autoload=True
)
messages = sa.Table(
    'messages', meta, sa.Column(
        "id", sa.BigInteger, primary_key=True
    ), autoload=True
)
mapper(User, users)
mapper(AuthToken, auth_token_manager)
mapper(Message, messages)
db_session = sessionmaker(bind=engine)
db_session.configure()
print("Database opened successfully")'''


# def create_connection():
#     connection = psycopg2.connect(
#         """
#         dbname=messenger
#         user=denis
#         password=qwe
#         host=127.0.0.1
#         port=5432
#         """
#     )
#     return connection


def object_to_list(object_):
    lines = []
    for row in object_:
        print(f'row: {vars(row)}')
        lines.append(vars(row))
    return lines


def current_time():
    return datetime.datetime.utcnow().timestamp() * 1000


def convert_date(time):
    time /= 1000
    return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')


class ServerHandler(BaseHTTPRequestHandler):

    def get_post_body(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        return (self.rfile.read(content_len)).decode()

    def write_response(self, response):
        self.wfile.write(str.encode(responses.toJSON(response)))

    def do_POST(self):  # noqa: C901 # TODO how does it work?
        if self.path == "/register":
            self.handle_register()
        if self.path == "/login":
            self.handle_login()
        if self.path == "/sendMessage":
            self.handle_send_message()
        if self.path == "/readMessages":
            self.handle_read_message()
        if self.path == "/getUser":
            self.handle_get_user()
        if self.path == "/findUserId":
            self.handle_find_user_id()
        if self.path == "/setAvatar":
            self.handle_set_avatar()

    def handle_register(self):
        post_body = self.get_post_body()
        login = json.loads(post_body).get('login')
        password = json.loads(post_body).get('password')
        print(f'post body: {post_body}')

        if login is None or len(login) == 0:
            self.write_response(responses.Response("login_is_missing"))
            return

        user = sql.get_user(login)
        print('user:', user)
        if user:
            self.write_response(responses.Response("user_is_already_registered"))
            return
        if len(password) == 0:
            self.write_response(responses.Response("password_is_missing"))
            return
        if len(password) < 6:
            self.write_response(responses.Response(
                "password_must_be_6_or_more_characters_long"
            ))
            return
        sql.register_user(login, password)

        self.write_response(responses.Response("user_registered"))

    def handle_login(self):
        post_body = self.get_post_body()
        login = json.loads(post_body)['login']
        password = json.loads(post_body)['password']
        if len(login) == 0:
            self.write_response(responses.Response("login_is_missing"))
            return
        if len(password) == 0:
            self.write_response(responses.Response("password_is_missing"))
            return

        user = sql.get_user(login)
        if not user:
            self.write_response(responses.Response("unknown_login"))
            return
        print('SQL_user:', user)
        user_password = user[2]
        if user_password != password:
            self.write_response(responses.Response("wrong_password"))
            return

        user_id = user[0]
        user_last_active = user[4]
        user_auth_token = generate_auth_token()
        sql.create_auth_token(user_id, user_auth_token)
        self.write_response(
            responses.LoginResponse(user_id, user_auth_token, float(user_last_active))
        )
        return

    def handle_send_message(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']

        to_user_id = json.loads(post_body)['to_user_id']
        message_text = json.loads(post_body)['message']

        from_user_id = sql.get_user_id(auth_token)
        if from_user_id is None:
            self.write_response(responses.Response("unknown_auth_token"))
            return
        if not to_user_id:
            self.write_response(responses.Response("user_is_missing"))
            return

        if len(message_text) == 0:
            self.write_response(responses.Response("message_is_missing"))
            return
        #timestamp_date = current_time()
        date = current_time()  #convert_date(timestamp_date)
        sql.add_message(from_user_id, to_user_id, message_text, date)

        self.write_response(responses.Response("message_has_delivered"))

    def handle_read_message(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        since_date = json.loads(post_body)['since_date']

        user = sql.get_user_by_auth_token(auth_token)
        if not user:
            self.write_response(responses.Response("unknown_auth_token"))
            return
        #var_current_time = current_time()
        cur_time = current_time()  #convert_date(var_current_time)
        user_id = user[0]
        sql.update_last_active(cur_time, user_id)

        messages = sql.get_messages(user_id, since_date)
        messages_to_read = []
        for message in messages:
            new_message = Message(
                message[1],
                message[2],
                message[3],
                float(message[4]),
            )
            messages_to_read.append(new_message)

        self.write_response(
            responses.ReadMessagesResponse(
                messages_to_read, float(cur_time)
            )
        )

    # setAvatar - set avatar - params: auth_token, avatar_url
    def handle_set_avatar(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        avatar_url = json.loads(post_body)['avatar_url']

        user = sql.get_user_by_auth_token(auth_token)
        if not user:
            self.write_response(responses.Response("unknown_auth_token"))
            return
        if len(avatar_url) == 0:
            self.write_response(responses.Response("url_is_missing"))
            return
        if not validators.url(avatar_url):
            self.write_response(responses.Response("url_is_not_valid"))
            return
        user_id = user[0]
        sql.set_avatar(avatar_url, user_id)
        self.write_response(responses.Response("avatar_has_been_set"))

    def handle_get_user(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        user_id_to_get = json.loads(post_body)['user_id_to_get']

        user_id = sql.get_user_by_auth_token(auth_token)  # TODO ask if it is needed
        if not user_id:
            self.write_response(responses.Response("unknown_auth_token"))
            return

        user_to_get = sql.get_user_by_id(user_id_to_get)
        if not user_to_get:
            self.write_response(responses.Response("user_is_missing"))
            return
        user_to_get_login = user_to_get[1]
        user_to_get_avatar_url = user_to_get[3]
        user_to_get_last_active = user_to_get[4]
        self.write_response(responses.GetUserResponse(
            user_to_get_login,
            user_to_get_avatar_url,
            float(user_to_get_last_active),
        ))

    def handle_find_user_id(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        login = json.loads(post_body)['user_login_to_get']

        user_id = sql.get_user_by_auth_token(auth_token)  # TODO ask if it is needed
        if not user_id:
            self.write_response(responses.Response("unknown_auth_token"))
            return

        user_to_find = sql.get_user(login)
        if not user_to_find:
            self.write_response(responses.Response("user_is_missing"))
            return
        user_to_find_id = user_to_find[0]
        self.write_response(responses.FindUserIDResponse(
            user_to_find_id,
        ))


def run_server():
    PORT = 8080

    httpd = socketserver.TCPServer(("", PORT), ServerHandler)
    print("serving at port", PORT)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
