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

#TODO избегать падений сервера, в случае ошибки обработки запроса - возвращать джсон с резалт = "internal server error"


import datetime
import socketserver
from http.server import BaseHTTPRequestHandler
import json

from messenger.server.messages import Message
from messenger.common.user import User, \
    AuthTokenManager, RegisteredUsersManager, generate_auth_token
import validators
from messenger.common import responses


registered_users = RegisteredUsersManager()
auth_token_store = AuthTokenManager()


def current_time():
    return int(datetime.datetime.utcnow().timestamp() * 1000)


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
        if self.path == "/setAvatar":
            self.handle_set_avatar()

    def handle_register(self):
        print(f'register handle beginning: {current_time()}')
        post_body = self.get_post_body()
        login = json.loads(post_body).get('login')
        password = json.loads(post_body).get('password')
        print(post_body)
        print(f'register post body formed: {current_time()}')
        if login is None or len(login) == 0:
            self.write_response(responses.Response("login_is_missing"))
            return
        if registered_users.is_login_in_store(login):
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
        print(f'register check ended: {current_time()}')
        user = User(login, password)
        print(f'register user add begin: {current_time()}')
        registered_users.add_user(user)
        print(f'register user add and: {current_time()}')
        registered_users.show_users()
        print(f'register show user end: {current_time()}')

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
        if registered_users.is_login_in_store(login):
            user = registered_users.get_user_by_login(login)
            if not user.check_password(password):
                self.write_response(responses.Response("wrong_password"))
                return

            auth_token = generate_auth_token()
            auth_token_store.add_user(user, auth_token)
            self.write_response(
                responses.LoginResponse(user.get_id(), auth_token)
            )
            return

        self.write_response(responses.Response("unknown_login"))

    def handle_send_message(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        #from_user_id = json.loads(post_body)['from_user_id'] # is it right? Or it should be found in user_store?
        to_user_id = json.loads(post_body)['to_user_id']
        message_text = json.loads(post_body)['message']
        from_user = auth_token_store.get_user_by_auth_token(auth_token)
        from_user_id = from_user.get_id()
        if from_user is None:
            self.write_response(responses.Response("unknown_auth_token"))
            return

        if not registered_users.is_id_in_store(to_user_id):
            self.write_response(responses.Response("user_is_missing"))
            return
        if len(message_text) == 0:
            self.write_response(responses.Response("message_is_missing"))
            return
        date = current_time()
        print(date)
        message = Message(from_user_id, to_user_id, message_text, date)
        messages_store.store.append(message)
        print(messages_store.store)
        self.write_response(responses.Response("message_has_delivered"))

    def handle_read_message(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        since_date = json.loads(post_body)['since_date']

        user = auth_token_store.get_user_by_auth_token(auth_token)  # переделать
        var_current_time = current_time()

        if user is None:
            self.write_response(responses.Response("unknown_auth_token"))
            return

        if user is not None:
            user.last_active = var_current_time
        print("handle_read_message user=" + str(user))
        messages_to_read = []
        for message in messages_store.store:
            if message.to_user_id == user.get_id() and \
                    message.date >= since_date:
                messages_to_read.append(message)

        self.write_response(
            responses.ReadMessagesResponse(messages_to_read, var_current_time)
        )

    # setAvatar - set avatar - params: auth_token, avatar_url
    def handle_set_avatar(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        avatar_url = json.loads(post_body)['avatar_url']
        if not auth_token_store.is_token_in_store(auth_token):
            self.write_response(responses.Response("unknown_auth_token"))
            return
        if len(avatar_url) == 0:
            self.write_response(responses.Response("url_is_missing"))
            return
        if not validators.url(avatar_url):
            self.write_response(responses.Response("url_is_not_valid"))
            return
        # http request url
        user_id = auth_token_store.get_user_by_auth_token(auth_token).get_id()
        user = registered_users.get_user_by_id(user_id)
        user.set_avatar(avatar_url)
        self.write_response(responses.Response("avatar_has_been_set"))

    def handle_get_user(self):
        post_body = self.get_post_body()
        auth_token = json.loads(post_body)['auth_token']
        user_id_to_get = json.loads(post_body)['user_id_to_get']
        if not auth_token_store.is_token_in_store(auth_token):
            self.write_response(responses.Response("unknown_auth_token"))
            return
        if not registered_users.is_id_in_store(user_id_to_get):
            self.write_response(responses.Response("user_is_missing"))
            return
        user = registered_users.get_user_by_id(user_id_to_get)
        last_active = None  # How should it be implemented?

        self.write_response(responses.GetUserResponse(
            user.get_login(), user.get_avatar(), last_active,
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
