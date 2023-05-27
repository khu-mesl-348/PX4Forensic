from pymavlink import mavutil
import binascii
from crccheck.crc import Crcc16Mcrf4xx
class MavlinkPort:
    # 출처: PX4/Tools/mavlink.py
    '''an object that looks like a serial port, but
    transmits using mavlink SERIAL_CONTROL packets'''
    def __init__(self, portname, baudrate, devnum=0, debug=0):
        self.baudrate = baudrate
        self._debug = debug
        self.serial_buf = ''
        self.ftp_buf = []
        self.port = devnum
        self.debug("Connecting with MAVLink to %s ..." % portname)
        self.mav = mavutil.mavlink_connection(portname, autoreconnect=False, baud=baudrate)
        self.mav.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GENERIC, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
        print('Sending HEARTBEAT...')
        self.health = self.mav.wait_heartbeat(timeout=5)
        if self.health is None:
            print('Connection Failed')
            self.health = False
        else:
            self.debug("HEARTBEAT OK\n")
            self.debug("Locked serial device\n")
            self.health = True

    def debug(self, s, level=1):
        # write some debug text
        print("console: "+s)
        if self._debug >= level:
            print('debug: '+s)

    def set_port(self, portname, baudrate):
        self.close()
        self.mav = mavutil.mavlink_connection(portname, autoreconnect=True, baud=baudrate)
        self.mav.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GENERIC, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
        self.mav.wait_heartbeat()
        self.debug("HEARTBEAT OK\n")
        self.debug("Locked serial device\n")

    def serial_write(self, b):
        # write some bytes
        #self.debug("sending '%s' (0x%02x) of len %u\n" % (b, ord(b[0]), len(b)), 2)
        if b == "login\n":
            self.login_write("mesl", "1234")
            return
        while len(b) > 0:
            n = len(b)
            if n > 70:
                n = 70
            buf = [ord(x) for x in b[:n]]
            buf.extend([0]*(70-len(buf)))
            self.mav.mav.serial_control_send(self.port,
                                             mavutil.mavlink.SERIAL_CONTROL_FLAG_EXCLUSIVE |
                                             mavutil.mavlink.SERIAL_CONTROL_FLAG_RESPOND,
                                             0,
                                             0,
                                             n,
                                             buf)
            b = b[n:]

    def serial_close(self):
        self.mav.mav.serial_control_send(self.port, 0, 0, 0, 0, [0]*70)

    def serial_recv(self):
        # read some bytes into self.buf
        m = self.mav.recv_match(condition='SERIAL_CONTROL.count!=0',
                                type='SERIAL_CONTROL', blocking=True,
                                timeout=0.03)
        if m is not None:
            if self._debug > 2:
                print(m)
            data = m.data[:m.count]
            self.serial_buf += ''.join(str(chr(x)) for x in data)

    def serial_read(self, n):
        # read some bytes
        if len(self.serial_buf) == 0:
            self.serial_recv()
        if len(self.serial_buf) > 0:
            if n > len(self.serial_buf):
                n = len(self.serial_buf)
            ret = self.serial_buf[:n]
            self.serial_buf = self.serial_buf[n:]
            if self._debug >= 2:
                for b in ret:
                    self.debug("read 0x%x" % ord(b), 2)
            return ret
        return ''

    def ftp_write(self, opcode=0, data='', size=0, offset=0, session=0, seq_number=0):

        payload = []

        # write sequence
        for i in range(2):
            payload.append(seq_number % 256)
            seq_number = int((seq_number - seq_number % 256) / 256)

        # write session
        payload.append(session)

        # write opcode
        payload.append(opcode)

        # write size
        payload.append(size)

        # write req opcode
        payload.append(0)

        # write burst_complete
        payload.append(0)

        # write padding
        payload.append(0)

        # write offset
        for i in range(4):
            payload.append(offset % 256)
            offset = int((offset - offset % 256) / 256)

        # write data
        for x in data:
            payload.append(ord(x))


        # write some bytes
        self.debug("sending '%s' of len %u" % (payload,  len(payload)), 2)

        payload.extend([0] * (251 - len(payload)))
        self.mav.mav.file_transfer_protocol_send(0, 0, 0, payload)

    def ftp_recv(self):
        # read some bytes into self.buf
        m = self.mav.recv_match(type='FILE_TRANSFER_PROTOCOL', blocking=True,
                                timeout=0.03)

        if m is not None:
            if self._debug > 2:
                print(m.payload)
            self.ftp_buf.append(m.payload)

    def ftp_read(self, n):
        # read some bytes
        if len(self.ftp_buf) == 0:
            self.ftp_recv()
        if len(self.ftp_buf) > 0:
            data = self.ftp_buf[0]
            ret = {
                'seq_number': data[0] + data[1]*256,
                'session': data[2],
                'opcode': data[3],
                'size': data[4],
                'req_opcode': data[5],
                'burst_complete': data[6],
                'offset': data[8]+data[9]*256+data[10]*(256*256)+data[11]*(256*256*256),
                'data': data[12:12+data[4]]
            }
            self.ftp_buf.pop(0)
            if self._debug >= 2:
                for b in ret:
                    self.debug("read 0x%x" % ord(b), 2)
            return ret
        return []

    def close(self):
        self.mav.close()

    def ftp_close(self, seq_num, session=-1):
        if session>-1:
            self.ftp_write(opcode=1, seq_number=seq_num, session=session)
        else:
            self.ftp_write(opcode=2)

        while True:
            mavBuffer = self.ftp_read(4096)
            if mavBuffer and len(mavBuffer) > 0:
                print("terminate: ", mavBuffer)
                if mavBuffer['req_opcode'] == 2:
                    return 1
                else:
                    return -1
            else:
                pass
    
    def calculate_length(self,payload):
        return format(len(payload) // 2, '02x')


    def packetGenerator(self, msgid, seq, id,pw):
        global msgid_crc
        info = id + ":" + pw
        payload = info.encode()
        payload = str(binascii.hexlify(payload), 'ascii')
        stx = "fd"
        incFLAG = "00"
        cmpFLAG = "00"
        compID = str(format(0, "02x"))
        sysID = str(format(255, "02x"))
        magic = format(int('20'), '02x')
        msgid = format(int(msgid), '06x')
        msgid = msgid[-2:] + msgid[-4:-2] + msgid[0:2]
        length = self.calculate_length(payload)
        seq = format(seq, '02x')
        packet = length + incFLAG + cmpFLAG + seq + sysID + compID + msgid + payload
        print(packet)
        crc = Crcc16Mcrf4xx.calc(bytearray.fromhex(packet + magic))
        crc = str(format(crc, '04x'))
        crc = [crc[-2:], crc[0:2]]
        packet += crc[0] + crc[1]
        return stx + packet

    def login_write(self, id, pw):

        packet = self.packetGenerator('288',0,id, pw)

        # write some bytes
        self.debug("sending '%s' of len %u" % (packet,  len(packet)), 2)
        self.mav.write(bytes.fromhex(packet))

        