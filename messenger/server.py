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
from messenger.user import User, AuthToken, RegisteredUsers, generate_auth_token


#registered_users = []  # TODO store users as User objects with login, password, user_id
#auth_token_store = []        # TODO store user's auth_token_store as objects with user_id, auth_token_store {user_id = 10, auth_token_store="fhhhdas123"}

registered_users = RegisteredUsers()
auth_token_store = AuthToken()


class ServerHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == "/register":
            self.handle_register()
        if self.path == "/login":
            self.handle_login()
        if self.path == "/sendMessage":
            self.handle_send_message()
        if self.path == "/readMessage":
            self.handle_read_message()

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
            self.wfile.write(str.encode("{\"result\" : \"please, enter your login\"}"))
            return
        if registered_users.is_login_in_store(login):
            self.wfile.write(str.encode("{\"result\" : \"user_already_registered\"}"))
            return
        if len(password) == 0:
            self.wfile.write(str.encode("{\"result\" : \"please, enter your password\"}"))
            return
        if len(password) < 6:
            self.wfile.write(str.encode("{\"result\" : \"password must be 6 or more characters long\"}"))
            return
        user = User(login, password)
        #print('login: {}'.format(user.get_login()))
        #print('password: {}'.format(user.get_password()))
        #print('user_id: {}'.format(user.get_id()))
        # TODO store users as objects with login, user_id, password etc..

        registered_users.add_user(user)
        registered_users.show_users()

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
        if len(login) == 0:
            self.wfile.write(str.encode("{\"result\" : \"please, enter your login\"}"))
            return
        if len(password) == 0:
            self.wfile.write(str.encode("{\"result\" : \"please, enter your password\"}"))
            return
        if registered_users.is_login_in_store(login):
            user = registered_users.get_user(login)
            if not user.check_password(password):
                self.wfile.write(str.encode("{\"result\" : \"wrong password\"}"))
                return

            auth_token = generate_auth_token()
            auth_token_store.add_user(user, auth_token)
            self.wfile.write(str.encode(
                "\"result\" : \"ok\", \"user_id\" : {}, \"auth_token\" : \" {} \"".format(
                user.get_id(), auth_token
            )))
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
        to_user_id = json.loads(post_body)['to_user_id'] # checking have to be done on the client-side? Why not?
        message = json.loads(post_body)['message']
        if not auth_token_store.is_token_in_store(auth_token):
            self.wfile.write(str.encode(
                "{\"result\" : \"please, register your account\"}"
            ))
            return
        if not registered_users.is_id_in_store(to_user_id):
            self.wfile.write(str.encode(
                "{\"result\" : \"user you have tried to send a message isn't registered\"}"
            ))
            return
        if len(message) == 0:
            self.wfile.write(str.encode("{\"result\" : \"please, enter your message\"}"))
            return


        self.wfile.write(str.encode("{\"result\" : \"message has delivered\"}"))

    def handle_read_message(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        auth_token = json.loads(post_body)['auth_token']
        to_user_id = json.loads(post_body)['to_user_id']  # check have to be done on the client-side? Why not?
        message = json.loads(post_body)['message']
        if len(message) == 0:
            self.wfile.write(str.encode("{\"result\" : \"please, enter your message\"}"))
            return
        if not registered_users.is_id_in_store(to_user_id):
            self.wfile.write(str.encode(
                "{\"result\" : \"user you have tried to send a message isn't registered\"}"
            ))
            return
        if not auth_token_store.is_token_in_store(auth_token):
            self.wfile.write(str.encode(
                "{\"result\" : \"please, register your account\"}"
            ))
            return

        self.wfile.write(str.encode("{\"result\" : \"message has delivered\"}"))


def run_server():

    PORT = 8080

    httpd = socketserver.TCPServer(("", PORT), ServerHandler)
    print("serving at port", PORT)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
