import struct

from src.MavPort import MavlinkPort
from src.Mission.tools import command
from pymavlink import mavutil
import hashlib
import binascii

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

    print(HMAC_calc("/fs/microsd/dataman", m))

def str_to_hex(s):
    res = 0
    a = [ord(i) for i in s]
    for i in a:
        res = (res << 8) + i
    return str(hex(res))[2:]

def HMAC_calc(filename, m):

    command("cd /\n", m)
    s = command("cat " + filename + "h\n", m).split("\n")[1]

    s = s[40:68]
    res = 0
    a = [ord(i) for i in s]
    for i in a:
        res = (res << 8) + i
    hmac_rec = str(hex(res))[2:]
    print("received hmac file: ",hmac_rec)

    h = hashlib.sha3_224()
    plain = open("." + filename, 'rb').read()
    plain = plain + b"mesl:1234"
    h.update(plain)
    hmac_cur = h.hexdigest()
    print("hmac of current file: ",hmac_cur)

    return hmac_rec == hmac_cur

if __name__ == '__main__':
    main()