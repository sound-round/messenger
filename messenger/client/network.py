
import requests
import json
from messenger.server.server import current_time


# типы клиента
# 1) Command line client -
# 2) Desktop ui client - tkinter,
# 3) web client - some python web libraries?


import tkinter as tk
from tkinter import LEFT, RIGHT, BOTTOM, StringVar



global_auth_token = ""
global_since_date = 0

def register(login, password):

    request_output = '\n'.join([
        "do actual register network request...",
        f'login: {login}',
        f'password: {password}',
    ])
    print(request_output)
    startTs = current_time()
    print(f'register beginning: {startTs}')
    request_json = json.dumps({'login': login, 'password': password})
    response = requests.post(
        "http://127.0.0.1:8080/register", data=request_json
    )
    print(f'register ending: {current_time() - startTs}')
    response_text = response.text  # How does it work?
    print(response_text)
    return json.loads(response_text)


def do_actual_login(login, password):
    global global_auth_token
    request_output = '\n'.join([
        "do actual login network request...",
        f'login: {login}',
        f'password: {password}',
    ])
    print(request_output)
    request_json = json.dumps({'login': login, 'password': password})
    response = requests.post("http://127.0.0.1:8080/login", data=request_json)
    response_text = response.text
    print(response_text)
    response = json.loads(response_text)
    global_auth_token = response["auth_token"]
    return response




def readMessages():
    global global_auth_token, global_since_date
    request_json = json.dumps({'auth_token': global_auth_token, 'since_date': global_since_date})
    print("request= "+ request_json)
    response = requests.post("http://127.0.0.1:8080/readMessages", data=request_json)
    response_text = response.text
    print("response= " + response_text)
    response = json.loads(response_text)
    global_since_date = response["current_time"]
    return response