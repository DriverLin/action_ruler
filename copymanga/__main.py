import os
import json
from struct import pack
import zipfile
import shutil
import coloredlogs
import logging
import vthread


def getLogger():
    log = logging.getLogger(f'{"main"}:{"loger"}')
    fmt = f"%(asctime)s.%(msecs)03d .%(levelname)s \t%(message)s"
    coloredlogs.install(
        level=logging.DEBUG, logger=log, milliseconds=True, datefmt="%X", fmt=fmt
    )
    log.info("Loger initialized")
    return log

logger = getLogger()

@vthread.pool(8)
def repackProcess(path):
    with zipfile.ZipFile(path,'r') as oldzfp:
        if  "_" not in oldzfp.namelist()[0]:
            logger.info("pass "+path)
            return
        else:
            logger.info("Repacking..."+path)
        with zipfile.ZipFile(path+".tmp",'w') as newzfp:
            for file in oldzfp.namelist():
                newName = file.split("/")[1]
                newzfp.writestr(newName,oldzfp.read(file))
    os.remove(path)
    shutil.move(path+".tmp",path)
    logger.info("Repacked!"+path)

# repack(r"P:\hapiaier\哈批艾尔\0002_第02话.zip")
def listAll(path):
    result = []
    for root,dirs,files in os.walk(path):
        for file in files:
            if file.endswith(".zip"):
                result.append(os.path.join(root,file))
    return result

res = listAll(r"/tmp/manga")
for file in res:
    logger.info(file)
    repackProcess(file)
vthread.vthread.pool.waitall()
