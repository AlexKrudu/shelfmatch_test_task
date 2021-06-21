import logging
import requests
import time
import os
import base64

import config


def init_logger(filename):
    logging.basicConfig(filename=filename, filemode="w", level=logging.INFO)


def get_token():
    if os.path.isfile(config.TOKEN_PATH) and time.time() - os.path.getmtime(config.TOKEN_PATH) < 1440 :
        with open(config.TOKEN_PATH, 'r') as f:
            return f.read()
    data = {'account': {'login': config.login, 'password': config.password}}
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(config.AUTH_URL + 'token', json=data, headers=headers)
    if response.status_code == 200:
        token = response.json()['account']['token']['value']
        with open(config.TOKEN_PATH, "w") as f:
            f.write(token)
        return token
    return None


def get_images_names(root: str):
    img_names = []
    for root, dirs, files in os.walk(root):
        for f in files:
            filetype = f.split(".")[1]  # assuming that filenames contain only one dot char
            if filetype == 'png' or filetype == 'jpg' or filetype == 'gif':
                img_names.append(os.path.join(root, f))
    return img_names


def to_base64(filename: str):
    with open(filename, 'rb') as img:
        return filename, base64.b64encode(img.read()).decode()
