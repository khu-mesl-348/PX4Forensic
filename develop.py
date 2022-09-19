import struct

from src.FTPReader import FTPReader
from src.Mission.PyMavlinkCRC32 import crc
from src.Mission.tools import SerialPort

def main():
    ftp = FTPReader(_port=SerialPort())

    ftpcrc = ftp.get_crc_by_name("/fs/microsd/dataman",0)
    Crc = crc()
    print(ftpcrc)
    print(Crc.crc32Check(filename="./fs/microsd/dataman", checksum=ftpcrc[1]), ftpcrc[1])

if __name__ == '__main__':
    main()