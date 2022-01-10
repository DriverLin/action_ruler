import requests
import json
from cryptography.fernet import Fernet 
import base64
import os
import hashlib
import threading
import time

def dec(key, data):
    md5hash = hashlib.md5(key.encode()).hexdigest().encode('utf-8')
    f = Fernet(base64.urlsafe_b64encode(md5hash))
    return f.decrypt(data.encode('utf-8')).decode('utf-8')

def download_newleast(releaseUrl):
    try:
        print("fetching release from ", releaseUrl)
        result = requests.get(releaseUrl).json()
        print("fetching release done")
       
        for asset in result["assets"]:
            name = asset["name"]
            if name.endswith(".jar"):
                print("Downloading " + name + " from " + asset["browser_download_url"])
                file = requests.get(asset["browser_download_url"])
                print("Downloaded " + name + " successfully")
                return file.content
        return None
    except Exception as e:
        print(e)
        return None
try:
    tokenbin_url = "https://raw.githubusercontent.com/DriverLin/action_ruler/main/aliyunpan/auto_refresh/refresh_token.bin"
    response = requests.get(tokenbin_url)
    refresh_token = dec(os.environ.get("KEY") ,response.text)
    jar_path = os.path.join(os.getcwd(), "webdav-aliyundriver.jar")
    bytes = download_newleast("https://api.github.com/repos/zxbu/webdav-aliyundriver/releases/latest")
    with open(jar_path, "wb") as f:
        f.write(bytes)
    cmd = "java -jar {} --aliyundrive.refresh-token={} --server.port=8900 --aliyundrive.auth.enable=false".format(jar_path,refresh_token)

    threading.Thread(target=os.system, args=(cmd,)).start()

    for i in range(10):
        print("waiting for server start  {}/10".format(i+1))
        time.sleep(1)

    os.system("chmod 777 ./rclone")
    os.system("./rclone --config ./rclone.conf copy onedrive2: aliyunenc: -P --stats=3s --stats-one-line")

except Exception as e:
    print(e)

exit()



