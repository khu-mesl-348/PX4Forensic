import sys
from PyQt5.QtWidgets import *
from src.mavlink_shell import get_serial_item
from src.MavPort import MavlinkPort
from src.FTPReader import FTPReader
from src.Mission.PX4MissionParser import missionParser
from src.Mission.tools import SerialPort
from src.PX4Mission import hash_sha1, hash_md5, createdTime, is_encrypted
from PyQt5 import uic
from os import environ
import os

def suppress_qt_warnings():   # 해상도별 글자크기 강제 고정하는 함수
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("PX4Forensic.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        filename = "./../src/dataman"
        parser_fd = os.open(filename, os.O_BINARY)

        self.setupUi(self)
        self.parser = missionParser(parser_fd)

        # port 연결
        serial_list = get_serial_item()
        for item in serial_list:
            portAction = QAction(item[0])
            portAction.triggered.connect(lambda: self.portClicked(item[0],item[1]))
            self.menu_port2.addAction(portAction)
        disconnAction = QAction("연결 끊기")
        portAction.triggered.connect(lambda: self.portClicked("close",""))
        self.menu_port2.addAction(disconnAction)

        if len(serial_list) != 0:
            self.mavPort = SerialPort(serial_list[0][0])
            self.label_connected.setText(f"connected: {serial_list[0][1]}({serial_list[0][0]})")
        else:
            self.mavPort = None
            self.label_connected.setText(f"unconnected")

        self.ftp = FTPReader(_port=self.mavPort)
        # Mission - radiobox 트리거 함수 연결

        self.radio_safepoint.toggled.connect(self.safeClicked)
        self.radio_geofencepoint.toggled.connect(self.geoClicked)
        self.radio_waypoint.toggled.connect(self.wayClicked)

        # 파일 정보 표시
        self.fileInfo("./../src/dataman")


        self.dataRefreshButton.clicked.connect(self.getFileFromUAV)


    def getFileFromUAV(self):
        self.ftp.copy_data_from_UAV()

    def fileInfo(self, filename):
        fd = os.open(filename, os.O_BINARY)
        if fd < 0:
            self.getFileFromUAV()
            fd = os.open(filename, os.O_BINARY)
            if fd < 0:
                return -1

        datamanId = self.parser.get_mission()[3]
        created = createdTime(filename)
        hashSha = hash_sha1(filename)
        hashMD5 = hash_md5(filename)
        encrypt = is_encrypted(self.parser.get_safe_points(), self.parser.get_fence_points(),
                               self.parser.get_mission_item(datamanId), self.parser.get_mission())
        if encrypt == 0:
            encrypt = "False"
        elif encrypt ==1 :
            encrypt = "True"

        header = ["created", "MD5", "SHA-1", "encrypted"]
        data = [created, hashSha,hashMD5,encrypt]

        self.tableWidget_file.setColumnCount(2)
        self.tableWidget_file.setRowCount(len(header))
        self.tableWidget_file.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_file.verticalHeader().setVisible(False)
        self.tableWidget_file.horizontalHeader().setVisible(False)

        for i in range(len(header)):
            self.tableWidget_file.setItem(i, 0, QTableWidgetItem(header[i]))
            self.tableWidget_file.setItem(i, 1, QTableWidgetItem(str(data[i])))

        self.tableWidget_file.resizeRowsToContents()
        self.tableWidget_file.resizeColumnsToContents()
        os.close(fd)

    def portCliked(self,port, des):
        if self.mavPort == None or port == "close":
            self.mavPort.close()

        if port != "close":
            self.mavPort = SerialPort(port)
            self.label_connected.setText(f"connected: {des}({port})")

    def safeClicked(self):
        safePoints = self.parser.get_safe_points()

        stat_headers = ["num_items", "update_counter"]
        column_headers = ['lat', 'lon', 'alt', 'frame']

        self.tableWidget_status.clearContents()
        self.tableWidget_point.clearContents()

        self.tableWidget_status.setColumnCount(len(stat_headers))
        self.tableWidget_status.setRowCount(1)
        self.tableWidget_status.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_status.setHorizontalHeaderLabels(stat_headers)
        self.tableWidget_status.verticalHeader().setVisible(False)

        self.tableWidget_point.setColumnCount(len(column_headers))
        self.tableWidget_point.setRowCount(len(safePoints)-1)
        self.tableWidget_point.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_point.setHorizontalHeaderLabels(column_headers)

        print(safePoints)
        for idx, item in enumerate(safePoints):

            for i, num in enumerate(item):
                if type(num) != "str":
                    item[i] = str(num)
            if idx == 0:
                self.tableWidget_status.setItem(idx, 0, QTableWidgetItem(item[0]))
                self.tableWidget_status.setItem(idx, 1, QTableWidgetItem(item[1]))
            else:
                self.tableWidget_point.setItem(idx-1, 0, QTableWidgetItem(item[0]))
                self.tableWidget_point.setItem(idx-1, 1, QTableWidgetItem(item[1]))
                self.tableWidget_point.setItem(idx-1, 2, QTableWidgetItem(item[2]))
                self.tableWidget_point.setItem(idx-1, 3, QTableWidgetItem(item[3]))

        self.tableWidget_point.resizeRowsToContents()

    def geoClicked(self):
        geoPoints = self.parser.get_fence_points()

        stat_headers = ["num_items", "update_counter"]
        column_headers = ['lat', 'lon', 'alt', 'vertex/radius', 'nav_cmd', 'frame']

        self.tableWidget_status.clearContents()
        self.tableWidget_point.clearContents()

        self.tableWidget_status.setColumnCount(len(stat_headers))
        self.tableWidget_status.setRowCount(1)
        self.tableWidget_status.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_status.setHorizontalHeaderLabels(stat_headers)
        self.tableWidget_status.verticalHeader().setVisible(False)

        self.tableWidget_point.setColumnCount(len(column_headers))
        self.tableWidget_point.setRowCount(len(geoPoints) - 1)
        self.tableWidget_point.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_point.setHorizontalHeaderLabels(column_headers)

        print(geoPoints)
        for idx, item in enumerate(geoPoints):
            print(item)
            for i, num in enumerate(item):
                if type(num) != "str":
                    item[i] = str(num)
            if idx == 0:
                self.tableWidget_status.setItem(idx, 0, QTableWidgetItem(item[0]))
                self.tableWidget_status.setItem(idx, 1, QTableWidgetItem(item[1]))
            else:
                self.tableWidget_point.setItem(idx-1, 0, QTableWidgetItem(item[0]))
                self.tableWidget_point.setItem(idx-1, 1, QTableWidgetItem(item[1]))
                self.tableWidget_point.setItem(idx-1, 2, QTableWidgetItem(item[2]))
                self.tableWidget_point.setItem(idx-1, 3, QTableWidgetItem(item[3]))
                self.tableWidget_point.setItem(idx-1, 4, QTableWidgetItem(item[4]))
                self.tableWidget_point.setItem(idx-1, 5, QTableWidgetItem(item[5]))

        self.tableWidget_point.resizeRowsToContents()

    def wayClicked(self):
        mission = self.parser.get_mission()
        print(mission)
        waypoints = self.parser.get_mission_item(mission[3])

        stat_headers = ["timestamp", 'current_seq', 'count', 'dataman_id']
        column_headers = ['lat', 'lon', 'time_inside/circle_radius', 'acceptance_radius/param[0]',
                    'loiter_radius/param[2]', 'yaw/param[3]','param[4]' ,'param[5]','altitude/param[6]', 'nav_cmd', 'do_jump_mission_index',
                    'do_jump_repeat_count', 'union', 'frame', 'origin', 'loiter_exit_xtrack',
                    'force_heading', 'altitude_is_relative', 'autocontinue', 'vtol_back_transition']

        self.tableWidget_status.clearContents()
        self.tableWidget_point.clearContents()

        self.tableWidget_status.setColumnCount(len(stat_headers))
        self.tableWidget_status.setRowCount(1)
        self.tableWidget_status.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_status.setHorizontalHeaderLabels(stat_headers)
        self.tableWidget_status.verticalHeader().setVisible(False)

        self.tableWidget_point.setColumnCount(len(column_headers))
        self.tableWidget_point.setRowCount(len(waypoints))
        self.tableWidget_point.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_point.setHorizontalHeaderLabels(column_headers)


        for i in range(4):
            if type(mission[i]) != 'str':
                mission[i] = str(mission[i])
            self.tableWidget_status.setItem(0, i, QTableWidgetItem(mission[i]))

        for idx, item in enumerate(waypoints):
            print(item)
            for i, num in enumerate(item):
                if type(num) != "str":
                    item[i] = str(num)
                self.tableWidget_point.setItem(idx, i, QTableWidgetItem(item[i]))
        self.tableWidget_point.resizeRowsToContents()

if __name__ == "__main__" :
    suppress_qt_warnings()
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()