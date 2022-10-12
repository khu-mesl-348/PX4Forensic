import struct

from src.MavPort import MavlinkPort 
from pymavlink import mavutil

def main():
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

    m = MavlinkPort(port, baudrate=57600, devnum=10)  # 기본 baudrate 115200, 변경하는거 만들 필요 있음
    m.login_write("sju0924","1234")

if __name__ == '__main__':
    main()