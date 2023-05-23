from ui.PX4Forensic import PX4Forensic
from src.FTPReader import FTPReader
from src.Mission.tools import SerialPort, command

if __name__ == '__main__':
    # shell command에 직접 접속할때 주석을 푸세요
    # p = SerialPort()
    # ftp = FTPReader(_port=p)
    # ftp.live_shell()

    # 프로그램 실행
    PX4Forensic()
    
    
    