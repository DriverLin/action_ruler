import os
from bottle import *
import json
from cryptography.fernet import Fernet
import base64
import hashlib
import requests


def enc(key, data):
    md5hash = hashlib.md5(key.encode()).hexdigest().encode('utf-8')
    f = Fernet(base64.urlsafe_b64encode(md5hash))
    return str(f.encrypt(data.encode('utf-8')), 'utf-8')


def dec(key, data):
    md5hash = hashlib.md5(key.encode()).hexdigest().encode('utf-8')
    f = Fernet(base64.urlsafe_b64encode(md5hash))
    return f.decrypt(data.encode('utf-8')).decode('utf-8')


@route('/api/getRefreshToken', method="POST")
def getRefreshToken():
    try:
        data = json.loads(request.body.read())
        key = data["key"]
        tokenbin_url = "https://raw.githubusercontent.com/DriverLin/action_ruler/main/aliyunpan/auto_refresh/refresh_token.bin"
        response = requests.get(tokenbin_url)
        refresh_token = dec(key, response.text)
        return refresh_token
    except Exception as e:
        return e.__str__()

@route('/api/dec', method="POST")
def getRefreshToken():
    try:
        data = json.loads(request.body.read())
        return dec(data["key"], data["text"]) 
    except Exception as e:
        return e.__str__()

@route('/api/enc', method="POST")
def getRefreshToken():
    try:
        data = json.loads(request.body.read())
        return enc(data["key"], data["text"]) 
    except Exception as e:
        return e.__str__()

@route('/api/aliyunwebdav/latest/url', method="GET")
def download_newleast():
    try:
        result = requests.get("https://api.github.com/repos/zxbu/webdav-aliyundriver/releases/latest").json()
        for asset in result["assets"]:
            name = asset["name"]
            if name.endswith(".jar"):
                return asset["browser_download_url"]
        return ""
    except Exception as e:
        return e.__str__()

run(host="0.0.0.0", port=int(os.environ.get("PORT") or 8088), reloader=False)  # reloader设置为True可以在更新代码时自动重载
