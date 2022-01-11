#!/usr/bin/python -u
import requests
import json
from cryptography.fernet import Fernet 
import base64
import os
import hashlib



def enc(key, data):
    md5hash = hashlib.md5(key.encode()).hexdigest().encode('utf-8')
    f = Fernet(base64.urlsafe_b64encode(md5hash))
    return str(f.encrypt(data.encode('utf-8')), 'utf-8')


def dec(key, data):
    md5hash = hashlib.md5(key.encode()).hexdigest().encode('utf-8')
    f = Fernet(base64.urlsafe_b64encode(md5hash))
    return f.decrypt(data.encode('utf-8')).decode('utf-8')



if __name__ == '__main__':
    try:
        old_refresh_token = dec(os.environ.get("KEY"),open("./refresh_token.bin").read())
        # print("old_refresh_token: " , old_refresh_token)
        adata = {
            "refresh_token":old_refresh_token
        }
        aheaders = {'Content-Type': 'application/json'}
        url = "https://api.aliyundrive.com/token/refresh"
        response = requests.post(url, headers=aheaders, data = json.dumps(adata))
        new_refresh_token = response.json()["refresh_token"]
        # print("new_refresh_token: " , new_refresh_token)
        with open("./refresh_token.bin", "w") as f:
            f.write( enc(os.environ.get("KEY"),new_refresh_token))
        print("refresh token refreshed successfully")
    except Exception as e:
        print("Error: ", e)
    