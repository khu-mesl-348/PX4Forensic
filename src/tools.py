from pymavlink import mavutil
from src.MavPort import MavlinkPort



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
        mav_serialport = MavlinkPort(port, baudrate=115200, devnum=10)  # 기본 baudrate 115200, 변경하는거 만들 필요 있음
        mav_serialport.serial_write('\n')  # make sure the shell is started
        while True:
            data = mav_serialport.serial_read(4096)
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
    mav_serialport.serial_write(param)
    ret = ''
    while True:
        data = mav_serialport.serial_read(4096)
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
# 오류, 혹은 사용되지 않는 디렉토리 및 파일
blacklist = [' group/']  #


# command 실행 함수
def cmd_ls(mav_serialport):
    global datalist
    cmd = "ls\n"
    data = command(cmd, mav_serialport)

    if data.find("nsh:") != -1:  # 오류 메시지 출력
        print(data)
    datalist = data.split('\n')


def cmd_cd(param, mav_serialport):
    cmd = "cd " + param.replace("/", "") + "\n"
    print("cmd :", cmd)
    data = command(cmd, mav_serialport)

    if data.find("nsh:") != -1:  # 오류 메시지 출력
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