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

import datetime
import socketserver
from http.server import BaseHTTPRequestHandler
import json
from messenger.common.user import User, AuthTokenManager, RegisteredUsersManager, generate_auth_token
import validators

# registered_users = []  # TODO store users as User objects with login, password, user_id
# auth_token_store = []        # TODO store user's auth_token_store as objects with user_id, auth_token_store {user_id = 10, auth_token_store="fhhhdas123"}
messages = [] # TODO replace with some fancy store\manager class


registered_users = RegisteredUsersManager()
auth_token_store = AuthTokenManager()

#TODO replace self.wfile.write with self.writeResponse(response)

def currentTime():
    return int(datetime.datetime.utcnow().timestamp() * 1000)

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


class GetUser(Response):

    def __init__(self, user_login, avatar, last_active):
        super().__init__("ok")
        self.user_login = user_login
        self.avatar = avatar
        self.last_active = last_active


class ReadMessagesResponse(Response):

    def __init__(self, messages, current_date):
        super().__init__("ok")
        self.messages = messages
        self.current_date = current_date



class ServerHandler(BaseHTTPRequestHandler):

    def get_post_body(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        return (self.rfile.read(content_len)).decode()

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
        post_body = self.get_post_body()
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

        self.writeResponse(Response(("user_registered")))

    def handle_login(self):
        post_body = self.get_post_body()
        login = json.loads(post_body)['login']
        password = json.loads(post_body)['password']
        # TODO check password
        # TODO handle other errors: missing password, missing login, etc...
        if len(login) == 0:
            self.writeResponse(Response("login_is_missing"))
            return
        if len(password) == 0:
            self.writeResponse(Response("password_is_missing"))
            return
        if registered_users.is_login_in_store(login):
            user = registered_users.get_user_by_login(login)
            if not user.check_password(password):
                self.writeResponse(Response("wrong_password"))
                return

            auth_token = generate_auth_token()
            auth_token_store.add_user(user, auth_token)
            self.writeResponse(LoginResponse(user.get_id(), auth_token))
            auth_token_store.show_user_tokens()
            return

        self.writeResponse(Response("unknown_login"))

    def handle_send_message(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        to_user_id = json.loads(post_body)['to_user_id']
        message = json.loads(post_body)['message']
        user = auth_token_store.get_user_by_auth_token(auth_token)
        if user is None:
            self.writeResponse(Response("unknown_auth_token"))
            return

        if not registered_users.is_id_in_store(to_user_id):
            self.writeResponse(Response("user_is_missing"))
            return
        if len(message) == 0:
            self.writeResponse(Response("message_is_missing"))
            return

        sself.writeResponse(Response("message_has_delivered"))

    def handle_read_message(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        since_date = json.loads(post_body)['since_date']

        user = auth_token_store.get_user_by_auth_token(auth_token) # переделать
        ct = currentTime()

        if user is not None:
            user.last_active = ct

        messagesToRead = []
        for m in messages:
            if m.to_user_id == user.user_id and m.date >= since_date:
                messagesToRead.append(m)

        self.writeResponse(ReadMessagesResponse(messagesToRead, ct))

    # setAvatar - set avatar - params: auth_token, avatar_url
    def handle_set_avatar(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        avatar_url = json.loads(post_body)['avatar_url']
        if not auth_token_store.is_token_in_store(auth_token):
            self.writeResponse(Response("unknown_auth_token"))
            return
        if len(avatar_url) == 0:
            self.writeResponse(Response("url_is_missing"))
            return
        if not validators.url(avatar_url):
            self.writeResponse(Response("url_is_not_valid"))
            return
        # http request url
        user_id = auth_token_store.get_user_by_auth_token(auth_token).get_id()
        user = registered_users.get_user_by_id(user_id)
        user.set_avatar(avatar_url)
        self.writeResponse(Response("avatar_has_been_set"))

    # 5) /getUser - get info about user - params: auth_token, user_id
    #             - result: login: String, last_active: Date, avatar_url: String
    def handle_get_user(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        user_id_to_get = json.loads(post_body)['user_id_to_get']
        if not auth_token_store.is_token_in_store(auth_token):
            self.writeResponse(Response("unknown_auth_token"))
            return
        if not registered_users.is_id_in_store(user_id_to_get):
            self.writeResponse(Response("user_is_missing"))
            return
        user = registered_users.get_user_by_id(user_id_to_get)
        last_active = None  # How should it be implemented?

# TODO rewrite response under in class
        self.writeResponse(GetUser(
            user.get_login(), user.get_avatar(), last_active,
        ))


def run_server():
    PORT = 8080

    httpd = socketserver.TCPServer(("", PORT), ServerHandler)
    print("serving at port", PORT)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
