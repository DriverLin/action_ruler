#!/usr/bin/python -u
import urllib.request
import urllib.parse
import string
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

if __name__ == "__main__":
    try:
        token = os.environ.get("TOKEN")
        tag=os.environ.get("TAG")
        title=os.environ.get("TITLE")
        text = os.environ.get("TEXT")
        print("tag: " + tag)
        print("title: " + title)
        print("text: " + text)
        param = urllib.parse.urlencode(
            {"tag": tag, "title": title, "text": text}, quote_via=urllib.parse.quote
        )
        apiUrl = "https://trigger.macrodroid.com/{}?{}".format(token, param)
        print(param)
        req = urllib.request.Request(apiUrl)
        url_open = urllib.request.urlopen(req)
        data = url_open.read()
        print(data)
    except Exception as e:
        print("Error: ", e)
