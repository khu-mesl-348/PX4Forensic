import struct
import copy
import sys
from this import d
import numpy as np

# 파이썬 버전 확인
if sys.hexversion >= 0x030000F0:
    _RUNNING_PYTHON3 = True
    def _parse_string(cstr, errors='strict'):
        return str(cstr, 'utf-8', errors)
else:
    _RUNNING_PYTHON3 = False
    def _parse_string(cstr):
        return str(cstr)

# ULog 파일 데이터
class ULog():

    #Constant bytes
    HEADER_BYTES = b'\x55\x4c\x6f\x67\x01\x12\x35'
    SYNC_BYTES = b'\x2F\x73\x13\x20\x25\x0C\xBB\x12'

    # message types
    MSG_TYPE_FORMAT = ord('F')
    MSG_TYPE_DATA = ord('D')
    MSG_TYPE_INFO = ord('I')
    MSG_TYPE_INFO_MULTIPLE = ord('M')
    MSG_TYPE_PARAMETER = ord('P')
    MSG_TYPE_PARAMETER_DEFAULT = ord('Q')
    MSG_TYPE_SYNC = ord('S')
    MSG_TYPE_DROPOUT = ord('O')
    MSG_TYPE_LOGGING = ord('L')
    MSG_TYPE_FLAG_BITS = ord('B')

    _UNPACK_TYPES = {
        'int8_t':   ['b', 1, np.int8],
        'uint8_t':  ['B', 1, np.uint8],
        'int16_t':  ['h', 2, np.int16],
        'uint16_t': ['H', 2, np.uint16],
        'int32_t':  ['i', 4, np.int32],
        'uint32_t': ['I', 4, np.uint32],
        'int64_t':  ['q', 8, np.int64],
        'uint64_t': ['Q', 8, np.uint64],
        'float':    ['f', 4, np.float32],
        'double':   ['d', 8, np.float64],
        'bool':     ['?', 1, np.int8],
        'char':     ['c', 1, np.int8]
        }

    def __init__(self):
        self._file_Corrupt = False # 파일 호환
        self._encryption = False # 암호화
        self._fileCreationDate = False # 파일 생성 날짜
        self._fileHash = False # 파일 해시값(?)

    def byte_to_string(self, data, datasize):
        _string = ""
        _data = []
        # print("data: ", len(data))
        # print("datasize: ", datasize)
        
        for i in range(datasize):
            _data.append(data[i])

        for j in _data:
            result = chr(j)
            _string = _string + result

        # print(_string)
        return _string

    def set_header(self, header_data):    
        self._header = Message_Header()
        self._header.size_ini(header_data)

    def get_header(self):
        return self._header

class Message_Header():
    def __init__(self):
        self.msg_size = 0
        self.msg_type = 0

    def size_ini(self, data):
        self.msg_size = struct.unpack('H', data[0:2])[0] 
        self.msg_type = struct.unpack('B', data[2:3])[0]

    def get_size(self):
        return self.msg_size

    def get_type(self):
        return self.msg_type

class Type(ULog):

    def __init__(self, data):
        self.set_header(data[0:3])
        if self.get_header().get_type == self.MSG_TYPE_FORMAT:
            _data = Def_Format(data)
            return _data
        elif self.get_header().get_type == self.MSG_TYPE_DATA:
            _data = Data_D(data)
            return _data
        elif self.get_header().get_type == self.MSG_TYPE_INFO:
            _data = Def_Info(data)
            return _data
        elif self.get_header().get_type == self.MSG_TYPE_INFO_MULTIPLE:
            _data = Def_Info(data)
            return _data
        elif self.get_header().get_type == self.MSG_TYPE_PARAMETER:
            _data = Def_Param(data)
            return _data
        elif self.get_header().get_type == self.MSG_TYPE_LOGGING:
            _data = Data_Log(data)
            return _data
        elif self.get_header().get_type == self.MSG_TYPE_DROPOUT:
            _data = Data_DropOut(data)
            return _data
        else:
            print("type error: 식별할 수 없는 메시지 헤더 타입이 존재합니다.")
            print(_data)
            return -1

# Header section
class Header(ULog):
    def __init__(self):
        self.magic_number = self.HEADER_BYTES
        self.version = 1 
        self.timestamp = 0

    def header_data(self, data):
        self.magic_number = struct.unpack('BBBBBBB', data[0:7])
        self.version = struct.unpack('B', data[7:8])
        self.timestamp = struct.unpack('BBBBBBBB', data[8:16])

        # magic number check
        if self.magic_number != self.HEADER_BYTES:
            print("err: magic number is different.")
            return -1

        # version check
        if self.version != 1: 
            print("warning: The ULog file version is different. Targeting version is '1'")
            print("file version: ", self.version)

        return 0

    # file timestamp
    def print_file_timestamp(self): 
        return self.timestamp

# Definition section
# B type message
class Def_B(ULog):
    def __init__(self, data, header):
        self.compat_flags
        self.incompat_flags
        self.appended_offsets
        
# Definition section. Format
# F type message 
class Def_Format(ULog):
    def __init__(self, data):
        self.set_header(data[0:3])
        format_data = self.byte_to_string(data, self.get_header().get_size).split(':')
        self.topic_name = format_data[0]
        self.topic_data = format_data[1].split(';')

    def format_data(self):
        return self.topic_data

# Definition section. Info
# I type, M type message
class Def_Info(ULog):
    def __init__(self, data, info_multiple = False):
        self.set_header(data[0:3])
        # M type message(multiple info)
        if info_multiple == True:
            self.is_continued = struct.unpack('B', data[0:1])[0]
            data = data[1:]

        self.key_len = struct.unpack('B', data[3:4])[0]
        self.key = self.byte_to_string(data[4:], self.key_len) # return type: string
        data = data[(4 + self.key_len):]
        self.value = self.byte_to_string(data, (self.get_header().get_size() -1 - self.key_len)) # return type: string

    def print_info(self):
        print(self.key, ": ", self.value)

# Definition section. Parameter
# P type, Q type message
class Def_Param():
    def __init__(self, data, default_type = False):
        self.key_len
        self.key
        self.value

# Data section
# D type message
# 실제 로그 데이터
class Data_D():
    def __init__(self, data, header):
        self.d_type = self.msg_header.msg_type
        self.multi_id = data.multi_id
        self.msg_id = data.msg_id
        self.message_name = data.message_name
        self.d_timestamp = data.d_timestamp

# Data section
# L type message
# 로그 메시지 출력
class Data_Log():
    def __init__(self, data):
        self.log_level 
        self.timestamp
        self.message

    def log_level_str(self):
        return {ord('0'): 'EMERGENCY',
                ord('1'): 'ALERT',
                ord('2'): 'CRITICAL',
                ord('3'): 'ERROR',
                ord('4'): 'WARNING',
                ord('5'): 'NOTICE',
                ord('6'): 'INFO',
                ord('7'): 'DEBUG'}.get(self.log_level, 'UNKNOWN')

# Data section
# L type message
# 로그 메시지 손실 발생 시, 발생 경과 시간 출력
class Data_DropOut():
    def __init__(self, data, header, duration):
        self.duration

#ULog 파일 열기
with open("test.ulg", "rb") as f:               
    data = f.read()

def main(data):
    data = data[59:118]
    a = Def_Info(data)
    a.print_info()

main(data)

f.close()  

pointer = 0

test = [0x46, 0x61, 0x69, 0x72, 0x73, 0x70, 0x65, 0x65, 0x64, 0x5F, 0x76, 0x61, 0x6C, 0x69, 0x64, 0x61, 0x74, 0x65, 0x64, 0x3A, 0x75, 0x69, 0x6E, 0x74, 0x36, 0x34, 0x5F, 0x74, 0x20, 0x74, 0x69, 0x6D, 0x65, 0x73, 0x74, 0x61, 0x6D, 0x70, 0x3B, 0x66, 0x6C, 0x6F, 0x61, 0x74]
int_test = []




# 순차적으로 파일 읽기
# ToDo: 오프셋 점프
# ToDo: Definition type value들 저장
# ToDo: Data type 읽고 저장











