# tech topics: HTTP (POST request), JSON, ports, python: SimpleHttpServer

# server methods:
# 1) /register - register new user - params: login, password
# 2) /login - login as some user - params: login, password - result: user_id, auth_token
# 3) /sendMessage  - send message to some user - params: auth_token, to_user_id, message: String
# 4) /readMessages - receive messages since date (polling), should be called each 1sec
#                  - params: auth_token, since_date
#                  - result: list of Message(message: String, date: Date, from_user_id: Int)
# 5) /getUser - get info about user - params: auth_token, user_id
#             - result: login: String, last_active: Date, avatar_url: String
# 6) /setAvatar - set avatar - params: auth_token, avatar_url

import http.server
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid
import secrets
import copy


#registered_users = []  # TODO store users as User objects with login, password, user_id
#auth_token = []        # TODO store user's auth_token as objects with user_id, auth_token {user_id = 10, auth_token="fhhhdas123"}


class RegisteredUsers:
    store = []

    def add_user(self, user):
        self.store.append(user)

    def show_users(self):
        print('Registered users:')
        for user in self.store:
            print('login: {}'.format(user.get_login()))

    def check_login_in_store(self, login):
        for user in self.store:
            if user.get_login() == login:
                return True


class AuthToken:

    store = []
    def add_user(self, current_user):
        user = copy.deepcopy(current_user)
        auth_token = generate_auth_token()
        user.auth_token = []
        user.auth_token.append(auth_token)
        print('user_auth_token_added: {}'.format(user.auth_token))
        delattr(user, 'login')
        delattr(user, 'password')
        self.store.append(user)

    def add_token_to_user(self, current_user):
        for user in self.store:
            if user.get_user_id() == current_user.get_user_id():
                new_auth_token = generate_auth_token()
                user.auth_token.append(new_auth_token)

    def get_tokens(self, current_user):
        for user in self.store:
            if user.get_user_id() == current_user.get_user_id():
                return user.auth_token

    def show_user_tokens(self):
        for user in self.store:
            print('user_id: {}'.format(user.get_user_id()))
            print('user_auth_tokens: {}'.format(auth_token.get_tokens(user)))

class User:

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.user_id = generate_user_id()

    def get_login(self):
        return self.login

    def set_login(self, new_login):
        self.login = new_login

    def get_password(self):
        return self.password

    def set_password(self, new_password):
        self.password = new_password

    def get_user_id(self):
        return self.user_id


def generate_user_id():
    return uuid.uuid4()


def generate_auth_token():
    return secrets.token_urlsafe()


registered_users = RegisteredUsers()
auth_token = AuthToken()


class ServerHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == "/register":
            self.handle_register()
        if self.path == "/login":
            self.handle_login()
        if self.path == "/sendMessage":
            self.handle_send_message()

    def handle_register(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        login = json.loads(post_body).get('login')
        password = json.loads(post_body).get('password')
        print(post_body)
        user = User(login, password)
        # TODO handle other errors: missing password, missing login, etc...
        if user.get_login() is None:
            self.wfile.write(str.encode("{\"result\" : \"please, enter your login\"}"))
            return
        if registered_users.check_login_in_store(user.get_login()):
            self.wfile.write(str.encode("{\"result\" : \"user_already_registered\"}"))
            return
        if user.get_password() is None:
            self.wfile.write(str.encode("{\"result\" : \"please, enter your password\"}"))
            return
        if len(user.get_password()) < 6:
            self.wfile.write(str.encode("{\"result\" : \"password must be 6 or more characters long\"}"))
            return

        print('login: {}'.format(user.get_login()))
        print('password: {}'.format(user.get_password()))
        print('user_id: {}'.format(user.get_user_id()))
        # TODO store users as objects with login, user_id, password etc..

        registered_users.add_user(user)
        auth_token.add_user(user)
        registered_users.show_users()
        auth_token.show_user_tokens()

        self.wfile.write(str.encode("{\"result\" : \"user registered\"}"))

    def handle_login(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        login = json.loads(post_body)['login']
        password = json.loads(post_body)['password']
        # TODO check password
        # TODO handle other errors: missing password, missing login, etc...
        if login in registered_users:
            auth_token = "TODO generate token"
            self.wfile.write(str.encode("{\"result\" : \"ok\", \"user_id\": 1337, \"auth_token\" : \"" + auth_token + "\"}"))
            return

        self.wfile.write(str.encode("{\"result\" : \"unknown_login\"}"))

    def handle_send_message(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()

        self.wfile.write(str.encode("{\"result\" : \"not_implemented\"}"))


def run_server():

    PORT = 8080

    httpd = socketserver.TCPServer(("", PORT), ServerHandler)
    print("serving at port", PORT)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
