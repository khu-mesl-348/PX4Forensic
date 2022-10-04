'''
구현할 기능

1. 미션 파일 가져와서 열기
2. 미션 파일 내부 구조 보여주기 (각 구조체 별 의미 설명 및 데이터 나열)
3. 미션 파일 생성 일자, 해쉬값, 암호화 여부 등 파악
4. 미션 파일 시각화

'''

import hashlib
import os.path, time
from src.Mission.PX4MissionParser import *

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

def dataman_is_encrypted(safe, fence, mission, stats):
    if safe[0][0] != len(safe) - 1:
        return 1

    if fence[0][0] != len(fence) - 1:
        return 1

    if stats[2] != len(mission):
        return 1

    return 0

def main():
    if not len(sys.argv) == 2 or sys.argv[1] == "help":
        print("[usage]: ./parser <file name> \n")
        return 1
    print(sys.argv[1])

    filename = sys.argv[1]
    fd = os.open(filename, os.O_BINARY)

    parser = missionParser(fd)

    if fd == -1:
        print("invaild file\n")
        return 1


    safe_points = parser.get_safe_points()
#    fence_points = get_fence_points(fd)
#    mission_0 = get_mission_item(fd, dm_item_t.DM_KEY_WAYPOINTS_OFFBOARD_0.value)
#    mission_1 = get_mission_item(fd, dm_item_t.DM_KEY_WAYPOINTS_OFFBOARD_1.value)
#    mission_stats = get_mission(fd)
#    key_compat = get_key_compat(fd)

    dataman = []

    os.close(fd)

    # 파일 생성일자, 해시
    created = createdTime(filename)
    hashSha = hash_sha1(filename)
    hashMD5 = hash_md5(filename)



if __name__ == '__main__':
    main()