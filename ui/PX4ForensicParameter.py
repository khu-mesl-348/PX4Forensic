from src.PX4Parameter import get_parameters
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem


class Parameterclass:
    
    def __init__(self, List, Description, Value, Range, Information):
        self.list = List
        self.description = Description
        self.value = Value
        self.range = Range
        self.information = Information
        self.param = []
        self.list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.list.itemClicked.connect(self.clickon)

        self.description.setRowCount(2)
        self.description.setColumnCount(2)

        self.range.setColumnCount(2)

        self.information.setColumnCount(2)

        self.description.verticalHeader().hide()
        self.description.horizontalHeader().hide()

        self.range.verticalHeader().hide()
        self.range.horizontalHeader().hide()

        self.information.verticalHeader().hide()
        self.information.horizontalHeader().hide()


    def show_parameter_list(self):
        self.param = get_parameters()
        for i in self.param:
            self.list.addItem(i['name'])

    def clickon(self):
        curItem = self.list.currentItem().text()
        
        for item in self.param:

            if item['name'] == curItem:
                # Description 테이블 채우기
                i = 0

                if 'shortDesc' in item:
                    self.description.setItem(i, 0, QTableWidgetItem('short'))
                    self.description.setItem(i, 1, QTableWidgetItem(item['shortDesc']))
                    i += 1
                if 'longDesc' in item:
                    self.description.setItem(i, 0, QTableWidgetItem('long'))
                    self.description.setItem(i, 1, QTableWidgetItem(item['longDesc']))

                # Value 값 채우기
                if 'value' in item:
                    self.value.setText(str(item['value']))
                elif 'default' in item:
                    self.value.setText(str(item['default']))
                else:
                    self.value.setText('None')


                # range 값 채우기
                # 자료형이 불연속적인 경우(int 등)
                if 'values' in item:
                    self.range.setColumnCount(2)
                    self.range.setRowCount(len(item['values']))
                    for it, v in enumerate(item['values']):
                        self.range.setItem(it, 0, QTableWidgetItem(str(v['value'])))
                        self.range.setItem(it, 1, QTableWidgetItem(v['description']))
                else:
                    self.range.setRowCount(2)
                i = 0
                if 'min' in item:
                    self.range.setItem(i, 0, QTableWidgetItem(str(item['min'])))
                    self.range.setItem(i, 1, QTableWidgetItem('min'))
                    i += 1
                if 'max' in item:
                    self.range.setItem(i, 0, QTableWidgetItem(str(item['max'])))
                    self.range.setItem(i, 1, QTableWidgetItem('max'))

                k = item.keys() - ['name', 'shortDesc', 'longDesc', 'value',  'values', 'min', 'max']

                self.information.setRowCount(len(k))
                i = 0
                for key in k:
                    self.information.setItem(i, 0, QTableWidgetItem(key))
                    self.information.setItem(i, 1, QTableWidgetItem(str(item[key])))
                    i += 1

                self.description.resizeRowsToContents()
                self.description.resizeColumnsToContents()

                self.range.resizeRowsToContents()
                self.range.resizeColumnsToContents()

                self.information.resizeRowsToContents()
                self.information.resizeColumnsToContents()
                break





    def clear(self):
        self.param = []