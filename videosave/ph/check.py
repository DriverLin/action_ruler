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


def getPlaylist(listid, savepath):
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
            savepath,
        )
        for elem in bs4.BeautifulSoup(response.text, "html.parser").select(
            "span.title > a"
        )
    ]
    print(len(res))
    return res


needDownload = []
for lid, path in [(220875701,"/tmp/ADM/short"),(220876141,"/tmp/ADM/3D")]:
    videoList = getPlaylist(lid, path)
    downloaded = [x[:-4] for x in os.listdir(path)]
    for video in videoList:
        if video[0] not in downloaded:
            needDownload.append(video)

print(len(needDownload), needDownload)

if len(needDownload) > 0:
    with open("/tmp/needDownload.json", "w", encoding="UTF-8") as f:
        json.dump(needDownload, f)
