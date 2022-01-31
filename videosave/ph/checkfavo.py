import hashlib
import json
import shutil
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


# def getFavos(uid, page=1):
#     #如果长度为48 则还没结束 请继续请求下一页
#     headers = {
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.69",
#     }
#     params = (
#         ("o", "newest"),
#         ("page", page),
#     )
#     try:
#         response = requests.post(
#             f"https://cn.pornhub.com/users/{uid}/videos/favorites/ajax",
#             headers=headers,
#             params=params,
#         )
#         html = response.text
#         etree = bs4.BeautifulSoup(html, "html.parser")
#         return [
#             (
#                 validateTitle(elem.select_one("a").text.strip()),
#                 elem.select_one("a").get("href").split("viewkey=")[-1],
#             )
#             for elem in etree.select("span.title")
#         ]
#     except Exception as e:
#         print(e.__str__())
#         return []



# def checkDownloaded(favos,saveDirs):
#     for saveDir in saveDirs:
#         for filename in os.listdir(saveDir):
#             for favo,vk in favos:
#                 if favo == os.path.splitext(filename)[0]:
#                     print(f"{favo} 已下载 as {filename}")


# checkDownloaded(getFavos("lty6531600"),["P:/"])


# # print(favos)

# # ydl_opts = {
# #             'format': 'best',
# #             'outtmpl': r"P:/OT.MP4",
# #             'nooverwrites': True,
# #             'no_warnings': False,
# #             'ignoreerrors': True,
# #         }


# # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
# #         ydl.download(["https://cn.pornhub.com/view_video.php?viewkey=ph5cf187a0e6b13"])



def downloadByViewkey(savePath,viewKey):

    tmpPath = os.path.join("/tmp",viewKey+".tmp")
    ydl_opts = {
        "nooverwrites": True,
        "outtmpl": savePath,
        "format": "best",
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["https://www.pornhub.com/view_video.php?viewkey=" + viewKey])
    shutil.move(tmpPath,savePath)

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

savedList = os.listdir("/tmp/ADM/short")
print("savedList",savedList)
videoList = getPlaylist(220875701)
print("videoList",videoList)
downloadList = [entry for entry in videoList if entry[0] not in savedList]
print(len(downloadList),downloadList)

for (name,vk) in downloadList:
    print(name,vk)
    downloadByViewkey( os.path.join("/tmp/ADM/short",name+".mp4")   ,vk)
