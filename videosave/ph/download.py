import json
import shutil
import os
from time import time
import youtube_dl
import vthread

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

@vthread.pool(8)
def downloadByViewkey(savePath,viewKey):
    print(f"downloading {savePath}")
    tmpPath = os.path.join("/tmp",viewKey+".tmp")
    ydl_opts = {
        "nooverwrites": True,
        "outtmpl": tmpPath,
        "format": "best",
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    start = time()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["https://www.pornhub.com/view_video.php?viewkey=" + viewKey])
    usingtime = time() - start
    size = os.path.getsize(tmpPath)
    print("{} download over using {:.2f}s , speed = {:.2f}mb/s".format(savePath,usingtime,size/usingtime/1024/1024))
    
    start = time()
    shutil.move(tmpPath,savePath)
    usingtime = time() - start
    print("{} move over , speed = {:.2f}mb/s".format(savePath,size/usingtime/1024/1024))    

downloadList = json.load(open("/tmp/needDownload.json",'r',encoding="UTF-8"))

for (name,vk,savedir) in downloadList:
    print(name,vk)
    downloadByViewkey( os.path.join(savedir,name+".mp4")   ,vk)

vthread.vthread.pool.waitall()