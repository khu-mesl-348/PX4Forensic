import os
import csv
import subprocess
import struct
from this import d
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# os.system('ulog_info fs/microsd/log/2022-07-18/09_39_09.ulg')  #info

# os.system('ulog_params fs/microsd/log/2022-07-18/09_39_09.ulg') #params

# os.system('ulog_messages fs/microsd/log/2022-07-18/09_39_09.ulg') # log message
filepath = "C:/Users/youngbin/Desktop/PX4Forensic/fs/microsd/log" #절대경로

def readCSV(filename):
        f = open(filename, 'r', encoding = "utf-8")
        obj = csv.reader(f)
        cnt = 0
        
        for line in obj:
            cnt = 1
            result = line
            if cnt == 1:
                break

        return result

def searchLogFile():
    print_log_list = []
    for dir in os.listdir(filepath):
        d = os.path.join(filepath, dir)
        if os.path.isdir(d):
            for file in os.listdir(d):
                f = os.path.join(d, file)
                print_log_list.append(f)
                
    return(print_log_list)


def byte_to_string(data):
        _string = ""
        _data = []

        for i in range(len(data)):
            _data.append(data[i])

        for j in _data:
            result = chr(j)
            _string = _string + result

        # print(_string)
        return _string

# shell command로 작동하는 함수
def shell_log_info():
    return 0

def shell_log_params(filepath):
    _listData = []
    cmd = ['ulog_params', filepath]
    fd_popen = subprocess.Popen(cmd, stdout= subprocess.PIPE).stdout
    data = fd_popen.read().strip()
    stringData = byte_to_string(data)
    listData = stringData.split('\r\n')
    fd_popen.close()

    for i in listData:
        _listData.append(i.split(','))

    return _listData


def shell_log_messages(filepath):

    cmd = ['ulog_messages', filepath]
    fd_popen = subprocess.Popen(cmd, stdout= subprocess.PIPE).stdout
    data = fd_popen.read().strip()
    stringData = byte_to_string(data)
    listData = stringData.split('\r\n')
    fd_popen.close()

    return listData


def shell_ulog_2_csv(filepath):
    # os.system('ulog2csv fs/microsd/log/2022-07-18/09_39_09.ulg')
    with open('output.txt', 'wb') as f:
        out = subprocess.run(['ulog2csv', filepath], capture_output=True, text = True)
        f.write(out.stdout)

#ULog 파일 헤더
class Header():

    HEADER_BYTES = b'\x55\x4c\x6f\x67\x01\x12\x35'

    def __init__(self, data):
        self.magic_number = struct.unpack('BBBBBBB', data[0:7])
        self.version = 1 
        self.timestamp = 0

    def header_data(self, data):
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


