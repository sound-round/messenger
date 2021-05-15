import uuid
import secrets
import copy


class RegisteredUsers:
    store = []

    def add_user(self, user):
        self.store.append(user)

    def show_users(self):
        print('Registered users:')
        for user in self.store:
            print('login: {}'.format(user.get_login()))
            print('user_id: {}'.format(user.get_id()))

    def is_login_in_store(self, login):
        for user in self.store:
            if user.get_login() == login:
                return True

    def is_id_in_store(self, user_id):
        for user in self.store:
            if user.get_id() == user_id:
                return True

    def get_user_by_login(self, login):
        for user in self.store:
            if user.get_login() == login:
                return user

    def get_user_by_id(self, user_id):
        for user in self.store:
            if user.get_id() == user_id:
                return user


class AuthToken:

    store = []
    def add_user(self, current_user, token):
        user = copy.deepcopy(current_user)
        user.auth_token_store = []
        user.auth_token_store.append(token)
        delattr(user, 'login')
        delattr(user, 'password')
        self.store.append(user)

    def add_token_to_user(self, current_user):
        for user in self.store:
            if user.get_id() == current_user.get_id():
                new_auth_token = generate_auth_token()
                user.auth_token_store.append(new_auth_token)

    def get_user_tokens(self, current_user):
        for user in self.store:
            if user.get_id() == current_user.get_id():
                return user.auth_token_store

    def show_user_tokens(self):
        for user in self.store:
            print('user_id: {}'.format(user.get_id()))
            print('user_auth_tokens: {}'.format(self.get_user_tokens(user)))

    def get_user_by_login(self, login):
        for user in self.store:
            if user.get_login() == login:
                return user

    def get_user_by_auth_token(self, auth_token):
        for user in self.store:
            if auth_token in self.get_user_tokens(user):
                return user

    def is_token_in_store(self, auth_token):
        for user in self.store:
            if auth_token in self.get_user_tokens(user):
                return True




class User:

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.user_id = str(generate_user_id())
        self.avatar_url = None

    def get_login(self):
        return self.login

    def set_login(self, new_login):
        self.login = new_login

    def get_password(self):
        return self.password

    def set_password(self, new_password):
        self.password = new_password

    def check_password(self, entered_password):
        return self.get_password() == entered_password

    def get_id(self):
        return self.user_id

    def set_avatar(self, url):
        self.avatar_url = url

    def get_avatar(self):
        return self.avatar_url




def generate_user_id():
    return uuid.uuid4()


def generate_auth_token():
    return secrets.token_urlsafe()


