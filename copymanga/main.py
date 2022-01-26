import threading
from time import sleep, time
import json
import requests
import vthread
import os
import shutil
import zipfile
import coloredlogs
import logging



def getLogger():
    log = logging.getLogger(f'{"main"}:{"loger"}')
    fmt = f"%(asctime)s.%(msecs)03d .%(levelname)s \t%(message)s"
    coloredlogs.install(
        level=logging.DEBUG, logger=log, milliseconds=True, datefmt="%X", fmt=fmt
    )
    log.info("Loger initialized")
    return log


logger = getLogger()


@vthread.pool(16)
def download_img(url, path):
    if os.path.exists(path):
        # logger.info("pass"+path)
        pass
    else:
        retry = 0
        while True:
            try:
                tmp_path = path + ".tmp"

                with open(tmp_path, "wb") as f:
                    f.write(requests.get(url, stream=True).content)

                shutil.move(tmp_path, path)
                logger.info(">" * retry + "success : " + path)
                break
            except Exception as e:
                logger.warning(">" * retry + url+ path+ e)
                retry += 1
                sleep(1)


@vthread.pool(16)
def download_img_tozip(url, name, zfp, write_lock):
    if name in [x.replace("\\","/") for x in zfp.namelist()]:
        logger.info("pass"+name)
        pass
    else:
        retry = 0
        while True:
            try:
                bytes = requests.get(url, stream=True).content
                write_lock.acquire()
                zfp.writestr(name, bytes)
                write_lock.release()
                logger.info(">" * retry + "success : "+ name)
                break
            except Exception as e:
                logger.warning(">" * retry + "error! : " + name+ "\t"+ e)
                retry += 1
                sleep(1)


def get_chapters(comic_id, retry=0):
    try:
        first = requests.get(
            "https://api.copymanga.com/api/v3/comic/{}/group/default/chapters?limit=100&offset=0&platform=3".format(
                comic_id
            )
        ).json()
        chapters = [x for x in first["results"]["list"]]
        total = first["results"]["total"]
        for i in range(int(total / 100)):
            offset = (i + 1) * 100
            tmp = requests.get(
                "https://api.copymanga.com/api/v3/comic/{}/group/default/chapters?limit=100&offset={}&platform=3".format(
                    comic_id, offset
                )
            ).json()
            for ch in tmp["results"]["list"]:
                chapters.append(ch)
        logger.info(">" * retry + "get_chapters" + comic_id)
        return chapters
    except Exception as e:
        logger.warning(">" * retry + e)
        sleep(1)
        return get_chapters(comic_id, retry + 1)


def get_pages(comic_id, chapter_uid, retry=0):
    # 这里可以考虑下持久化 在下载连载中的时候减少读取时间
    global cache
    key = "{}_{}".format(comic_id, chapter_uid)
    if key in cache:
        logger.info("get_pages from cache" + comic_id + chapter_uid)
        return cache[key]

    imgs = []
    try:
        result = requests.get(
            "https://api.copymanga.com/api/v3/comic/{}/chapter2/{}?platform=3".format(
                comic_id, chapter_uid
            )
        ).json()
        assert len(result["results"]["chapter"]["contents"]) == len(
            result["results"]["chapter"]["words"]
        )
        for i in range(len(result["results"]["chapter"]["contents"])):
            url = result["results"]["chapter"]["contents"][i]["url"]
            index = result["results"]["chapter"]["words"][i]
            imgs.append((url, index))
        logger.info(">" * retry + "get_pages" + comic_id + chapter_uid)
        cache[key] = imgs
        return imgs
    except Exception as e:
        logger.warning(">" * retry + e)
        sleep(1)
        return get_pages(comic_id, chapter_uid, retry + 1)


# def modeDir(ch,save_dir,manga_id):
#     ch_dir = os.path.join(save_dir , "{:0>4d}_{}".format(ch['index'] + 1 ,ch['name']))
#     if not os.path.exists(ch_dir):
#         os.makedirs(ch_dir)
#     for (url,index) in get_pages(manga_id,ch['uuid']):
#         download_img(url,os.path.join(ch_dir , "{:0>8d}.jpg".format(index+1) )   )
#     vthread.vthread.pool.waitall()

# def modeZip(ch,save_dir,manga_id):
#     packPath = os.path.join(save_dir , "{:0>4d}_{}.zip".format(ch['index'] + 1 ,ch['name']))
#     with zipfile.ZipFile(packPath, 'a', zipfile.ZIP_DEFLATED) as zfp:
#         lock = threading.Lock()
#         for (url,index) in get_pages(manga_id,ch['uuid']):
#             download_img_tozip(url,"{:0>8d}.jpg".format(index+1),zfp,lock)
#         vthread.vthread.pool.waitall()

# def modeSingleDir(ch,save_dir,manga_id):
#     for (url,index) in get_pages(manga_id,ch['uuid']):
#         download_img(url,os.path.join(save_dir , "{:0>4d}_{:0>4d}.jpg".format(ch['index'] + 1,index+1) )   )
#     vthread.vthread.pool.waitall()

# def modeSingleZip(ch,save_dir,manga_id):
#     packPath = os.path.join(save_dir , "main.zip")
#     with zipfile.ZipFile(packPath, 'a', zipfile.ZIP_DEFLATED) as zfp:
#         lock = threading.Lock()
#         for (url,index) in get_pages(manga_id,ch['uuid']):
#             download_img_tozip(url, "{:0>4d}_{:0>4d}.jpg".format(ch['index'] + 1,index+1),zfp,lock)
#         vthread.vthread.pool.waitall()


def modeSingleZipSplitch(ch, manga_id, packPath, zfp, lock):
    for (url, index) in get_pages(manga_id, ch["uuid"]):
        download_img_tozip(
            url,
            "{:0>4d}_{}/{:0>8d}.jpg".format(ch["index"] + 1, ch["name"], index + 1),
            zfp,
            lock,
        )


def copymanga_download(manga_id, save_name=None, save_path=r"./"):
    save_name = manga_id if save_name == None else save_name
    packPath = os.path.join(save_path, "{}.zip".format(save_name))

    zfp = zipfile.ZipFile(packPath, "a", zipfile.ZIP_DEFLATED)

    for i in range(10):
        logger.info("caching ...  " + i )
        time.sleep(1)

    logger.info(zfp.namelist())

    return
    
    lock = threading.Lock()
    for ch in get_chapters(manga_id):
        modeSingleZipSplitch(ch, manga_id, packPath, zfp, lock)
    vthread.vthread.pool.waitall()
    zfp.close()
    logger.info(manga_id + "All over!")


#=======================================================================================================================
cache = json.load(open(r"cache.json", "r", encoding="utf-8"))
watchList = json.load(open(r"watching.json", "r", encoding="utf-8"))
os.system("mkdir /tmp/manga")
os.system("nohup rclone --config ./rclone.conf mount onedrive:Manga  /tmp/manga --vfs-cache-mode full &")

for i in range(10):
    logger.info("Waiting for mount onedrive "+str(i))
    sleep(1)

for (mid,mname) in watchList:
    logger.info("Start download "+mid+" "+mname)
    copymanga_download(mid, mname, "/tmp/manga")
json.dump(cache, open(r"cache.json", "w", encoding="utf-8"))