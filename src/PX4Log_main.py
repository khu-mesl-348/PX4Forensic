import struct
import copy
import sys
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
    MSG_TYPE_ADD_LOGGED_MSG = ord('A')
    MSG_TYPE_REMOVE_LOGGED_MSG = ord('R')
    MSG_TYPE_SYNC = ord('S')
    MSG_TYPE_DROPOUT = ord('O')
    MSG_TYPE_LOGGING = ord('L')
    MSG_TYPE_LOGGING_TAGGED = ord('C')
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
    
with open("test.ulg", "rb") as f:               
    data = f.read()

for i in range(8):
    unpack_result = struct.unpack(ULog._UNPACK_TYPES['uint8_t'][0], data[i:i+1])
    print(hex(unpack_result[0]))


f.close()

class Parser():
    def offset(self, data_len):
        self.data_len = data_len 

    def msg_header(self, msg_size, msg_type):
        self.msg_size = msg_size
        self.msg_type = msg_type

# Header section
class Header():
    def __init__(self, file_timestamp):
        self.magic_number = ULog.HEADER_BYTES
        self.version = 1
        self.timestamp = file_timestamp

# Definition section
class Definition(Parser):
    def __init__(self, msg_size, msg_type):
        self.msg_header(msg_size, msg_type)

    def def_B(self, compat_flags, incompat_flags, appended_offsets):
        self.compat_flags = compat_flags 
        self.incompat_flags = incompat_flags
        self.appended_offsets = appended_offsets

    def def_I(self, key_len, key, value):
        self.key_len = key_len
        self.key = key
        self.value = value

    def def_F(self, format):
        self.format = format

    def def_P(self, key_len, key, value):
        self.key_len = key_len
        self.key = key
        self.value = value

    def def_Q(self, default_types, key_len, key, value):
        self.default_types = default_types
        self.key_len = key_len
        self.key = key
        self.value = value
        
    def def_M(self, is_continued, key_len, key, value):
        self.is_continued = is_continued
        self.key_len = key_len
        self.key = key
        self.value = value

# Definition section
class Data(Parser):
    def __init__(self, msg_size, msg_type):
        self.msg_header(msg_size, msg_type)

    def data_A(self, multi_id, msg_id, message_name):
        self.multi_id = multi_id
        self.msg_id = msg_id
        self.message_name = message_name

    def data_D(self, multi_id, msg_id, message_name):
        self.multi_id = multi_id
        self.msg_id = msg_id
        self.message_name = message_name

    def data_L(self, multi_id, msg_id, message_name):
        self.multi_id = multi_id
        self.msg_id = msg_id
        self.message_name = message_name

    def data_O(self, multi_id, msg_id, message_name):
        self.multi_id = multi_id
        self.msg_id = msg_id
        self.message_name = message_name

