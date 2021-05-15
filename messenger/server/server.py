# tech topics: HTTP (POST request), JSON (http request\response body), ports, python: SimpleHttpServer

# server methods:
# 1) /register - register new user - params: login, password
# 2) /login - login as some user - params: login, password - result: user_id, auth_token
# 3) /sendMessage  - send message to some user - params: auth_token, to_user_id, message: String
# 4) /readMessages - receive messages since date (polling), should be called each 1sec
#                  - params: auth_token, since_date
#                  - result: list of Message(message: String, date: Date, from_user_id: Int)
# 5) /getUser - get info about user - params: auth_token, user_id
#             - result: login: String, last_active: Date, avatar_url: String
# 6) /getUserByLogin - get info about user - params: auth_token, login,
#             - result: login: String, last_active: Date, avatar_url: String, user_id: String
# 7) /setAvatar - set avatar - params: auth_token, avatar_url

import socketserver
from http.server import BaseHTTPRequestHandler
import json
from messenger.common.user import User, AuthTokenManager, RegisteredUsersManager, generate_auth_token
import validators

# registered_users = []  # TODO store users as User objects with login, password, user_id
# auth_token_store = []        # TODO store user's auth_token_store as objects with user_id, auth_token_store {user_id = 10, auth_token_store="fhhhdas123"}

registered_users = RegisteredUsersManager()
auth_token_store = AuthTokenManager()


# TODO extract to separate file
class Response(object):
    result = "ok"

    def __init__(self, result):
        self.result = result


def toJSON(object):
    return json.dumps(object, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)


class LoginResponse(Response):

    def __init__(self, user_id, auth_token):
        super().__init__("ok")
        self.user_id = user_id
        self.auth_token = auth_token


class ServerHandler(BaseHTTPRequestHandler):

    def writeResponse(self, response):
        self.wfile.write(str.encode(toJSON(response)))

    def do_POST(self):
        if self.path == "/register":
            self.handle_register()
        if self.path == "/login":
            self.handle_login()
        if self.path == "/sendMessage":
            self.handle_send_message()
        if self.path == "/readMessage":
            self.handle_read_message()
        if self.path == "/getUser":
            self.handle_get_user()
        if self.path == "/setAvatar":
            self.handle_set_avatar()

    def handle_register(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        login = json.loads(post_body).get('login')
        password = json.loads(post_body).get('password')
        print(post_body)

        # TODO handle other errors: missing password, missing login, etc...
        if len(login) == 0:
            self.writeResponse(Response("login_is_missing"))
            return
        if registered_users.is_login_in_store(login):
            self.writeResponse(Response("user_already_registered"))
            return
        if len(password) == 0:
            self.writeResponse(Response("password_is_missing"))
            return
        if len(password) < 6:
            self.writeResponse(Response("password_must_be_6_or_more_characters_long"))
            return
        user = User(login, password)
        # print('login: {}'.format(user.get_login()))
        # print('password: {}'.format(user.get_password()))
        # print('user_id: {}'.format(user.get_id()))
        # TODO store users as objects with login, user_id, password etc..

        registered_users.add_user(user)
        registered_users.show_users()

        self.wfile.write(str.encode("{\"result\" : \"user_registered\"}"))

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
        if len(login) == 0:
            self.wfile.write(str.encode("{\"result\" : \"login_is_missing\"}"))
            return
        if len(password) == 0:
            self.wfile.write(str.encode("{\"result\" : \"password_is_missing\"}"))
            return
        if registered_users.is_login_in_store(login):
            user = registered_users.get_user_by_login(login)
            if not user.check_password(password):
                self.wfile.write(str.encode("{\"result\" : \"wrong_password\"}"))
                return

            auth_token = generate_auth_token()
            auth_token_store.add_user(user, auth_token)
            self.writeResponse(LoginResponse(user.get_id(), auth_token))
            auth_token_store.show_user_tokens()
            return

        self.wfile.write(str.encode("{\"result\" : \"unknown_login\"}"))

    def handle_send_message(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        auth_token = json.loads(post_body)['auth_token']
        to_user_id = json.loads(post_body)['to_user_id']
        message = json.loads(post_body)['message']
        if not auth_token_store.is_token_in_store(auth_token):
            self.wfile.write(str.encode(
                "{\"result\" : \"unknown_auth_token\"}"
            ))
            return
        if not registered_users.is_id_in_store(to_user_id):
            self.wfile.write(str.encode(
                "{\"result\" : \"user_is_missing\"}"
            ))
            return
        if len(message) == 0:
            self.wfile.write(str.encode("{\"result\" : \"message_is_missing\"}"))
            return

        self.wfile.write(str.encode("{\"result\" : \"message_has_delivered\"}"))

    def handle_read_message(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        since_date = json.loads(post_body)['auth_token']
        message = json.loads(post_body)['message']

        self.wfile.write(str.encode("{\"result\" : \"not implemented\"}"))

    # setAvatar - set avatar - params: auth_token, avatar_url
    def handle_set_avatar(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        auth_token = json.loads(post_body)['auth_token']
        avatar_url = json.loads(post_body)['avatar_url']
        if not auth_token_store.is_token_in_store(auth_token):
            self.wfile.write(str.encode(
                "{\"result\" : \"unknown_auth_token\"}"
            ))
            return
        if len(avatar_url) == 0:
            self.wfile.write(str.encode("{\"result\" : \"url_is_missing\"}"))
            return
        if not validators.url(avatar_url):
            self.wfile.write(str.encode("{\"result\" : \"url_is_not_valid\"}"))
            return
        # http request url
        user_id = auth_token_store.get_user_by_auth_token(auth_token).get_id()
        user = registered_users.get_user_by_id(user_id)
        user.set_avatar(avatar_url)
        self.wfile.write(str.encode("{\"result\" : \"avatar_has_been_set\"}"))

    # 5) /getUser - get info about user - params: auth_token, user_id
    #             - result: login: String, last_active: Date, avatar_url: String
    def handle_get_user(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        auth_token = json.loads(post_body)['auth_token']
        user_id_to_get = json.loads(post_body)['user_id_to_get']
        if not auth_token_store.is_token_in_store(auth_token):
            self.wfile.write(str.encode(
                "{\"result\" : \"unknown_auth_token\"}"
            ))
            return
        if not registered_users.is_id_in_store(user_id_to_get):
            self.wfile.write(str.encode(
                "{\"result\" : \"user_is_missing\"}"
            ))
            return
        user = registered_users.get_user_by_id(user_id_to_get)
        last_active = None  # How should it be implemented?

        self.wfile.write(str.encode(
            "\"result\" :\n \"Login: {}\nLast active: {}\nAvatar url: {}\"".format(
                user.get_login(), last_active, user.get_avatar(),
            )
        ))


def run_server():
    PORT = 8080

    httpd = socketserver.TCPServer(("", PORT), ServerHandler)
    print("serving at port", PORT)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
