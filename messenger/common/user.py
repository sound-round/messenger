import uuid
import secrets
import copy
import sqlalchemy as sa


class User:
    login = None


    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.avatar_url = None
        self.last_active = None

class AuthToken:
    def __init__(self, user_id, auth_token):
        self.user_id = user_id
        self.auth_token = auth_token


def generate_auth_token():
    return secrets.token_urlsafe()
