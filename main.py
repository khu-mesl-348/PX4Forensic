from timeit import default_timer as timer
import serial
from argparse import ArgumentParser
import os
from pymavlink import mavutil
from threading import Thread
from src.MavSerialPort import MavlinkSerialPort
import sys



def main():
    # 시리얼 포트 자동 detect
    serial_list = mavutil.auto_detect_serial(preferred_list=['*FTDI*',
        "*Arduino_Mega_2560*", "*3D_Robotics*", "*USB_to_UART*", '*PX4*', '*FMU*', '*PX*'])

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

    # MAVLink 연결
    print("Connecting to MAVLINK...")
    try:
        mav_serialport = MavlinkSerialPort(port, baudrate=115200, devnum=10) # 기본 baudrate 115200, 변경하는거 만들 필요 있음
        mav_serialport.write('\n')  # make sure the shell is started
        print('PX4 connect complete')
    except KeyboardInterrupt:
        print('Aborting')

    # Drone -> GCS로 보내는 MAVLink Shell Message 받을 때 사용.
    def read():
        while True:
            data = mav_serialport.read(4096)
            if data and len(data) > 0:
                sys.stdout.write(data)

    try:
        fd_in = sys.stdin.fileno()
        ubuf_stdin = os.fdopen(fd_in, 'rb', buffering=0)
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
                mav_serialport.mav.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GENERIC, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
                next_heartbeat_time = heartbeat_time + 1

    except serial.serialutil.SerialException as e:
        print(e)

    except KeyboardInterrupt:
        mav_serialport.close()

    read_th.join()
    mav_serialport.close()


if __name__ == '__main__':
    main()