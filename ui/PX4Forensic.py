import sys
import os.path
import getpass
import glob
import hashlib
import platform
from PyQt5.QtWidgets import *
from src.mavlink_shell import get_serial_item
from src.FTPReader import FTPReader
from src.Mission.PyMavlinkCRC32 import crc
from src.Mission.PX4MissionParser import missionParser
from src.Mission.tools import SerialPort, command

#TODO: mission, logger 파일 검증 함수 분리
from src.PX4Mission import hash_sha1, hash_md5, createdTime, dataman_is_encrypted #mission
from src.PX4Log import hash_sha1, hash_md5, createdTime, is_encrypted # logger
from src.Logger.PX4LogParser import *

import csv
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QVariant

from PyQt5 import uic
from os import environ
import os
from matplotlib import patches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from haversine import inverse_haversine, Direction, Unit
import pandas as pd
from pandas import Series, DataFrame
from ui.PX4ForensicParameter import Parameterclass

# Use if it have to set port manually
# if you use linux os, check your serial port that connected with px4
# example: Serial = '/dev/ttyACM0'
Serial = None

def suppress_qt_warnings():   # 해상도별 글자크기 강제 고정하는 함수
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("ui/PX4Forensic.ui")[0]
download_class = uic.loadUiType("ui/downloadProgress.ui")[0]

#CSV 파일 존재 유무 확인
username = getpass.getuser()
dirpath = 'C:/Users/' + username + '/Desktop/PX4Forensic/fs/microsd/log/2022-07-18/'
fileExe = '*.csv'
csvlist = glob.glob(dirpath+fileExe)
if csvlist == []:
    shell_ulog_2_csv()


#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.parameter_ui = Parameterclass(self.parameterList, self.parameterDescription, self.parameterValue, self.parameterRange, self.parameterInformation)
        self.progressbar = QProgressBar()
        self.statusbar.addPermanentWidget(self.progressbar)
        self.step = 0
        self.modulePath = ""
        self.tabWidget.currentChanged.connect(self.onChange)
        self.clicked_log = ""
        self.parent_log = ""
        self.mavPort = None
        self.label_connected.setText(f"unconnected")
        self.login = None
        self.ftp = None

        self.connectSerial(serial=Serial)
        # 로고
        self.initUI()
     
        # 로그 리스트 객체 생성
        self.LogTree()


        self.dataman = "./fs/microsd/dataman"

        try:
            parser_fd = os.open(self.dataman, os.O_BINARY)
            self.parser = missionParser(parser_fd)
            # 파일 정보 표시(mission)
            self.fileInfo(self.dataman, self.tableWidget_file)
        except FileNotFoundError as e:
            self.getFileFromUAV()
            parser_fd = os.open(self.dataman, os.O_BINARY)
            self.parser = missionParser(parser_fd)
            pass
        except AttributeError as a:
            print(a)            
            parser_fd = os.open(self.dataman,0)
            self.parser = missionParser(parser_fd)

        # Mission - radiobox 트리거 함수 연결
        self.radio_safepoint.toggled.connect(self.safeClicked)
        self.radio_geofencepoint.toggled.connect(self.geoClicked)
        self.radio_waypoint.toggled.connect(self.wayClicked)

        self.dataRefreshButton.clicked.connect(self.getFileFromUAV)
        self.loginButton.clicked.connect(self.loginClicked)

        self.fig = plt.Figure(figsize=(1,1))
        self.canvas = FigureCanvas(self.fig)

        self.log_fig = plt.Figure(figsize=(1,1))
        self.log_canvas = FigureCanvas(self.log_fig)
        
        self.tabWidget.setCurrentIndex(0)
        
    def initUI(self):
        self.setWindowTitle('PX4ForensicTool')
        self.setWindowIcon(QIcon('drone.png'))
        self.setGeometry(300,300,300,200)
        self.show()
    
    def returnClickedItem(self, tw):
        return(tw.text())

    def connectSerial(self, serial = None):
        if serial is not None:
            self.mavPort = SerialPort(serial)
            self.label_connected.setText(f"connected: {serial}")
        elif serial is None:
            # port 연결
            serial_list = get_serial_item()

            if len(serial_list) != 0:
                if serial_list[0][0].find("통신 포트") > 0:
                    return -1
                self.mavPort = SerialPort(serial_list[0][0])
                self.label_connected.setText(f"connected: {serial_list[0][1]}({serial_list[0][0]})")
            else:
                self.mavPort = None
                self.label_connected.setText(f"unconnected")

        self.login = self.loginCheck()
        self.ftp = FTPReader(_port=self.mavPort)

        return 1

    def LogTree(self):
     
        #파일 이름
        self.log_treeWidget.setHeaderLabels(["ULog File"])
        self.log_treeWidget.header().setVisible(True)
        self.log_treeWidget.setAlternatingRowColors(True)

        pathsym = ""
        if platform.system() == "Linux":
            pathsym = "/"
        elif platform.system()  == "Windows":
            pathsym = "\\"


        self.log_list = searchLogFile()
        print(type(platform.system()))
        date_dirname = self.log_list[0].split(pathsym)[1]
        date_dir = QTreeWidgetItem(self.log_treeWidget)
        date_dir.setText(0, date_dirname)
        ulgname = QTreeWidgetItem(date_dir)
        ulgname.setText(0, self.log_list[0].split(pathsym)[2])

        for i in range(len(self.log_list)):
            ll = self.log_list[i]
            tmp_date_dirname = ll.split(pathsym)[1]

            if tmp_date_dirname != date_dirname:
                date_dirname = tmp_date_dirname
                date_dir = QTreeWidgetItem(self.log_treeWidget)
                date_dir.setText(0, date_dirname)

            if ll.find('csv')!= -1:
                ulgname = ll.split(pathsym)[2]
                set_ulgname = ulgname.replace('.csv','')
                set_ulgname = set_ulgname[9:]
                log_file = QTreeWidgetItem(date_dir)
                log_file.setText(0, set_ulgname)

                result = readCSV(ll)
                result.remove('timestamp')

                for j in range(len(result)):
                    topic_list = QTreeWidgetItem(log_file)
                    result[j]
                    topic_list.setText(0, result[j])
        
        self.log_treeWidget.itemClicked.connect(self.getCurrentItems)
        self.log_treeWidget.itemClicked.connect(self.LogItemClicked)

    def loginCheck(self):
        res = command("integrity_tools login\n", self.mavPort)
        print(res.split("\n")[1])
        if res.split("\n")[1] == "true":
            self.ID.setText("")
            self.PW.setText("")
            self.ID.setDisabled(True)
            self.PW.setDisabled(True)
            self.loginButton.setText("logout")
            return True
        else:
            return False

    def HMAC_calc(self, filename):
        command("cd /\n", self.mavPort)
        s = command("cat " + filename.strip(".") + "h\n", self.mavPort).split("\n")[1]
        print("received raw: ", s)
        s = s[40:68]

        res = 0
        a = [ord(i) for i in s]
        for i in a:
            res = (res << 8) + i
        hmac_rec = str(hex(res))[2:]
        print("received hmac file: ", hmac_rec)

        h = hashlib.sha3_224()
        plain = open(filename, 'rb').read()
        plain = plain + b"mesl:1234"
        h.update(plain)
        hmac_cur = h.hexdigest()
        print("hmac of current file: ", hmac_cur)

        return hmac_rec == hmac_cur

    def loginClicked(self):
        if not self.login:
            _id = self.ID.text()
            _pw = self.PW.text()

            print("integrity_tools login " + _id+" " + _pw)

            res = command("integrity_tools login " + _id+" " + _pw+"\n", self.mavPort)
            self.loginLabel.setText(res.split("\n")[1])
            print(res)

            if self.loginCheck():
                self.login = True
                self.ID.setText("")
                self.PW.setText("")
                self.ID.setDisabled(True)
                self.PW.setDisabled(True)
                self.loginButton.setText("logout")

        else:
            res = command("integrity_tools login 0 0" + "\n", self.mavPort)
            print(res)
            self.loginLabel.setText("login")
            res = command("integrity_tools login\n", self.mavPort)
            print(res)
            self.ID.setEnabled(True)
            self.PW.setEnabled(True)
            self.loginLabel.setText("")
            self.loginButton.setText("login")
            self.login = False


    def getCurrentItems(self):
        if self.log_treeWidget.indexOfTopLevelItem(self.log_treeWidget.currentItem()) == -1:
            self.parent_log = self.log_treeWidget.currentItem().parent().text(0)

    def LogItemClicked(self, tl, col):
        self.clicked_log = tl.text(col)
        self.LogGraph()

    def LogGraph(self):

        #로그 그래프 객체 설정
        self.logGraph.addWidget(self.log_canvas)

        self.log_fig.clf()
        ax = self.log_fig.add_subplot(111)

        username = getpass.getuser()
        dirpath = 'C:/Users/' + username + '/Desktop/PX4Forensic/fs/microsd/log/2022-07-18/'
        csvfile = '09_39_09_'+ self.parent_log + '.csv'
        logpath = dirpath + csvfile
        
        if os.path.isfile(logpath) == True:
            df = pd.read_csv(logpath)

            df_timestamp = df['timestamp']
            df_log = df[str(self.clicked_log)]
            ax.plot(df_timestamp, df_log)
            ax.set_xlabel("timestamp")

            # ax.plot(df['timestamp'], df[self.clicked_log])
            # ax.set_xlabel("timestamp")

            self.log_fig.tight_layout()
            self.log_canvas.show()
            self.log_canvas.draw()
        else:
            print("해당 경로에 CSV 파일이 없습니다.")
            

    #TODO: 로그 데이터 경로 수정
    def onChange(self):
        tabIndex = self.tabWidget.indexOf(self.tabWidget.currentWidget())
        #비행 데이터

        if tabIndex == 1:
            self.modulePath = "./fs/microsd/dataman"
            

        #로그 데이터

        elif tabIndex == 2:
            username = getpass.getuser()
            self.modulePath = "C:/Users/" + username  + "/Desktop/PX4Forensic/fs/microsd/log/2022-07-18/09_39_09.ulg"   
            #정보 출력
            self.fileInfo(self.modulePath, self.tableWidget_file_log)
            self.logParams(self.tableWidget_log_params, self.modulePath)
            self.logMessages(self.tableWidget_log_messages, self.modulePath)
                        
        #설정 데이터
        elif tabIndex == 3:
            self.parameter_ui.show_parameter_list()

    def drawGraph(self, x, y, v, nav_cmd, title):
        print(x, y)

        # 그래프 객체 설정
        self.graphLayout.addWidget(self.canvas)
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        ax.set_title(title)
        if title == "safe points":
            ax.scatter(x, y)
            for i in range(len(x)):
                ax.annotate(i + 1, (x[i], y[i]))

        elif title == "fence points":
            ax.scatter(x, y)
            for i in range(len(x)):
                ax.annotate(i + 1, (x[i], y[i]))
            idx = 0
            maxidx = len(x)
            while idx < maxidx:
                print(idx, nav_cmd[idx])
                if nav_cmd[idx] == 5001 or nav_cmd[idx] == 5002:
                    ax.plot(x[idx:int(idx+v[idx])]+[x[idx]], y[idx:int(idx+v[idx])]+[y[idx]])
                    idx += int(v[idx])

                elif nav_cmd[idx] == 5003 or nav_cmd[idx] == 5004:

                    width = float(round(abs(x[idx]-inverse_haversine((y[idx], x[idx]), v[idx], Direction.WEST, unit=Unit.METERS)[1]), 10))
                    height = float(round(abs(y[idx]-inverse_haversine((y[idx], x[idx]), v[idx], Direction.NORTH, unit=Unit.METERS)[0]), 10))
                    draw_oval = patches.Ellipse((x[idx], y[idx]), width*2, height*2, fill=False, color='blue')

                    print("ih: ",inverse_haversine((y[idx], x[idx]), v[idx], Direction.WEST, unit=Unit.METERS))
                    x.append(x[idx]+width)
                    x.append(x[idx]-width)
                    y.append(y[idx] + height)
                    y.append(y[idx] - height)
                    ax.add_patch(draw_oval)
                    idx += 1

        elif title == "waypoints":
            way_x = []
            way_y = []
            way_num = []
            for i,item in enumerate(x):
                if v[i] == 2:
                    continue
                else:
                    way_x.append(x[i])
                    way_y.append(y[i])
                    way_num.append(i)

            ax.scatter(way_x, way_y)
            ax.plot(way_x,way_y)
            for i in range(len(way_x)):
                ax.annotate(way_num[i]+1, (way_x[i], way_y[i]))

            x = way_x
            y = way_y

        print(x, y)
        x_blank = (max(x) - min(x)) / 10
        y_blank = (max(y) - min(y)) / 10
        x_min = min(x) - x_blank
        x_max = max(x) + x_blank
        y_min = min(y) - y_blank
        y_max = max(y) + y_blank
        ax.grid()


        ax.axis([x_min, x_max, y_min, y_max])
        self.fig.tight_layout()
        self.canvas.show()
        self.canvas.draw()

        return


    def getFileFromUAV(self):

        if self.ftp is None:
            res = self.connectSerial()
            if res == -1:
                QMessageBox.about(self, '연결 오류', 'PX4와 연결되어 있지 않습니다.')
                return -1
        self.radio_safepoint.setDisabled(True)
        self.radio_geofencepoint.setDisabled(True)
        self.radio_waypoint.setDisabled(True)
        self.dataRefreshButton.setDisabled(True)

        st = []
        root = self.ftp.tree_root
        search_result = []
        st.append(root)
        i = 0
        while len(st) > 0:
            item = st.pop()
            # item = 부모 노드
            # item이 디렉토리면, chdir(item.data)
            # item이 파일이면, 아래 과정 무시

            if item != root:
                if item.data.find('/') != -1:
                    while (not os.path.exists(item.data)):
                        os.chdir("..")
                    os.chdir(item.data)

            for sub in item.child:

                # sub = 자식 노드
                # sub이 디렉토리면, mkdir(sub.data)
                # sub이 파일이면, 파일 생성

                cur = sub
                filename = ""
                # 현재 노드가 파일일 경우
                if cur.data.find('/') == -1:
                    while cur.parent != None:
                        filename = cur.data + filename
                        cur = cur.parent
                    # root 경로 추가
                    filename = '/' + filename
                    # 해당 디렉토리에 파일 받기
                    print(filename, self.ftp.total_count)
                    if self.step >= 100:
                        self.step = 0

                    self.statusbar.showMessage(filename)
                    self.statusbar.repaint()
                    while True:
                        res = self.ftp.get_file_by_name(filename)
                        if res[0] == -1:
                            print("재요청중...")
                            # self.mav_port.ftp_close(seq_num=0)
                        elif res[0] == 0:
                            search_result.append([filename, 'SUCCESS'])
                            self.step = int((i / self.ftp.total_count)*100)
                            self.progressbar.setValue(self.step)
                            print(i)
                            QApplication.processEvents()

                            i += 1
                            break
                        elif res[0] == 2:
                            if res[1] == 13:
                                search_result.append([filename, 'EACCES'])
                                break
                        elif res[0] == 4:
                            print("Session not found. reloading...")
                        elif res[0] == 10:
                            search_result.append([filename, 'FILEEXISTSERROR'])
                            break
                        else:
                            break

                else:
                    try:
                        foldername = sub.data
                        while foldername[0] == " ":
                            foldername = foldername[1:]
                        os.makedirs(foldername)
                    except FileExistsError:
                        pass

                st.append(sub)
        self.statusbar.showMessage("")
        self.statusbar.repaint()
        self.progressbar.setValue(0)

        try:
            parser_fd = os.open(self.modulePath, os.O_BINARY)
            self.parser = missionParser(parser_fd)

            # 파일 정보 표시(mission)
            self.fileInfo(self.modulePath, self.tableWidget_file)

        except FileNotFoundError as e:
            print(os.getcwd())
            self.parser = None
            print(e)
            pass
        except AttributeError as a:
            print(a)            
            parser_fd = os.open(self.dataman,0)
            self.parser = missionParser(parser_fd)
            self.fileInfo(self.modulePath, self.tableWidget_file)
            pass

        QApplication.processEvents()
        self.dataRefreshButton.setEnabled(True)
        self.radio_safepoint.setEnabled(True)
        self.radio_geofencepoint.setEnabled(True)
        self.radio_waypoint.setEnabled(True)

    def fileInfo(self, filename, table):
        try:
            fd = os.open(filename, os.O_BINARY)
        except FileNotFoundError:
            return
        except AttributeError as a:
            print(a)            
            fd = os.open(filename,0)
            
        if fd < 0:
            if self.ftp is not None:
                self.getFileFromUAV()
                try:
                    fd = os.open(filename, os.O_BINARY)
                except AttributeError as a:
                    print(a)            
                    fd = os.open(filename,0)
            elif fd < 0 or self.ftp is None:
                return -1

        if "dataman" in filename :
            datamanId = self.parser.get_mission()[3]
            encrypt = dataman_is_encrypted(self.parser.get_safe_points(), self.parser.get_fence_points(),
                               self.parser.get_mission_item(datamanId), self.parser.get_mission())
            if self.ftp is not None:
                inte = self.HMAC_calc(filename)
            else:
                inte = "unconnected"

        if "ulg" in filename:
            encrypt = is_encrypted(filename)
            inte = True

        created = createdTime(filename)
        hashSha = hash_sha1(filename)
        hashMD5 = hash_md5(filename)

        if self.ftp is not None:
            ftpcrc = self.ftp.get_crc_by_name(filename[filename.find("/"):], 0)
            Crc = crc()
            CrcResult = Crc.crc32Check(filename=filename, checksum=ftpcrc[1])
        else:
            CrcResult = "unconnected"


        if encrypt == 0:
            encrypt = "False"
        elif encrypt ==1 :
            encrypt = "True"

        header = ["created", "MD5", "SHA-1","CRC", "integrity"]
        data = [created, hashSha,hashMD5,CrcResult,inte]

        table.setColumnCount(2)
        table.setRowCount(len(header))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)

        for i in range(len(header)):
            table.setItem(i, 0, QTableWidgetItem(header[i]))
            table.setItem(i, 1, QTableWidgetItem(str(data[i])))

        table.resizeRowsToContents()
        table.resizeColumnsToContents()
        os.close(fd)

    def logParams(self, table, filepath):
        _list = shell_log_params(filepath)
        table.setColumnCount(2)
        table.setRowCount(len(_list))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)

        for i in range(len(_list)):
            table.setItem(i, 0, QTableWidgetItem(_list[i][0]))
            table.setItem(i, 1, QTableWidgetItem(str(_list[i][1])))

        table.resizeRowsToContents()
        table.resizeColumnsToContents()

    def logMessages(self, table, filepath):
        _list = shell_log_messages(filepath)
        table.setColumnCount(1)
        table.setRowCount(len(_list))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        
        for i in range(len(_list)):
            table.setItem(i, 0, QTableWidgetItem(_list[i]))
  
        table.resizeRowsToContents()
        table.resizeColumnsToContents()


    def safeClicked(self):
        try:
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
            self.tableWidget_point.setRowCount(len(safePoints) - 1)
            self.tableWidget_point.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tableWidget_point.setHorizontalHeaderLabels(column_headers)

            x = []
            y = []

            print(safePoints)
            for idx, item in enumerate(safePoints):

                for i, num in enumerate(item):
                    if type(num) != "str":
                        item[i] = str(num)
                if idx == 0:
                    self.tableWidget_status.setItem(idx, 0, QTableWidgetItem(item[0]))
                    self.tableWidget_status.setItem(idx, 1, QTableWidgetItem(item[1]))
                else:
                    self.tableWidget_point.setItem(idx - 1, 0, QTableWidgetItem(item[0]))
                    self.tableWidget_point.setItem(idx - 1, 1, QTableWidgetItem(item[1]))
                    self.tableWidget_point.setItem(idx - 1, 2, QTableWidgetItem(item[2]))
                    self.tableWidget_point.setItem(idx - 1, 3, QTableWidgetItem(item[3]))
                    y.append(round(float(item[0]), 7))
                    x.append(round(float(item[1]), 7))

            self.tableWidget_point.resizeRowsToContents()
            print(x, y)
            self.drawGraph(x, y, [],[],title='safe points')
            self.fileInfo(self.modulePath, self.tableWidget_file)

        except FileNotFoundError as e:
            print(e)
            QMessageBox.about(self, '파일 오류', '비행 데이터 파일을 찾을 수 없습니다.')
            pass
        except AttributeError as a:
            print(a)
            if a == "'NoneType' object has no attribute 'serial_write'":
                pass
            elif a =="module 'os' has no attribute 'O_BINARY'":
                pass
            else:
                QMessageBox.about(self, '파일 오류', '파일이 잘못되었습니다.')


    def geoClicked(self):
        try:
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
            x = []
            y = []
            v = []
            n = []
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

                    y.append(round(float(item[0]), 7))
                    x.append(round(float(item[1]), 7))
                    v.append(float(item[3]))
                    n.append(int(item[4]))

            self.tableWidget_point.resizeRowsToContents()
            self.drawGraph(x, y, v, n, "fence points")

            self.fileInfo(self.modulePath, self.tableWidget_file)
        except FileNotFoundError as e:
            print(e)
            QMessageBox.about(self, '파일 오류', '비행 데이터 파일을 찾을 수 없습니다.')
            pass
        except AttributeError as a:
            print(a)
            if a == "'NoneType' object has no attribute 'serial_write'":
                pass
            else:
                QMessageBox.about(self, '파일 오류', '파일이 잘못되었습니다.')

    def wayClicked(self):
        try:
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

            x = []
            y = []
            v = []
            n = []

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
                y.append(round(float(item[0]), 7))
                x.append(round(float(item[1]), 7))
                n.append(int(item[9]))
                v.append(int(item[13]))
            self.tableWidget_point.resizeRowsToContents()
            self.drawGraph(x, y, v, n, "waypoints")

            self.fileInfo(self.modulePath, self.tableWidget_file)
        except FileNotFoundError as e:
            print(e)
            QMessageBox.about(self, '파일 오류', '비행 데이터 파일을 찾을 수 없습니다.')
            pass
        except AttributeError as a:
            if a == "'NoneType' object has no attribute 'serial_write'":
                pass
            else:
                QMessageBox.about(self, '파일 오류', '파일이 잘못되었습니다.')


def PX4Forensic():
    suppress_qt_warnings()
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
