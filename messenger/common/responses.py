import json


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

    def __init__(self, messages, current_time):
        super().__init__("ok")
        self.messages = messages
        self.current_date = current_time


def toJSON(object):
    return json.dumps(
        object, default=lambda obj: obj.__dict__, sort_keys=True, indent=4,
    )
