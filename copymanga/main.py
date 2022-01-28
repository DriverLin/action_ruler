import json
import logging
import os
import shutil
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from time import sleep, time

import coloredlogs
import requests


class packer:
    def __init__(self, save_dir, save_name, picQuiet=False, notifyer=None) -> None:
        self.notifyer = notifyer
        self.picQuiet = picQuiet
        self.save_dir = os.path.join(save_dir, save_name)
        self.save_name = save_name
        os.makedirs(self.save_dir, exist_ok=True)
        log = logging.getLogger(f'{"main"}:{"loger"}')
        fmt = f"%(asctime)s.%(msecs)03d .%(levelname)s \t%(message)s"
        coloredlogs.install(
            level=logging.DEBUG, logger=log, milliseconds=True, datefmt="%X", fmt=fmt
        )
        self.logger = log

    def _download(self, url, name, zfp, write_lock):
        retry = 0
        while True:
            try:
                bytes = requests.get(url, stream=True, timeout=5).content
                write_lock.acquire()
                zfp.writestr(name, bytes)
                write_lock.release()
                if retry > 0:
                    self.logger.warning(
                        "> " * retry + "success : " + zfp.filename + ":" + name
                    )
                else:
                    if not self.picQuiet:
                        self.logger.info(
                            ">" * retry + "success : " + zfp.filename + ":" + name
                        )
                break
            except Exception as e:
                self.logger.warning(
                    "> " * retry
                    + "error! : "
                    + zfp.filename
                    + ":"
                    + name
                    + "\t"
                    + e.__str__()
                )
                retry += 1
                sleep(1)

    def downloadCh(
        self, ch_index, ch_name, get_url_Closure, max_workers=8
    ):  # index 记得从1开始
        pack_name = "{:0>4d}_{}".format(ch_index, ch_name)
        pack_tmp_path = os.path.join(self.save_dir, pack_name + ".zip.tmp")
        pack_path = os.path.join(self.save_dir, pack_name + ".zip")
        if os.path.exists(pack_path):
            self.logger.warning("passed " + pack_name)
            return
        # self.logger.info("start downloaded "+pack_name)
        write_lock = threading.Lock()
        urls = get_url_Closure()
        size = 0
        timeUsed = 0
        with zipfile.ZipFile(
            pack_tmp_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as zfp:
            excuter = ThreadPoolExecutor(max_workers=max_workers)
            start = time()
            for index, url in enumerate(urls):
                excuter.submit(
                    self._download,
                    url,
                    "{:0>8d}.jpg".format(index + 1),
                    zfp,
                    write_lock,
                )
            excuter.shutdown(wait=True)
            timeUsed = time() - start
            size = sum([zinfo.file_size for zinfo in zfp.filelist]) / 1048576

        shutil.move(pack_tmp_path, pack_path)

        if self.notifyer:
            self.notifyer(self.save_name, ch_name)

        finishInfo = "{} finish \t{:.2f}mb in {:.2f}s speed={:.2f}mb/s".format(
            pack_name, size, timeUsed, size / timeUsed
        )

        self.logger.info(finishInfo)


def getLogger():
    log = logging.getLogger(f'{"main"}:{"loger"}')
    fmt = f"%(asctime)s.%(msecs)03d .%(levelname)s \t%(message)s"
    coloredlogs.install(
        level=logging.DEBUG, logger=log, milliseconds=True, datefmt="%X", fmt=fmt
    )
    return log


logger = getLogger()


def get_chapters(manga_id, retry=0):
    try:
        first = requests.get(
            "https://api.copymanga.com/api/v3/comic/{}/group/default/chapters?limit=100&offset=0&platform=3".format(
                manga_id
            ),
            timeout=10,
        ).json()
        chapters = [x for x in first["results"]["list"]]
        total = first["results"]["total"]
        for i in range(int(total / 100)):
            offset = (i + 1) * 100
            tmp = requests.get(
                "https://api.copymanga.com/api/v3/comic/{}/group/default/chapters?limit=100&offset={}&platform=3".format(
                    manga_id, offset
                )
            ).json()
            for ch in tmp["results"]["list"]:
                chapters.append(ch)
        # logger.info(">" * retry + "get_chapters " + manga_id)
        return chapters
    except Exception as e:
        logger.warning(">" * retry + e.__str__())
        sleep(1)
        return get_chapters(manga_id, retry + 1)


def get_Urls(manga_id, chapter_uid, retry=0):
    # 这里可以考虑下持久化 在下载连载中的时候减少读取时间
    imgs = []
    try:
        result = requests.get(
            "https://api.copymanga.com/api/v3/comic/{}/chapter2/{}?platform=3".format(
                manga_id, chapter_uid
            ),
            timeout=10,
        ).json()
        assert len(result["results"]["chapter"]["contents"]) == len(
            result["results"]["chapter"]["words"]
        )
        for i in range(len(result["results"]["chapter"]["contents"])):
            url = result["results"]["chapter"]["contents"][i]["url"]
            # index = result["results"]["chapter"]["words"][i]
            imgs.append(url)
        # logger.info(">" * retry + "get_Urls" + manga_id + chapter_uid)
        return imgs
    except Exception as e:
        logger.warning(">" * retry + e.__str__())
        sleep(1)
        return get_Urls(manga_id, chapter_uid, retry + 1)


msg = ""

def notify_update(mname, update):
    global msg
    msg += "《{}》更新到{}\n".format(mname, update)

def copymanga_download(manga_id, manga_name=None, save_path=r"./"):
    manga_name = manga_id if manga_name == None else manga_name
    pa = packer(save_path, manga_name, picQuiet=True, notifyer=notify_update)
    for index, ch in enumerate(get_chapters(manga_id)):
        pa.downloadCh(
            ch_index=index + 1,
            ch_name=ch["name"],
            get_url_Closure=lambda: get_Urls(manga_id, ch["uuid"]),
        )

if __name__ == "__main__":
    
    watchList = json.load(open(r"watching.json", "r", encoding="utf-8"))

    for (mid, mname) in watchList:
        
        logger.info("Start download " + mid + " " + mname)

        copymanga_download(mid, mname, "/tmp/manga")
        # copymanga_download(mid, mname, "D:\\漫画")

    open("/tmp/msg", "w", encoding="UTF-8").write(msg) if len(msg) > 0 else None