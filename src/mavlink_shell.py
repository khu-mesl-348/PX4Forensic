from pymavlink import mavutil
from src.MavSerialPort import MavlinkSerialPort

def get_serial_item():
    res = []
    # 시리얼 포트 자동 detect
    serial_list = mavutil.auto_detect_serial(preferred_list=['*FTDI*',
                                                             "*Arduino_Mega_2560*", "*3D_Robotics*", "*USB_to_UART*",
                                                             '*PX4*', '*FMU*', '*PX*'])
    if len(serial_list) == 0:
        print("Error: no serial connection found")
        return -1

    if len(serial_list) >= 1:
        print('Auto-detected serial ports are:')
        for port in serial_list:
            print(" {:}".format(port))
            res.append([port.device, port.description])

    return res


def connect_to_serial(port):
    # MAVLink 연결
    print("Connecting to MAVLINK...")
    try:
        mav_serialport = MavlinkSerialPort(port, baudrate=115200, devnum=10)  # 기본 baudrate 115200, 변경하는거 만들 필요 있음
        mav_serialport.write('\n')  # make sure the shell is started
        print('PX4 connect complete')

    except KeyboardInterrupt:
        print('Aborting')
        return -1
    return 1
