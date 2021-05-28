import datetime
import socketserver
from http.server import BaseHTTPRequestHandler
import json
from messenger.common.user import User, AuthTokenManager, RegisteredUsersManager, generate_auth_token
import validators


# TODO extract to separate file
class Response(object):
    result = "ok"

    def __init__(self, result):
        self.result = result


class LoginResponse(Response):

    def __init__(self, user_id, auth_token):
        super().__init__("ok")
        self.user_id = user_id
        self.auth_token = auth_token


class GetUserResponse(Response):

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


def toJSON(object):
    return json.dumps(object, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)