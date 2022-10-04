from ui.PX4Forensic import PX4Forensic
from src.FTPReader import FTPReader
from src.Mission.tools import SerialPort, command

if __name__ == '__main__':
    #p = SerialPort('COM5')

    #ftp = FTPReader(_port=p)
    #ftp.live_shell()

    PX4Forensic()
    