import json
from time import time
import requests
import bs4
import re
import os

import youtube_dl

def validateTitle(title):
    # 去除文件名中的非法字符
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "", title)  # 替换为下划线
    return new_title


def getPlaylist(listid, savepath,page=0):
    url = f'https://www.xvideos.com/favorite/{listid}/{page}'
    response = requests.get(url)
    # print(response.text)
    res = [ (
        validateTitle(elem.get("title")),
        elem.get("href").split("/")[1],
        savepath
    ) for elem in bs4.BeautifulSoup(response.text, "html.parser").select('p.title > a')]
    return res

res = getPlaylist("62868599/11._", "/home/xv/")

def downoad(path,vid):
    tmpPath = os.path.join("P:\\",validateTitle(vid)+".tmp")
    
    print(f"downloading {path} tmp = {tmpPath}")
    
    ydl_opts = {
        "nooverwrites": True,
        "outtmpl": tmpPath,
        "format": "best",
    }

    print("https://www.xvideos.com" + vid)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # ydl.download([f"https://www.xvideos.com/{vid}/" ])
        ydl.download(["http://www.xvideos.com/video4588838/biker_takes_his_girl"])


for name,vid,savePath in res[:1]:
    print(name,vid,savePath)
    downoad(os.path.join(savePath,name+".mp4")  ,vid)








# saveMap = json.load(open("saveMap.json",'r',encoding="UTF-8"))
# needDownload = []
# for lid, path in saveMap:
#     videoList = getPlaylist(lid, path)
#     downloaded = [x[:-4] for x in os.listdir(path)]
#     need = [x for x in videoList if x[0] not in downloaded]
    
#     print(f"list {lid} has {len(videoList)} videos")
#     print(f"path{path} has {len(downloaded)} download videos")
#     print(f"need download {len(need)} videos")

#     needDownload.extend(need)

# print(f"total {len(needDownload)} videos need download")

# if len(needDownload) > 0:
#     print("downloading...")
#     for name, vk, savedir in needDownload:
#         print(f"{name} {vk} > {savedir}")
#     with open("/tmp/needDownload.json", "w", encoding="UTF-8") as f:
#         json.dump(needDownload, f)
