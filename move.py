from asyncio import subprocess
import json
import os
from time import time
import zipfile
import shutil
#在zip文件同目录下生成文件夹 里面是分开压缩的多个压缩包
def repack(path):
    if not path.endswith('.zip'):
        print("error! not a zip file")
        return

    print('Repacking...',path)
    saveDir = path[:-4]
    os.makedirs(saveDir, exist_ok=True)
    with zipfile.ZipFile(path, 'r') as zipf:
        names = zipf.namelist()
        packingDict = {}
        for file in names:
            dirname,name = os.path.split(file)
            if dirname in packingDict:
                packingDict[dirname].append(file)
            else:
                packingDict[dirname] = [file]
        for key in packingDict:
            files = sorted(packingDict[key])
            with zipfile.ZipFile(os.path.join(saveDir,key+'.zip'),'w',zipfile.ZIP_DEFLATED) as chzfp:
                for file in files:
                    chzfp.writestr(file,zipf.read(file))
            print('Repacked!'+os.path.join(saveDir,key+'.zip'))      

def singleRepackProcess(instance,workdir):
    print(instance["Name"])
    packPath = os.path.join(workdir,instance["Name"])

    start = time()
    downloadCmd = "rclone copy 'onedrive:Manga/{}' /tmp/manga ".format(instance["Name"])
    os.system(downloadCmd)
    print("use {:.2f}s to download".format(time() - start))

    repack(packPath)

    start = time()
    uploadCmd = "rclone copy /tmp/manga/{} 'onedrive:MangaS/{}' ".format(instance["Name"][:-4],instance["Name"][:-4])
    os.system(uploadCmd)
    print("use {:.2f}s to upload".format(time() - start))

    shutil.rmtree(packPath,ignore_errors=True)
    os.remove(packPath)



def rcloneHandeler():
    po = os.popen("rclone lsjson onedrive:Manga")
    msg = po.buffer.read().decode('utf-8')
    lsres = json.loads(msg)
    workdir = "/tmp/manga"
    os.makedirs(workdir, exist_ok=True)
    for instance in lsres:
        singleRepackProcess(instance,workdir)
        break
        
rcloneHandeler()