from src.MavPort import MavlinkPort
import  os, fnmatch

class SerialPort(object):
    '''auto-detected serial port'''
    def __init__(self, device, description=None, hwid=None):
        self.device = device
        self.description = description
        self.hwid = hwid

    def __str__(self):
        ret = self.device
        if self.description is not None:
            ret += " : " + self.description
        if self.hwid is not None:
            ret += " : " + self.hwid
        return ret

def auto_detect_serial_win32(preferred_list=['*']):
    '''try to auto-detect serial ports on win32'''
    try:
        from serial.tools.list_ports_windows import comports
        list = sorted(comports())
    except:
        return []
    ret = []
    others = []

    print('list: ', list)
    for port, description, hwid in list:
        matches = False
        p = SerialPort(port, description=description, hwid=hwid)
        for preferred in preferred_list:
            if fnmatch.fnmatch(description, preferred) or fnmatch.fnmatch(hwid, preferred):
                matches = True
        if matches:
            ret.append(p)
        else:
            others.append(p)
    if len(ret) > 0:
        return ret
    # now the rest
    ret.extend(others)
    return ret
        

        

def auto_detect_serial_unix(preferred_list=['*']):
    '''try to auto-detect serial ports on unix'''
    import glob
    glist = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + glob.glob('/dev/serial/by-id/*')
    ret = []
    others = []
    # try preferred ones first
    for d in glist:
        matches = False
        for preferred in preferred_list:
            if fnmatch.fnmatch(d, preferred):
                matches = True
        if matches:
            ret.append(SerialPort(d))
        else:
            others.append(SerialPort(d))
    if len(ret) > 0:
        return ret
    ret.extend(others)
    return ret

def auto_detect_serial(preferred_list=['*']):
    '''try to auto-detect serial port'''
    # see if 
    if os.name == 'nt':
        
        return auto_detect_serial_win32(preferred_list=preferred_list)
    return auto_detect_serial_unix(preferred_list=preferred_list)

def get_serial_item():
    res = []
    # 시리얼 포트 자동 detect
    serial_list = auto_detect_serial(preferred_list=['*FTDI*',
                                                             "*Arduino_Mega_2560*", "*3D_Robotics*", "*USB_to_UART*",
                                                             '*PX4*', '*FMU*', '*PX*'])
    print('serial list: ', serial_list)
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
        mav_serialport = MavlinkPort(port, baudrate=115200, devnum=10)  # 기본 baudrate 115200, 변경하는거 만들 필요 있음
        mav_serialport.write('\n')  # make sure the shell is started
        print('PX4 connect complete')

    except KeyboardInterrupt:
        print('Aborting')
        return -1
    return 1
