'''
구현할 기능

1. 미션 파일 가져와서 열기
2. 미션 파일 내부 구조 보여주기 (각 구조체 별 의미 설명 및 데이터 나열)
3. 미션 파일 생성 일자, 해쉬값, 암호화 여부 등 파악
4. 미션 파일 시각화

'''

import hashlib
import os.path, time

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


def hash_sha1(filepath, blocksize=8192):
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


def main():
    if not len(sys.argv) == 2 or sys.argv[1] == "help":
        print("[usage]: ./parser <file name> \n")
        return 1
    print(sys.argv[1])
    fd = os.open(sys.argv[1], os.O_BINARY)
    if fd == -1:
        print("invaild file\n")
        return 1

    init()

    get_safe_points(fd)
    get_fence_points(fd)
    get_mission_item(fd, dm_item_t.DM_KEY_WAYPOINTS_OFFBOARD_0.value)
    get_mission_item(fd, dm_item_t.DM_KEY_WAYPOINTS_OFFBOARD_1.value)
    get_mission(fd)
    get_key_compat(fd)


if __name__ == '__main__':
    main()