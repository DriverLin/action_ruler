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

saveMap = json.load(open("saveMap.json",'r',encoding="UTF-8"))
needDownload = []
for lid, path in saveMap:
    videoList = getPlaylist(lid, path)
    downloaded = [x[:-4] for x in os.listdir(path)]
    need = [x for x in videoList if x[0] not in downloaded]
    
    print(f"list {lid} has {len(videoList)} videos")
    print(f"path{path} has {len(downloaded)} download videos")
    print(f"need download {len(need)} videos")

    needDownload.extend(need)

print(f"total {len(needDownload)} videos need download")

if len(needDownload) > 0:
    print("downloading...")
    for name, vk, savedir in needDownload:
        print(name, vk)
    with open("/tmp/needDownload.json", "w", encoding="UTF-8") as f:
        json.dump(needDownload, f)
        