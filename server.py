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


registeredUsers = []  # TODO store users as User objects with login, password, user_id
authToken = []        # TODO store user's auth_token as objects with user_id, auth_token {user_id = 10, auth_token="fhhhdas123"}

class ServerHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == "/register":
            self.handleRegister()
        if self.path == "/login":
            self.handleLogin()
        if self.path == "/sendMessage":
            self.handleSendMessage()

    def handleRegister(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        login = json.loads(post_body)['login']
        print(post_body)
        print(login)
        # TODO handle other errors: missing password, missing login, etc...
        if login in registeredUsers:
            self.wfile.write(str.encode("{\"result\" : \"user_already_registered\"}"))
            return
        # TODO store users as objects with login, user_id, password etc..
        registeredUsers.append(login)
        print(registeredUsers)
        self.wfile.write(str.encode("{\"result\" : \"ok\"}"))

    def handleLogin(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()
        login = json.loads(post_body)['login']
        password = json.loads(post_body)['password']
        # TODO check password
        # TODO handle other errors: missing password, missing login, etc...
        if login in registeredUsers:
            auth_token = "TODO generate token"
            self.wfile.write(str.encode("{\"result\" : \"ok\", \"user_id\": 1337, \"auth_token\" : \"" + auth_token + "\"}"))
            return

        self.wfile.write(str.encode("{\"result\" : \"unknown_login\"}"))

    def handleSendMessage(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = (self.rfile.read(content_len)).decode()

        self.wfile.write(str.encode("{\"result\" : \"not_implemented\"}"))


def runServer():

    PORT = 8080

    httpd = socketserver.TCPServer(("", PORT), ServerHandler)
    print("serving at port", PORT)
    httpd.serve_forever()


if __name__ == '__main__':
    runServer()
