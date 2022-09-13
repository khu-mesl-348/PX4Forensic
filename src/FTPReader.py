from src.Mission.tree import Tree
import time
from src.Mission.tools import SerialPort
import sys
import os
from timeit import default_timer as timer
import serial
from pymavlink import mavutil
from threading import Thread
from src.Mission.tools import command
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
CalcFileCRC32 = 14
BurstReadFile = 15

# nak err info
PASS = -2
RELOAD = -1
SUCCESS = 0
FailErrno = 2
SessionNotFound = 4
FileNotFound = 10

# nuttx errno
EACCES = 13
ENOENT =  2
EIO = 5


class FTPReader:

    def __init__(self, blacklist=['group/', 'mmcsd0'], root="/", _port=None):
        fd_in = sys.stdin.fileno()
        self.ubuf_stdin = os.fdopen(fd_in, 'rb', buffering=0)
        self.root = root
        if _port is None:
            self.mav_port = None
        else:
            self.connect_port(_port, blacklist)





    def connect_port(self, port, blacklist=[]):
        self.mav_port = port
        tree = Tree(self.mav_port)
        self.total_count = tree.dfs(self.root, blacklist)
        self.tree_root = tree.get_root()

    # 실시간 Shell을 여는 함수
    # @input: MavlinkSerialPort 객체
    # @output: -
    # require: -
    def live_shell(self):
        cur_line = ''

        # Drone -> GCS로 보내는 MAVLink Shell Message 받을 때 사용.
        def read():
            while True:
                data = self.mav_port.serial_read(4096)
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
                    cmd = self.ubuf_stdin.readline().decode('utf8')
                    for ch in cmd:
                        if ch == '\n':
                            # Todo: 위아래로 명령어 이동하는거 만들기
                            # if len(cur_line) > 0:
                            # command_history = []
                            # cur_history_index = 0
                            if cur_line == "exit":
                                break
                            self.mav_port.serial_write(cur_line + '\n')
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
                    self.mav_port.mav.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GENERIC,
                                                          mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
                    next_heartbeat_time = heartbeat_time + 1

        except serial.serialutil.SerialException as e:
            print(e)

        except KeyboardInterrupt:
            self.mav_port.close()

        read_th.join()


    def get_crc_from_UAV(self, root="", blacklist=[]):
        st = []
        search_result = []
        blacklist = ['obj/', 'dev/']
        if root == "":
            root = self.tree_root
            st.append(root)
        seq_num = 0
        while len(st) > 0:
            item = st.pop()
            # item = 부모 노드
            # item이 디렉토리면, chdir(item.data)
            # item이 파일이면, 아래 과정 무시

            for sub in item.child:

                # sub = 자식 노드
                # sub이 디렉토리면, mkdir(sub.data)
                # sub이 파일이면, 파일 생성
                print("Data: ",sub.data)
                if sub.data in blacklist:
                    continue
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
                        res = self.get_crc_by_name(filename, seq_num)
                        if res[0] == RELOAD:
                            print("재요청중...")
                            # self.mav_port.ftp_close(seq_num=0)
                        elif res[0] == SUCCESS:
                            search_result.append([filename, 'SUCCESS', res[1]])
                            seq_num += 1
                            break
                        elif res[0] == FailErrno:
                            if res[1] == EACCES:
                                search_result.append([filename, 'EACCES'])
                            if res[1] == EIO:
                                search_result.append([filename, 'EIO'])
                            seq_num += 1
                            break
                        elif res[0] == SessionNotFound:
                            print("Session not found. reloading...")
                        elif res[0] == FileNotFound:
                            search_result.append([filename, 'FILEEXISTSERROR'])
                            break
                        else:
                            break

                st.append(sub)

        return search_result

    msg_buf = []
    # 구성된 트리를 dfs 탐색하는 함수
    # @input: root: 탐색할 트리의 루트 노드
    # @output: 불러온 파일 이름 및 다운로드 결과
    # description:
    def copy_data_from_UAV(self, root=""):
        st = []
        search_result = []

        if root == "":
            root = self.tree_root
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
                        res = self.get_file_by_name(filename)
                        if res[0] == RELOAD:
                            print("재요청중...")
                            #self.mav_port.ftp_close(seq_num=0)
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

    msg_buf = []

    # 파일명으로 Drone의 파일을 ftp 전송받는 함수
    # @input: filename(ex. /fs/microse/dataman), MavlinkPort
    # @output: file
    # require: PX4 기기와 사용자 PC가 연결되어 있어야 함
    def get_file_by_name(self, filename):

        filesize = 0
        # FTP 프로토콜
        mavMsg = {
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
                mavBuffer = self.mav_port.ftp_read(4096)
                if mavBuffer and len(mavBuffer) > 0:
                    print(mavBuffer)
                else:
                    break

            # 파일 이름 추출
            file = filename.split('/')[-1]
            if file[0] == '.':
                return [PASS]

            # OpenFile 메시지 전송 후 파일 크기 받아옴
            self.mav_port.ftp_write(opcode=OpenFileRO, data=filename, size=len(filename))
            total_size = 0
            offset = 0
            timeout = 0
            print(filename, "\n===============")

            # OpenFile 후 ACK 파싱
            while True:
                mavMsg['seq_number'] = 0
                mavBuffer = self.mav_port.ftp_read(4096)
                if mavBuffer and len(mavBuffer) > 0:
                    print(mavBuffer)
                    if mavBuffer['opcode'] == 129:  # 오류 처리
                        if mavBuffer['data'][0] == 2:  # 운영체제 사이드에서 오류
                            if mavBuffer['data'][1] == 13:  # Permission denied
                                print("Permission denied")
                                self.mav_port.ftp_close(seq_num=mavBuffer['seq_number'], session=0)
                                return [FailErrno, EACCES]

                        if mavBuffer['data'][0] == SessionNotFound:
                            print('session not found')
                            return [SessionNotFound]
                        if mavBuffer['data'][0] == 10:  # 파일이 존재하지 않을 시
                            print("File not found")
                            return [FileNotFound]

                        print("파일을 불러오는데 실패하였습니다.")
                        return [RELOAD]
                        break

                    else:
                        mavMsg = mavBuffer
                        break


            # OpenFile 성공시 데이터 길이 추출
            if len(mavMsg['data']) == 4:
                for i in range(4):
                    total_size += mavMsg['data'][i] * pow(256, i)
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


            # size가 0일시 cat으로 불러오기 시도
            if total_size == 0 and filename.split("/")[1] != 'dev' and filename.split("/")[1] != 'obj':
                if file == "mtd_params" or file == "mtd_waypoints":
                    f = open(file, 'wb')
                else:
                    f = open(file, 'w')
                param = "cat " + filename + "\n"
                print("cat parsing..")
                data = command(param, self.mav_port)
                data = data[data.find("\n")+1:]


                if file == "mtd_params" or file == "mtd_waypoints":
                    print(type(data))
                    data = data.encode()
                    print(type(data))
                    print("mtd_params: ", data)
                    f.write(data)
                else:
                    f.write(data)
                print("data:", data)
                f.close()
                res = [SUCCESS]

            # 파일 전송 요청
            else:
                f = open(file, 'wb')
                while True:
                    cur_seq = mavMsg['seq_number']
                    self.mav_port.ftp_write(opcode=ReadFile, session=mavMsg['session'], size=read_size, offset=offset,
                                             seq_number=mavMsg['seq_number'])

                    while True:
                        print(f"{filename}: {offset} of {total_size}")
                        mavBuffer = self.mav_port.ftp_read(4096)

                        if mavBuffer and len(mavBuffer) > 0:
                            last_time = time.time()
                            print(mavMsg)
                            mavMsg = mavBuffer
                            break

                    if mavMsg['opcode'] == 129:  # 파일 전송 도중 오류 처리
                        if mavMsg['data'][0] == 6:  # 파일 전송 완료
                            f.close()
                            if mavMsg['size'] == 0:
                                res = ['NO RESPONSE']
                            else:
                                res = [SUCCESS]
                            break
                        else:  # 다른 오류 발생 시
                            print(mavMsg)
                            print("파일을 불러오는 도중 오류가 발생하였습니다..")
                            res = [RELOAD]
                            break
                    else:  # 데이터 정상 수신
                        for c in mavMsg['data']:
                            f.write(c.to_bytes(1, byteorder='little'))

                    offset += read_size

        except serial.serialutil.SerialException as e:
            print(e)

        except KeyboardInterrupt:
            self.mav_port.ftp_close(seq_num=mavMsg['seq_number'], session=0)

        # ftp 세션 닫기
        self.mav_port.ftp_close(seq_num=mavMsg['seq_number'], session=0)

        return res

        # 파일명으로 crc값을 전송받는 함수
        # @input: filename(ex. /fs/microse/dataman), MavlinkPort
        # @output: crc
        # require: PX4 기기와 사용자 PC가 연결되어 있어야 함
    def get_crc_by_name(self, filename, seq_num):

        filesize = 0
        # FTP 프로토콜
        mavMsg = {
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
            # 버퍼 비우기
            while True:
                mavBuffer = self.mav_port.ftp_read(4096)
                if mavBuffer and len(mavBuffer) > 0:
                    print(mavBuffer)
                else:
                    break

            # OpenFile 메시지 전송 후 파일 크기 받아옴
            self.mav_port.ftp_write(opcode=CalcFileCRC32, data=filename, size=len(filename), seq_number=seq_num)
            total_size = 0
            offset = 0
            timeout = 0
            print(filename, "\n===============")

            # OpenFile 후 ACK 파싱
            while True:
                mavMsg['seq_number'] = 0
                mavBuffer = self.mav_port.ftp_read(4096)
                if mavBuffer and len(mavBuffer) > 0:
                    print(mavBuffer)
                    if mavBuffer['opcode'] == 129:  # 오류 처리
                        if mavBuffer['data'][0] == 2:  # 운영체제 사이드에서 오류
                            if mavBuffer['data'][1] == 5:
                                print("I/O Error")
                                return [FailErrno, EIO]
                            if mavBuffer['data'][1] == 13:  # Permission denied
                                print("Permission denied")
                                return [FailErrno, EACCES]
                            return[FailErrno, mavBuffer['data'][1]]

                        if mavBuffer['data'][0] == SessionNotFound:
                            print('session not found')
                            return [SessionNotFound]
                        if mavBuffer['data'][0] == 10:  # 파일이 존재하지 않을 시
                            print("File not found")
                            return [FileNotFound]

                        print("파일을 불러오는데 실패하였습니다.")
                        return [RELOAD]
                        break

                    else:
                        mavMsg = mavBuffer
                        crc = mavMsg['data'][0] + mavMsg['data'][1]*256 + mavMsg['data'][2]*pow(256,2) +mavMsg['data'][3]*pow(256,3)
                        res = [SUCCESS, crc]
                        break



        except serial.serialutil.SerialException as e:
            print(e)

        return res

    # Drone에 파일을 ftp 전송하는 함수
    # @input: filename(ex. /fs/microse/dataman): 드론 상에서의 저장 위치, filepath: 보낼 파일의 경로, MavlinkPort
    # @output: 실행 결과
    # require: PX4 기기와 사용자 PC가 연결되어 있어야 함
    def send_file_by_name(filename, filepath, mav_port):
        return

    def close(self):
        print("close port")
        while True:
            res = self.mav_port.ftp_close(seq_num=0)
            if res == 1:
                break
        self.mav_port.close()

