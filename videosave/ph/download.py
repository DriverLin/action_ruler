import json
import shutil
import os
import youtube_dl
import vthread

@vthread.pool(8)
def downloadByViewkey(savePath,viewKey):

    tmpPath = os.path.join("/tmp",viewKey+".tmp")
    ydl_opts = {
        "nooverwrites": True,
        "outtmpl": tmpPath,
        "format": "best",
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["https://www.pornhub.com/view_video.php?viewkey=" + viewKey])
    shutil.move(tmpPath,savePath)

downloadList = json.load(open("/tmp/needDownload.json",'r',encoding="UTF-8"))

for (name,vk,savedir) in downloadList:
    print(name,vk)
    downloadByViewkey( os.path.join(savedir,name+".mp4")   ,vk)

vthread.vthread.pool.waitall()