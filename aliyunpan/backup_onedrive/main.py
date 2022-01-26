#!/usr/bin/python -u
import subprocess
import requests
import json
from cryptography.fernet import Fernet
import base64
import os
import hashlib
import threading
import time
import coloredlogs
import logging


def getLogger():
    log = logging.getLogger(f'{"main"}:{"loger"}')
    fmt = f"%(asctime)s.%(msecs)03d .%(levelname)s \t%(message)s"
    coloredlogs.install(
        level=logging.DEBUG, logger=log, milliseconds=True, datefmt="%X", fmt=fmt
    )
    log.info("Loger initialized")
    return log


logger = getLogger()


def dec(key, data):
    md5hash = hashlib.md5(key.encode()).hexdigest().encode("utf-8")
    f = Fernet(base64.urlsafe_b64encode(md5hash))
    return f.decrypt(data.encode("utf-8")).decode("utf-8")


def download_newleast(releaseUrl):
    try:
        logger.info("fetching release from " + releaseUrl)
        result = requests.get(releaseUrl).json()
        logger.info("fetching release done")

        for asset in result["assets"]:
            name = asset["name"]
            if name.endswith(".jar"):
                logger.info(
                    "Downloading " + name + " from " + asset["browser_download_url"]
                )
                file = requests.get(asset["browser_download_url"])
                logger.info("Downloaded " + name + " successfully")
                return file.content
        return None
    except Exception as e:
        logger.error(e.__str__())
        return None

def rcloneExecutor(cmd, logger):
    if "-P" in cmd:
        cmd = cmd.replace("-P", "")
    if "--rc" not in cmd:
        cmd = cmd + " --rc"

    logger.warning("running\t[" + cmd + "]")
    processThread = threading.Thread(target=os.system, args=(cmd,))
    processThread.start()
    time.sleep(3)
    msg = ''
    while processThread.is_alive():
        res = os.popen("rclone rc core/stats").read()
        try:
            state = json.loads(res)
            speed = int(state["speed"] / 1048576 * 100) / 100#MB/S
            transfered = int(state["bytes"] / 1048576 * 100) / 100#MB
            usedTime = str(int(state["transferTime"]/60)) +"min "+ str(int(state["transferTime"])%60) +"s"    #min
            formatedOutput = "trasnfed {}mb  \t{}  \t{}mb/s".format(transfered, usedTime, speed)
            msg = formatedOutput
            logger.info(formatedOutput)
        except Exception as e:
            logger.error(e)
        time.sleep(1)
    logger.warning("over\t[" + cmd + "]")
    return msg


try:
    tokenbin_url = "https://raw.githubusercontent.com/DriverLin/action_ruler/main/aliyunpan/auto_refresh/refresh_token.bin"
    response = requests.get(tokenbin_url)
    refresh_token = dec(os.environ.get("KEY"), response.text)
    jar_path = os.path.join(os.getcwd(), "webdav-aliyundriver.jar")
    bytes = download_newleast(
        "https://api.github.com/repos/zxbu/webdav-aliyundriver/releases/latest"
    )
    with open(jar_path, "wb") as f:
        f.write(bytes)
    cmd = "java -jar {} --aliyundrive.refresh-token={} --server.port=8900 --aliyundrive.auth.enable=false > /dev/null".format(
        jar_path, refresh_token
    )

    # threading.Thread(target=os.system, args=(cmd,)).start()
    os.system("nohup {} &".format(cmd))

    for i in range(10):
        logger.info("waiting for server start  {}/10".format(i + 1))
        time.sleep(1)
    # os.system("chmod 777 ./rclone")
    msg = rcloneExecutor(
        "rclone --config ./rclone.conf copy onedrive2: aliyunenc: --rc", logger
    )
    logger.info("all done!")


    with open("/tmp/msg", "w",encoding="UTF-8") as f:
        f.write(msg)


except Exception as e:
    logger.error(e.__str__())

exit()
