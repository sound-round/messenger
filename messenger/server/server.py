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


import datetime
import socketserver
from http.server import BaseHTTPRequestHandler
import json

from messenger.server.messages import Message
from messenger.common.user import generate_auth_token, AuthToken, User
#from messenger.common.user import User#, \
 #   AuthTokenManager, RegisteredUsersManager, generate_auth_token
import validators
from messenger.common import responses
import psycopg2
import psycopg2.extras
import sqlalchemy as sa
from sqlalchemy.orm import mapper, relationship, sessionmaker


engine = sa.create_engine('postgresql+psycopg2://denis:qwe@127.0.0.1/messenger')
meta = sa.MetaData(engine)
#TODO Column('right_id', Integer, ForeignKey('right.id') if it nessasary
registered_users = sa.Table('registered_users', meta,  sa.Column("id", sa.BigInteger, primary_key=True), autoload=True)
auth_token_manager = sa.Table('auth_tokens', meta, sa.Column("id", sa.BigInteger, primary_key=True), autoload=True)
mapper(User, registered_users, allow_partial_pks=True)
mapper(AuthToken, auth_token_manager)
db_session = sessionmaker(bind=engine)
db_session.configure()
print("Database opened successfully")


def current_time():
    return int(datetime.datetime.utcnow().timestamp() * 1000)

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

    def do_POST(self):  # noqa: C901
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


        session = db_session()
        SQL_response = session.query(User).filter(User.login == login).first()
        if SQL_response:
            self.write_response(responses.Response("user_already_registered"))
            return
        if len(password) == 0:
            self.write_response(responses.Response("password_is_missing"))
            return
        if len(password) < 6:
            self.write_response(responses.Response(
                "password_must_be_6_or_more_characters_long"
            ))
            return
        user = User(login, password)
        session.add(user)
        session.commit()
        session.close()

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

        session = db_session()
        user = session.query(User).filter(User.login == login).first()
        if not user:
            self.write_response(responses.Response("unknown_login"))
        if user.password != password:
            self.write_response(responses.Response("wrong_password"))
            return

        user_auth_token = AuthToken(user.id, generate_auth_token())
        session.add(user_auth_token)
        session.commit()
        self.write_response(
            responses.LoginResponse(user.id, user_auth_token.auth_token)
        )
        session.close()
        return


    def handle_send_message(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']

        to_user_id = json.loads(post_body)['to_user_id']
        message_text = json.loads(post_body)['message']

        session = db_session()
        from_user = session.query(
            User, AuthToken
        ).filter(
            registered_users.c.id == auth_token_manager.c.user_id
        ).filter(auth_token_manager.c.auth_token == auth_token).first()

        if from_user is None:
            self.write_response(responses.Response("unknown_auth_token"))
            return
        if not to_user_id:
            self.write_response(responses.Response("user_is_missing"))
            return

        to_user = session.query(User).filter(registered_users.c.id == to_user_id).first()
        if not to_user:
            self.write_response(responses.Response("user_is_not_found"))
            return
        if len(message_text) == 0:
            self.write_response(responses.Response("message_is_missing"))
            return
        timestamp_date = current_time()
        date = convert_date(timestamp_date)
        message = Message(from_user.User.id, to_user.id, message_text, date)
        messages_store.store.append(message)
        session.commit()
        session.close()
        self.write_response(responses.Response("message_has_delivered"))


    def handle_read_message(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        since_date = json.loads(post_body)['since_date']

        session = db_session()
        user = session.query(
            User, AuthToken
        ).filter(
            registered_users.c.id == auth_token_manager.c.user_id
        ).filter(auth_token_manager.c.auth_token == auth_token).first()

        if not user:
            self.write_response(responses.Response("unknown_auth_token"))
            return
        var_current_time = current_time()
        user.User.last_active = convert_date(var_current_time)
        session.add(user.User)
        session.commit()
        messages_to_read = []
        since_date = convert_date(since_date)
        for message in messages_store.store:
            if message.to_user_id == user.User.id and \
                    message.date >= since_date:
                messages_to_read.append(message)
        session.close()
        self.write_response(
            responses.ReadMessagesResponse(messages_to_read, var_current_time)
        )

    # setAvatar - set avatar - params: auth_token, avatar_url
    def handle_set_avatar(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        avatar_url = json.loads(post_body)['avatar_url']

        session = db_session()
        user = session.query(
            User, AuthToken
        ).filter(
            registered_users.c.id == auth_token_manager.c.user_id
        ).filter(auth_token_manager.c.auth_token == auth_token).first()
        if not user:
            self.write_response(responses.Response("unknown_auth_token"))
            return
        if len(avatar_url) == 0:
            self.write_response(responses.Response("url_is_missing"))
            return
        if not validators.url(avatar_url):
            self.write_response(responses.Response("url_is_not_valid"))
            return

        user.User.avatar_url = avatar_url
        session.commit()
        session.close()
        self.write_response(responses.Response("avatar_has_been_set"))

    def handle_get_user(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        user_id_to_get = json.loads(post_body)['user_id_to_get']
        session = db_session()
        user = session.query(
            User, AuthToken
        ).filter(
            registered_users.c.id == auth_token_manager.c.user_id
        ).filter(auth_token_manager.c.auth_token == auth_token).first()
        if not user:
            self.write_response(responses.Response("unknown_auth_token"))
            return
        user_to_get = session.query(User).filter(registered_users.c.id == user_id_to_get).first()
        if not user_to_get:
            self.write_response(responses.Response("user_is_missing"))
            return

        self.write_response(responses.GetUserResponse(
            user_to_get.login,
            user_to_get.avatar_url,
            datetime.datetime.timestamp(user_to_get.last_active),
        ))

    #TODO find out if it is nessasary
    def handle_find_user_id(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        login = json.loads(post_body)['user_login_to_get']
        if not auth_token_store.is_token_in_store(auth_token):
            self.write_response(responses.Response("unknown_auth_token"))
            return
        if not registered_users.is_login_in_store(login):
            self.write_response(responses.Response("user_is_missing"))
            return
        user = registered_users.get_user_by_login(login)

        self.write_response(responses.FindUserIDResponse(
            user.get_id(),
        ))


class MessagesStore:
    store = []


messages_store = MessagesStore()


def run_server():
    PORT = 8080

    httpd = socketserver.TCPServer(("", PORT), ServerHandler)
    print("serving at port", PORT)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
