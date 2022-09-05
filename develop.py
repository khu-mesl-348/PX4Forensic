from timeit import default_timer as timer
import serial
import os
from pymavlink import mavutil
from threading import Thread
from src.Mission.tools import SerialPort
from src.Mission.tree import Tree
import time
import sys

# opcodes
TerminateSession = 1
ResetSession = 2
OpenFileRO = 4
ReadFile = 5
CreateFile = 6
WriteFile = 7
RemoveFile = 8
CreateDirectory = 9
RemoveDirectory = 10
BurstReadFile = 15

# nak err info
PASS = -2
RELOAD = -1
SUCCESS = 0
FailErrno = 2
SessionNotFound = 4
FileNotFound = 10

# nuttx errno
EACCES = 2

fd_in = sys.stdin.fileno()
ubuf_stdin = os.fdopen(fd_in, 'rb', buffering=0)


# 실시간 Shell을 여는 함수
# @input: MavlinkSerialPort 객체
# @output: -
# require: -
def live_shell(mav_serialport):
    cur_line = ''

    # Drone -> GCS로 보내는 MAVLink Shell Message 받을 때 사용.
    def read():
        while True:
            data = mav_serialport.serial_read(4096)
            if data and len(data) > 0:
                sys.stdout.write(data)
            if cur_line == "exit":
                break

    try:

        next_heartbeat_time = timer()

        # Drone -> GCS로 보내는 MAVLink Shell Message 받는 작업을 하는 스레드 생성
        read_th = Thread(target=read)
        read_th.start()

        quit_time = None
        while quit_time is None or quit_time > timer():
            while True:
                cmd = ubuf_stdin.readline().decode('utf8')
                for ch in cmd:
                    if ch == '\n':
                        # Todo: 위아래로 명령어 이동하는거 만들기
                        # if len(cur_line) > 0:
                        # command_history = []
                        # cur_history_index = 0
                        if cur_line == "exit":
                            break
                        mav_serialport.serial_write(cur_line + '\n')
                        cur_line = ''

                    else:
                        cur_line += ch

                if cur_line == "exit":
                    break
            if cur_line == "exit":
                break

            # handle heartbeat sending
            heartbeat_time = timer()
            if heartbeat_time > next_heartbeat_time:
                mav_serialport.mav.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GENERIC,
                                                      mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
                next_heartbeat_time = heartbeat_time + 1

    except serial.serialutil.SerialException as e:
        print(e)

    except KeyboardInterrupt:
        mav_serialport.close()

    read_th.join()


# 구성된 트리를 dfs 탐색하는 함수
# @input: root: 탐색할 트리의 루트 노드
# @output: -
# description:
def copy_data_from_UAV(root, mav_serialport):
    st = []
    search_result = []
    st.append(root)

    root_path = os.getcwd()

    while len(st) > 0:
        item = st.pop()

        # item = 부모 노드
        # item이 디렉토리면, chdir(item.data)
        # item이 파일이면, 아래 과정 무시

        if item != root:
            if item.data.find('/') != -1:
                while (not os.path.exists(item.data)):
                    os.chdir("..")
                os.chdir(item.data)

        for sub in item.child:

            # sub = 자식 노드
            # sub이 디렉토리면, mkdir(sub.data)
            # sub이 파일이면, 파일 생성

            cur = sub
            filename = ""
            # 현재 노드가 파일일 경우
            if cur.data.find('/') == -1:
                while cur.parent != None:
                    filename = cur.data + filename
                    cur = cur.parent
                # root 경로 추가
                filename = '/' + filename
                # 해당 디렉토리에 파일 받기
                print(filename)
                while True:
                    res = get_file_by_name(filename, mav_serialport)
                    if res[0] == RELOAD:
                        print("재요청중...")
                    elif res[0] == SUCCESS:
                        search_result.append([filename, 'SUCCESS'])
                        break
                    elif res[0] == FailErrno:
                        if res[1] == EACCES:
                            search_result.append([filename, 'EACCES'])
                            break
                    elif res[0] == SessionNotFound:
                        print("Session not found. reloading...")
                    elif res[0] == FileNotFound:
                        search_result.append([filename, 'FILEEXISTSERROR'])
                        break
                    else:
                        break

            else:
                try:
                    foldername = sub.data
                    while foldername[0] == " ":
                        foldername = foldername[1:]
                    os.makedirs(foldername)
                except FileExistsError:
                    pass

            st.append(sub)

    return search_result


# ftp 관련 함수들


# 전역변수
global filesize
global updated
global timeout

msg_buf = []


# 파일명으로 Drone의 파일을 ftp 전송받는 함수
# @input: filename(ex. /fs/microse/dataman), MavlinkPort
# @output: file
# require: PX4 기기와 사용자 PC가 연결되어 있어야 함
def get_file_by_name(filename, mav_serialport):
    global filesize
    global updated
    global timeout

    filesize = 0
    # FTP 프로토콜
    mav_msg = {
        'seq_number': 0,
        'session': 0,
        'opcode': 0,
        'size': 0,
        'req_opcode': 0,
        'burst_complete': 0,
        'offset': 0,
        'data': []
    }

    try:
        # # Drone -> GCS로 보내는 MAVLink Shell Message 받는 작업을 하는 스레드 생성
        # read_th = Thread(target=read_thread, args=(mav_serialport, filename))
        # read_th.start()

        # 버퍼 비우기
        while True:
            d = mav_serialport.ftp_read(4096)
            mav_msg = d
            if d and len(d) > 0:
                print(d)
            else:
                break

        # 파일 이름 추출
        file = filename.split('/')[-1]
        if file[0] == '.':
            return [PASS]

        # OpenFile 메시지 전송 후 파일 크기 받아옴
        mav_serialport.ftp_write(opcode=OpenFileRO, data=filename, size=len(filename))
        total_size = 0
        offset = 0
        timeout = 0
        print(filename, "\n===============")

        # OpenFile 후 ACK 파싱
        while True:
            d = mav_serialport.ftp_read(4096)
            if d and len(d) > 0:
                print(d)
                if d['opcode'] == 129:  # 오류 처리
                    if d['data'][0] == 2:  # 운영체제 사이드에서 오류
                        if d['data'][1] == 13:  # Permission denied
                            print("Permission denied")
                            return [FailErrno, EACCES]

                    if d['data'][0] == SessionNotFound:
                        print('session not found')
                        return [SessionNotFound]
                    if d['data'][0] == 10:  # 파일이 존재하지 않을 시
                        print("File not found")
                        return [FileNotFound]

                    print("파일을 불러오는데 실패하였습니다.")
                    return [RELOAD]
                    break

                else:
                    mav_msg = d
                    break

        print(mav_msg)

        # OpenFile 성공시 데이터 길이 추출
        if len(mav_msg['data']) == 4:
            for i in range(4):
                total_size += mav_msg['data'][i] * pow(256, i)
            filesize = total_size
        else:
            print("잘못된 응답입니다.")
            return [PASS]

        if total_size - offset > 230:
            read_size = 230
        elif total_size - offset == 0:
            read_size = 1
        else:
            read_size = total_size - offset

        # 파일 Open
        f = open(file, 'wb')

        # 파일 전송 요청
        while True:
            cur_seq = mav_msg['seq_number']
            mav_serialport.ftp_write(opcode=ReadFile, session=mav_msg['session'], size=read_size, offset=offset,
                                     seq_number=mav_msg['seq_number'])

            while True:
                print(f"{filename}: {offset} of {total_size}")
                d = mav_serialport.ftp_read(4096)

                if d and len(d) > 0:
                    last_time = time.time()
                    mav_msg = d
                    break

            if mav_msg['opcode'] == 129:  # 파일 전송 도중 오류 처리
                if mav_msg['data'][0] == 6:  # 파일 전송 완료
                    f.close()
                    res = [SUCCESS]
                    break
                else:  # 다른 오류 발생 시
                    print(mav_msg)
                    print("파일을 불러오는 도중 오류가 발생하였습니다..")
                    res = [RELOAD]
                    break
            else:  # 데이터 정상 수신
                for c in mav_msg['data']:
                    f.write(c.to_bytes(1, byteorder='little'))

            offset += read_size

    except serial.serialutil.SerialException as e:
        print(e)

    except KeyboardInterrupt:
        mav_serialport.ftp_close(seq_num=d['seq_number'], session=0)
        while True:
            d = mav_serialport.ftp_read(4096)

            if d and len(d) > 0:
                print(d)
                break

    # ftp 세션 닫기
    mav_serialport.ftp_close(seq_num=d['seq_number'], session=0)
    while True:
        d = mav_serialport.ftp_read(4096)
        mav_msg = d
        if d and len(d) > 0:
            print("terminate: ", d)
            break

    return res


# Drone에 파일을 ftp 전송하는 함수
# @input: filename(ex. /fs/microse/dataman): 드론 상에서의 저장 위치, filepath: 보낼 파일의 경로, MavlinkPort
# @output: 실행 결과
# require: PX4 기기와 사용자 PC가 연결되어 있어야 함
def send_file_by_name(filename, filepath, mav_port):
    return


def main():
    # MAVLink 포트 연결
    # 보통 자동 감지하나 안되는 경우에는 수동으로 파라미터 넣어서 포트명 변경해주세요
    # mav_serialport = SerialPort()
    mav_port = SerialPort()
    if mav_port is None:
        print("시리얼 연결에 오류가 발생하였습니다")
        return

    fd_in = sys.stdin.fileno()
    ubuf_stdin = os.fdopen(fd_in, 'rb', buffering=0)
    cur_line = ''

    # 실시간으로 Shell 사용할시
    # live_shell(mav_port)

    root = "/"
    tree = Tree(mav_port)

    blacklist = ['group/', 'mmcsd0']
    tree.dfs(root, blacklist)
    tree_root = tree.get_root()

    st = []
    search_result = []
    st.append(tree_root)


    root_path = os.getcwd()
    res = []
    # 폴더들 한번씩 순회해보기
    while len(st) > 0:
        item = st.pop()

        # item = 부모 노드
        # item이 디렉토리면, chdir(item.data)
        # item이 파일이면, 아래 과정 무시

        for sub in item.child:
            # sub = 자식 노드
            # sub이 디렉토리면, mkdir(sub.data)
            # sub이 파일이면, 파일 생성

            cur = sub
            filename = ""
            # 현재 노드가 파일일 경우: 무시
            if cur.data.find('/') == -1:
                continue
            # 현재 노드가 폴더일 경우: 도킹 시도
            else:
                foldername = ""
                while cur.parent != None:
                    foldername = cur.data + foldername
                    cur = cur.parent
                # root 경로 추가
                foldername = '/' + foldername

                foldername = foldername
                mav_port.ftp_write(opcode=CreateDirectory, data='/fs/microsd/', size=len("/fs/microsd/"),seq_number=0)
                print("/fs/microsd/")
                # OpenFile 후 ACK 파싱
                while True:
                    d = mav_port.ftp_read(4096)
                    if d and len(d) > 0:
                        print(d)
                        if d['opcode'] == 129 :  # 오류 처리
                            if d['data'][0] == 2:  # 운영체제 사이드에서 오류
                                if d['data'][1] == 13:  # Permission denied
                                    print("Permission denied")
                                    res.append((foldername, "Permission Denied"))
                                    break

                            if d['data'][0] == SessionNotFound:
                                print('session not found')
                                break
                            if d['data'][0] == 10:  # 파일이 존재하지 않을 시
                                print("File not found")
                                break

                            print("파일을 불러오는데 실패하였습니다.")
                            break

                        elif d['opcode'] == 128 :
                            res.append((foldername, "Success"))
                            mav_port.ftp_close(seq_num=d['seq_number'], session=d['session'])

                            # OpenFile 후 ACK 파싱
                            while True:
                                d = mav_port.ftp_read(4096)
                                if d and len(d) > 0:
                                    if d['opcode'] == 129:  # 오류 처리
                                        if d['data'][0] == SessionNotFound:
                                            print('session not found')
                                            break

                                        print("파일을 불러오는데 실패하였습니다.")
                                        break

                                    else:
                                        print(d)
                                        break
                            break
                    else:
                        continue

            st.append(sub)
    mav_port.ftp_close(seq_num=d['seq_number'], session=d['session'])
    mav_port.close()

    print(res)


if __name__ == '__main__':
    main()