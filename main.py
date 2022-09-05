from src.FTPReader import *
from src.Mission.PyMavlinkCRC32 import crc


def main():
    ftp = FTPReader()
    #ftp.copy_data_from_UAV()
    Crc = crc()
    mtd0 = ftp.get_crc_by_name('/dev/mtdblock0', 0)
    mtd1 = ftp.get_crc_by_name('/dev/mtdblock1', 1)
    print(mtd0, mtd1)
    print(mtd0[1],  Crc.crc32Check('./dev/mtdblock0', mtd0[1]))
    print(mtd1[1], Crc.crc32Check('./dev/mtdblock1', mtd1[1]))

    return
    res = ftp.get_crc_from_UAV()
    for item in res:
        if item[2] != 0:
            print(item[0], item[2], Crc.crc32Check('./'+item[0],item[2]))

if __name__ == '__main__':
    main()