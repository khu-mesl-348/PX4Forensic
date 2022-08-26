from timeit import default_timer as timer
import serial
import os
from pymavlink import mavutil
from threading import Thread
from src.tools import SerialPort
from src.tree import Tree
import time
from src.MavPort import MavlinkPort
import sys

fd_in = sys.stdin.fileno()
ubuf_stdin = os.fdopen(fd_in, 'rb', buffering=0)


# 실시간 Shell을 여는 함수
# @input: MavlinkSerialPort 객체
# @output: -
# require: -
def live_shell(mav_serialport):
    # Drone -> GCS로 보내는 MAVLink Shell Message 받을 때 사용.
    def read():
        while True:
            data = mav_serialport.serial_read(4096)
            if data and len(data) > 0:
                sys.stdout.write(data)

    try:
        cur_line = ''
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
                        mav_serialport.serial_write(cur_line + '\n')
                        cur_line = ''

                    else:
                        cur_line += ch

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
def search(root, mav_serialport):
    st = []
    st.append(root)

    root_path = os.getcwd()
    
    while len(st) > 0:
        item = st.pop()
        
        # item = 부모 노드
        # item이 디렉토리면, chdir(item.data)
        # item이 파일이면, 아래 과정 무시
        
        if item != root:
            if item.data.find('/') != -1:
                while(not os.path.exists(item.data)):
                    os.chdir("..")
                os.chdir(item.data)
                
                    
        for sub in item.child:
            
            # sub = 자식 노드
            # sub이 디렉토리면, mkdir(sub.data)
            # sub이 파일이면, 파일 생성

            filename = ''
            cur = sub
            # 현재 노드가 파일일 경우
            if cur.data.find('/') == -1:
                while cur.parent != None:
                    filename = cur.data.replace(" ", "") + filename
                    cur = cur.parent
                # root 경로 추가
                filename = '/' + filename  
                # 해당 디렉토리에 파일 받기
                get_file_by_name(filename, mav_serialport)
                print(filename)
                
            else:
                os.makedirs(sub.data)

            st.append(sub)


# ftp 관련 함수들


# opcodes
TerminateSession = 1
OpenFileRO = 4
ReadFile = 5
BurstReadFile = 15
# 전역변수
global mav_msg
global filesize
global updated

msg_buf = []


# ftp 파일을 받아올 때 쓸 멀티스레딩 함수
# 딱히 건드릴 필요 없음
def read_thread(mav_serialport, filename):
    global mav_msg
    global filesize
    global updated

    file = filename.split('/')[-1]
    f = open(file, 'wb')

    while True:
        if filesize == -1:
            break
        d = mav_serialport.ftp_read(4096)
        if d and len(d) > 0:
            mav_msg = d
            print(mav_msg)
            updated = 1
            if mav_msg['opcode'] == 129 and mav_msg['data'][0] == 6:
                f.close()
                break
            if mav_msg['req_opcode'] == 15:
                for c in mav_msg['data']:
                    f.write(c.to_bytes(1, byteorder='little'))


# 파일명으로 Drone의 파일을 ftp 전송받는 함수
# @input: filename(ex. /fs/microse/dataman), MavlinkPort
# @output: file
# require: PX4 기기와 사용자 PC가 연결되어 있어야 함
def get_file_by_name(filename, mav_serialport):
    global mav_msg
    global filesize
    global updated

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
        # Drone -> GCS로 보내는 MAVLink Shell Message 받는 작업을 하는 스레드 생성
        read_th = Thread(target=read_thread, args=(mav_serialport, filename))
        read_th.start()

        # OpenFile 메시지 전송 후 파일 크기 받아옴
        mav_serialport.ftp_write(opcode=OpenFileRO, data=filename, size=len(filename))
        total_size = 0
        offset = 0

        while mav_msg['opcode'] != 128:
            if mav_msg['opcode'] == 129:
                print("파일을 불러오는데 실패하였습니다.")
                filesize = -1
                return
            else:
                continue

        for i in range(4):
            total_size += mav_msg['data'][i] * pow(256, i)
        filesize = total_size

        if total_size - offset > 230:
            read_size = 230
        elif total_size - offset == 0:
            read_size = 1
        else:
            read_size = total_size - offset

        # 파일 전송 요청
        mav_serialport.ftp_write(opcode=BurstReadFile, session=mav_msg['session'], size=read_size, offset=offset,
                                 seq_number=mav_msg['seq_number'])

        while True:
            # 파일 전송이 끝났을 시 요청 멈춤
            if mav_msg['opcode'] == 129 and mav_msg['data'][0] == 6:
                break
            next_seq = mav_msg['seq_number']
            next_offset = mav_msg['offset'] + mav_msg['size']

            # 한 burst가 끝났지만 전송 완료되지 않았을 때 다음 전송 요청
            if mav_msg['burst_complete'] == 1 and next_offset < filesize:
                mav_serialport.ftp_write(opcode=TerminateSession, seq_number=mav_msg['seq_number'])
                mav_serialport.ftp_write(opcode=OpenFileRO, data=filename, size=len(filename))

                mav_serialport.ftp_write(opcode=BurstReadFile, session=mav_msg['session'], size=read_size,
                                         offset=next_offset, seq_number=next_seq)
                time.sleep(3)



    except serial.serialutil.SerialException as e:
        print(e)

    except KeyboardInterrupt:
        read_th.join()
        mav_serialport.ftp_close(mav_msg['seq_number'])

    read_th.join()
    mav_serialport.ftp_close(mav_msg['seq_number'])


def main():
    # MAVLink 포트 연결
    # 보통 자동 감지하나 안되는 경우에는 수동으로 파라미터 넣어서 포트명 변경해주세요
    # mav_serialport = SerialPort()
    mav_serialport = SerialPort('COM3')

    fd_in = sys.stdin.fileno()
    ubuf_stdin = os.fdopen(fd_in, 'rb', buffering=0)
    cur_line = ''

    # get_file_by_name('/fs/microsd/dataman', mav_serialport)
    # 실시간으로 Shell 사용할시
    # live_shell(mav_serialport)

    root = "/"
    tree = Tree(mav_serialport)

    while len(tree.stack) == 0:
        tree.dfs(root)
        tree_root = tree.get_root()
        search(tree_root, mav_serialport)

    get_file_by_name("/fs/microsd/dataman", mav_serialport)
    # while True:
    #     cmd = ubuf_stdin.readline().decode('utf8')
    #     data = command(cmd, mav_serialport)
    #     print(data)

    mav_serialport.close()


if __name__ == '__main__':
    main()