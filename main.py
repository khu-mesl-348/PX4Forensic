from timeit import default_timer as timer
import serial
from argparse import ArgumentParser
import os
from pymavlink import mavutil
from threading import Thread
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
            data = mav_serialport.read(4096)
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
                        mav_serialport.write(cur_line + '\n')
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


# MavlinkSerialPort 객체에 시리얼 연결을 수행하여 반환
# @input: -
# @output: MavlinkSerialPort
# require: PX4 기기와 사용자 PC가 연결되어 있어야 함
def SerialPort():
    # 시리얼 포트 자동 detect
    serial_list = mavutil.auto_detect_serial(preferred_list=['*FTDI*',
                                                             "*Arduino_Mega_2560*", "*3D_Robotics*", "*USB_to_UART*",
                                                             '*PX4*', '*FMU*', '*PX*'])

    for item in serial_list:
        print(item)

    if len(serial_list) == 0:
        print("Error: no serial connection found")
        return

    if len(serial_list) > 1:
        print('Auto-detected serial ports are:')
        for port in serial_list:
            print(" {:}".format(port))

    print('Using port {:}'.format(serial_list[0]))
    port = serial_list[0].device

    print("Connecting to MAVLINK...")
    try:
        mav_serialport = MavlinkSerialPort(port, baudrate=115200, devnum=10)  # 기본 baudrate 115200, 변경하는거 만들 필요 있음
        mav_serialport.write('\n')  # make sure the shell is started
        while True:
            data = mav_serialport.read(4096)
            if data and len(data) > 0:
                if data.find('nsh>') != -1:
                    break
        print('PX4 connect complete')
    except KeyboardInterrupt:
        print('Aborting')

    return mav_serialport


# PX4 기체에 명령어 전송
# @input:
#   param: 전송할 명령어
#   mav_serialport: serial에 연결된 MAVlinkSerialPort 객체
# @output: 명령어 실행 후 Shell message
# require: PX4 기기와 사용자 PC가 연결되어 있어야 함

def command(param, mav_serialport):
    mav_serialport.write(param)
    ret = ''
    while True:
        data = mav_serialport.read(4096)
        if data and len(data) > 0:

            if data.find('nsh>') != -1:
                # nsh> 제거
                data = data[:data.find('nsh>')]
                # 줄바꿈 제거
                ret += data
                ret = ret[:-1]
                break
            ret += data

    return ret

datalist = []
filelist = []
folderlist = []
#오류, 혹은 사용되지 않는 디렉토리 및 파일
blacklist = [' group/'] #

#command 실행 함수
def cmd_ls(mav_serialport):
    global datalist
    cmd = "ls\n"
    data = command(cmd, mav_serialport)

    if data.find("nsh:") != -1: # 오류 메시지 출력 
        print(data)
    datalist = data.split('\n')


def cmd_cd(param, mav_serialport):
    cmd = "cd " + param.replace("/", "") + "\n"
    print("cmd :", cmd)
    data = command(cmd, mav_serialport)

    if data.find("nsh:") != -1: # 오류 메시지 출력 
        print("error: ", data)
        cmd_ls(mav_serialport)
        for item in datalist:
            print(item)
        datalist.clear()
        return 1

    return 0
    
    
def cmd_cd_back(mav_serialport):
    cmd = "cd ..\n"
    command(cmd, mav_serialport)


# 트리 노드 생성
class Node:
    def __init__(self, data):
        self.data = data
        self.child = []
        self.parent = None

    def append_child(self, new_node):
        new_node.parent = self
        self.child.append(new_node)

class Tree:
    def __init__(self, mav_serialport):
        self.stack = []
        self.files = []
        self.mav_serialport = mav_serialport
        self.root = Node("/")

    # ls
    def dfs(self, root):
        self.stack.append(root)
        self.root.data = root
        cur = self.root
        while len(self.stack) != 0:
            print(self.stack)
            print("cur: ", cur.data)
            item = self.stack.pop()
            print("cur: ",cur.data)

            #print(item)
                
            if item == "..":
                if(len(self.stack) == 1 ): 
                    break
                cmd_cd_back(self.mav_serialport)
                if cur.data != '/':
                    cur = cur.parent
                continue

            elif "/" in item and item not in blacklist:
                cmd_cd(item, self.mav_serialport)
                self.stack.append("..")
                cmd_ls(self.mav_serialport)
                for next in cur.child:
                    print("next: ", next.data,"itm: ", item)
                    if next.data == item:
                        cur = next
                        break


            if(len(datalist) != 0):
                for idx, item in enumerate(datalist):
                    if idx < 2:
                        continue
                    self.stack.append(item)

                    leaf = Node(item)
                    cur.append_child(leaf)

            datalist.clear()

    # 구성된 트리를 dfs 탐색하는 함수
    def search(self):
        st = []
        st.append(self.root)

        while len(st) > 0:
            item = st.pop()
            for sub in item.child:
                filename = ''
                cur = sub
                if cur.data.find('/') == -1:
                    while cur.parent != None:
                        filename = cur.data.replace(" ", "") + filename
                        cur = cur.parent

                    # root 경로 추가
                    filename = '/'+filename

                    # 여기서 각 파일의 경로+파일명이 생성됩니다
                    print(filename)

                st.append(sub)
        
def main():

    # MAVLink 포트 연결
    mav_serialport = SerialPort()

    fd_in = sys.stdin.fileno()
    ubuf_stdin = os.fdopen(fd_in, 'rb', buffering=0)
    cur_line = ''

    # 실시간으로 Shell 사용할시
    #live_shell(mav_serialport)

    root = "/"
    tree = Tree(mav_serialport)

    while len(tree.stack) == 0:
        tree.dfs(root)
    tree.search()
    # while True:
    #     cmd = ubuf_stdin.readline().decode('utf8')
    #     data = command(cmd, mav_serialport)
    #     print(data)
        
    mav_serialport.close()

if __name__ == '__main__':
    main()