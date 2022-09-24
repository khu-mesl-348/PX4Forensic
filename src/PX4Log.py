'''
구현할 기능

1. 로그파일 가져와서 열기
2. 로그 파일 내부 구조 보여주기
3. 로그 파일 생성 일자, 해쉬값, 암호화 여부 등 파악
4. 로그 파일 시각화

'''
import hashlib
import os.path, time
from src.Logger.PX4LogParser import *

def hash_sha1(filepath, blocksize=8192):
    sha_1 = hashlib.sha1()
    try:
        f = open(filepath, "rb")
    except IOError as e:
        print("file open error", e)
        return
    while True:
        buf = f.read(blocksize)
        if not buf:
            break
        sha_1.update(buf)
    return sha_1.hexdigest()

def hash_md5(filepath, blocksize=8192):
    md5 = hashlib.md5()
    try:
        f = open(filepath, "rb")
    except IOError as e:
        print("file open error", e)
        return
    while True:
        buf = f.read(blocksize)
        if not buf:
            break
        md5.update(buf)
    return md5.hexdigest()

def createdTime(filepath):
    return time.ctime(os.path.getmtime(filepath))

def is_encrypted(filepath):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except IOError as e:
        print("file open error", e)
        return
   
    a = Header(data)
    if a.magic_number == (85, 76, 111, 103, 1, 18, 53):
        return 0
    else:
        return 1



