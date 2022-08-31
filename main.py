from src.FTPReader import *


def main():
    ftp = FTPReader()
    print(ftp.copy_data_from_UAV())
    ftp.close()

if __name__ == '__main__':
    main()