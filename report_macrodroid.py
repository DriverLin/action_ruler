#!/usr/bin/python -u
import urllib.request
import urllib.parse
import string
import os
import ssl
import coloredlogs
import logging
ssl._create_default_https_context = ssl._create_unverified_context

def getLogger():
    log = logging.getLogger(f'{"main"}:{"loger"}')
    fmt = f'%(asctime)s.%(msecs)03d .%(levelname)s \t%(message)s'
    coloredlogs.install(
        level=logging.DEBUG,
        logger=log,
        milliseconds=True,
        datefmt='%X',
        fmt=fmt
    )
    log.info("Loger initialized")
    return log




if __name__ == "__main__":
    try:
        logger =  getLogger()
        token = os.environ.get("TOKEN") or "none/none"
        tag=os.environ.get("TAG") or "info"
        title=os.environ.get("TITLE") or "No title"

        text = os.environ.get("TEXT") or "No text"
        if os.path.exists("/tmp/msg"):
            text = open("/tmp/msg", "r",encoding="UTF-8").read()
            os.remove("/tmp/msg")

        logger.info("tag: " + tag)
        logger.info("title: " + title)
        logger.info("text: " + text)
        param = urllib.parse.urlencode(
            {"tag": tag, "title": title, "text": text}, quote_via=urllib.parse.quote
        )
        apiUrl = "https://trigger.macrodroid.com/{}?{}".format(token, param)
        logger.info(param)
        req = urllib.request.Request(apiUrl)
        url_open = urllib.request.urlopen(req)
        data = url_open.read()
        logger.info(data)
    except Exception as e:
        logger.error(e.__str__())
