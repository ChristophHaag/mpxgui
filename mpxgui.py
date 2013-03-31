#!/usr/bin/python3

import sys
from PyQt4.QtGui import QApplication, QDialog
from PyQt4.QtCore import QAbstractListModel,QModelIndex,Qt
from mpxgui_ui import Ui_MainWindow
import ctypeswrapper

#import argparse
#parser = argparse.ArgumentParser(description='xinput gui')
#parser.add_argument('--sum', dest='accumulate', action='store_const',
#                           const=sum, default=max,
#                                            help='sum the integers (default: find the max)')
#args = parser.parse_args()
#print (args.accumulate(args.integers))

class DevListModel(QAbstractListModel): 
    def __init__(self, datain, parent=None, *args): 
        """ datain: a list where each item is a row
        """
        QAbstractListModel.__init__(self, parent, *args) 
        self.listdata = datain
 
    def rowCount(self, parent=QModelIndex()): 
        return len(self.listdata) 
 
    def data(self, index, role): 
        if index.isValid() and role == Qt.DisplayRole:
            return self.listdata[index.row()][0] + " (" + self.listdata[index.row()][1] + ")"
        else: 
            return #QVariant()

#crappy xinput cli parsing
#import subprocess
#def getOutput(cmd):
#    output = subprocess.check_output(cmd).decode("utf-8")
#    return output
#devices = list(zip(getOutput(['xinput', 'list', '--name-only']).strip().split('\n'), getOutput(['xinput', 'list', '--id-only']).split('\n')))
#devicestrings = ["\t" + d[0] + ":\t" + d[1] + "\n" for d in devices]
#print (repr(devicestrings))

l = ctypeswrapper.XIDeviceInfoList()
devices = [ (x['name'], str(x['deviceid'])) for x in l]

app = QApplication(sys.argv)
window = QDialog()
ui = Ui_MainWindow()
ui.setupUi(window)
window.show()

ui.listView.setModel(DevListModel(devices))

sys.exit(app.exec_())
