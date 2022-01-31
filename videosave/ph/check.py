import json
import requests
import bs4
import re
import os

def validateTitle(title):
    # 去除文件名中的非法字符
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "", title)  # 替换为下划线
    return new_title

def getPlaylist(listid):
    session = requests.Session()
    response = session.get(f"https://www.pornhub.com/playlist/{listid}")
    data_token = (
        bs4.BeautifulSoup(response.text, "html.parser")
        .select_one("#searchInput")
        .get("data-token")
    )
    print(data_token)
    url = f"https://www.pornhub.com/playlist/viewChunked?id={listid}&token={data_token}&page={0}"
    print(url)
    response = session.get(url)
    res = [
        (
            validateTitle(elem.get("title")),
            elem.get("href").split("viewkey=")[-1].split("&pkey=")[0],
        )
        for elem in bs4.BeautifulSoup(response.text, "html.parser").select("span.title > a")
    ]
    print(len(res))
    return res

savedList =[x[:-4] for x in  os.listdir("/tmp/ADM/short")]
# print("savedList",json.dumps( sorted(savedList)  ,indent=2,ensure_ascii=False))
videoList = getPlaylist(220875701)
# print("videoList",videoList)
downloadList = [entry for entry in videoList if entry[0] not in savedList]

print(len(downloadList),downloadList)

if len(downloadList) > 0:
    with open ("/tmp/downloadList.json",'w',encoding="UTF-8") as f:
        json.dump(downloadList,f)
    