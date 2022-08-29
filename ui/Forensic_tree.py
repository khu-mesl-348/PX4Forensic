import sys
import Text_Edit_open
from PyQt5.QtWidgets import *

#make tree and visualize
class QTreeView(QTreeView):
    def __init__(self):
        super(QTreeView, self).__init__()

    def edit(self, index, trigger, event):
        return False

#make a blank that can drag and drop the file
#the file that can be encoded by UTF-8 only be read by dialog_open
class QLineEdit(QLineEdit):
    def __init__(self):
        super(QLineEdit, self).__init__()
        self.pathLabel = QLabel(self)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            event.acceptProposedAction()
    
    # link it to widget, get the data about file
    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            filepath = str(urls[0].path())[1:]
            self.setText(filepath)
            push = ('/'+filepath, 'All Files (*)')

            #open a textEditer that shows a file data
            px4_get_file.MyApp.dialog_open(self,input = push)

class Main(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        #get total filesystem
        root_path = "C:/"
        self.model_file_system = QFileSystemModel()
        self.model_file_system.setRootPath(root_path)
        self.model_file_system.setReadOnly(False)

        #input = Forensic start point -> should be changed by a user
        start_index = "/home/kibong/python/"
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model_file_system)
        self.tree_view.setRootIndex(self.model_file_system.index(start_index))
        self.tree_view.doubleClicked.connect(lambda index : self.item_double_clicked(index))

        self.tree_view.setDragEnabled(True)
        self.tree_view.setColumnWidth(0,300)

        lineedit = QLineEdit()

        layout.addWidget(self.tree_view)
        layout.addWidget(lineedit)

        self.setLayout(layout)
        self.resize(800, 500)
        self.show()

    #get the file path when it double_clicked
    def item_double_clicked(self, index):
        print(self.model_file_system.filePath(index))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
