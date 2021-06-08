
import requests
import json


# типы клиента
# 1) Command line client -
# 2) Desktop ui client - tkinter,
# 3) web client - some python web libraries?


import tkinter as tk
from tkinter import LEFT, RIGHT, BOTTOM, StringVar


def do_actual_register(login, password):
    request_output = '\n'.join([
        "do actual register network request...",
        f'login: {login}',
        f'password: {password}',
    ])
    print(request_output)
    request_json = json.dumps({'login': login, 'password': password})
    response = requests.post(
        "http://localhost:8080/register", data=request_json
    )
    response_text = response.text  # How does it work?
    print(response_text)
    return response_text


def do_actual_login(login, password):
    request_output = '\n'.join([
        "do actual login network request...",
        f'login: {login}',
        f'password: {password}',
    ])
    print(request_output)
    request_json = json.dumps({'login': login, 'password': password})
    response = requests.post("http://localhost:8080/login", data=request_json)
    response_text = response.text
    print(response_text)
    return response_text
