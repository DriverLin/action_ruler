#!/usr/bin/python -u
import urllib.request
import urllib.parse
import string
import os

if __name__ == '__main__':
    try:
        apiurl = os.environ.get("URL")
        tag=os.environ.get("TAG")
        title=os.environ.get("TITLE")
        text = os.environ.get("TEXT")
        print("tag: " + tag)
        print("title: " + title)
        print("text: " + text)
        url = urllib.parse.quote("{}?tag={}&title={}&text={}".format(apiurl, tag, title, text), safe=string.printable)
        req = urllib.request.Request(url)
        url_open = urllib.request.urlopen(req)
        data = url_open.read()
        print(data)
    except Exception as e:
        print("Error: ", e)
        
