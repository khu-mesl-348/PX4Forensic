from cgitb import text
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

class MyApp(QDialog):

    def dialog_open(self,input):
        if input:
            fname = input
        else:        
            fname = QFileDialog.getOpenFileName(self)

        if fname[0]:
            self.pathLabel.setText(fname[0])
            print('filepath : ', fname[0])
            print('filesort : ', fname[1])
            f = open(fname[0], 'r', encoding = 'UTF8')
            with f:
                data = f.read()
                MyApp.second_window(data)
        else:
            QMessageBox.about(self, 'warning', '파일을 선택하지 않았습니다')

    def second_window(data):
        window_2 = second(data)
        window_2.exec_()

    # def paintEvent(self, e):
    #     qp = QPainter()
    #     qp.begin(self)
    #     self.draw_line(qp)
    #     qp.end()

    # def draw_line(self, qp):
    #     qp.setPen(QPen(Qt.black, 4))
    #     qp.drawLine(100, 700, 100, 750)
    #     qp.setPen(QPen(Qt.black, 4))
    #     qp.drawLine(100, 750, 150, 750)

    def __init__(self):
        super().__init__()
        QToolTip.setFont(QFont('SansSerif', 10))
        self.btn1 = QPushButton('open file', self)
        self.btn1.clicked.connect(self.dialog_open)
        self.pathLabel = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.btn1)
        layout.addWidget(self.pathLabel)
        self.setLayout(layout)
        self.setWindowTitle('px4_extracted')
        self.setWindowIcon(QIcon('drone.jpg'))
        self.resize(300,150)
        self.initUI()

    def initUI(self):
        self.show()

class second(QDialog):

    def __init__(self,data):
        super().__init__()
        layout = QVBoxLayout()
        self.textEdit = QTextEdit(self)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)
        self.setWindowTitle('data_shown')
        self.setWindowIcon(QIcon('drone.jpg'))
        self.get_data(data)
        self.resize(600,700)
        self._initUi_()

    def _initUi_(self):
        self.show()

    def get_data(self,data):
        self.textEdit.setText(data)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())

# def exit_Act(x):
#     x.setShortcut('Ctrl+Q')
#     x.setStatusTip('Exit application')
#     x.triggered.connect(qApp.quit)
