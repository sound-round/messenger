import requests
import json
from messenger.server.server import current_time
from requests.exceptions import ConnectionError


global_auth_token = ""
global_since_date = 0
global_user_id = ""


def register(login, password):

    request_output = '\n'.join([
        "do actual register network request...",
        f'login: {login}',
        f'password: {password}',
    ])
    print(request_output)
    request_json = json.dumps({'login': login, 'password': password})
    try:
        response = requests.post(
            "http://127.0.0.1:8080/register", data=request_json
        )
    except ConnectionError as e:
        print(e)
    else:
        response_text = response.text  # How does it work?
        print(f"response text: {response_text}")
        return json.loads(response_text)

    response_text = '''{
        "result": "internal_server_error"
    }'''
    print(f"response text: {response_text}")
    return json.loads(response_text)


def do_actual_login(login, password):
    global global_auth_token, global_user_id, global_since_date
    request_output = '\n'.join([
        "do actual login network request...",
        f'login: {login}',
        f'password: {password}',
    ])
    print(request_output)
    request_json = json.dumps({'login': login, 'password': password})
    try:
        response = requests.post(
            "http://127.0.0.1:8080/login", data=request_json
        )
    except ConnectionError as e:
        print(e)
    else:
        response_text = response.text
        print(f'response text: {response_text}')
        response = json.loads(response_text)
        global_auth_token = response.get("auth_token")
        global_user_id = response.get("user_id")
        if response.get('last_active'):
            global_since_date = response.get('last_active')
        return response

    response_text = '''{
           "result": "internal_server_error"
       }'''
    print(f"response text: {response_text}")
    return json.loads(response_text)


def read_messages():
    global global_auth_token, global_since_date
    request_json = json.dumps(
        {
            'auth_token': global_auth_token,
            'since_date': global_since_date
        }
    )
    print("request= " + request_json)
    try:
        response = requests.post(
            "http://127.0.0.1:8080/readMessages", data=request_json
        )
    except ConnectionError as e:
        print(e)
    else:
        response_text = response.text
        print("response= " + response_text)
        response = json.loads(response_text)
        global_since_date = response.get("current_time")
        return response
    response_text = '''{
               "result": "internal_server_error"
           }'''
    print(f"response text: {response_text}")
    return json.loads(response_text)


def send_message(to_user_id, message_to_send):
    global global_auth_token
    request_json = json.dumps(
        {
            'auth_token': global_auth_token,
            'to_user_id': to_user_id,
            'message': message_to_send,
        }
    )
    print("request= " + request_json)
    try:
        response = requests.post(
            "http://127.0.0.1:8080/sendMessage", data=request_json
        )
    except ConnectionError as e:
        print(e)
    else:
        response_text = response.text
        print("response= " + response_text)
        return json.loads(response_text)

    response_text = '''{
                   "result": "internal_server_error"
               }'''
    print(f"response text: {response_text}")
    return json.loads(response_text)


def get_username(user_id):
    global global_auth_token
    request_json = json.dumps(
        {
            'auth_token': global_auth_token,
            'user_id_to_get': user_id
        }
    )
    try:
        response = requests.post(
            "http://127.0.0.1:8080/getUser", data=request_json
        )
    except ConnectionError as e:
        print(e)
    else:
        response_text = response.text
        response = json.loads(response_text)
        return response
    response_text = '''{
                       "result": "internal_server_error"
                   }'''
    print(f"response text: {response_text}")
    return json.loads(response_text)


def find_user_id(login):
    global global_auth_token
    request_json = json.dumps(
        {
            'auth_token': global_auth_token,
            'user_login_to_get': login
        }
    )
    try:
        response = requests.post(
            "http://127.0.0.1:8080/findUserId", data=request_json
        )
    except ConnectionError as e:
        print(e)
    else:
        response_text = response.text
        response = json.loads(response_text)
        print(response_text)
        return response
    response_text = '''{
                       "result": "internal_server_error"
                   }'''
    print(f"response text: {response_text}")
    return json.loads(response_text)
