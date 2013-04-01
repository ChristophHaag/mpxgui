#!/usr/bin/python3

import sys
from PyQt4.QtGui import QApplication, QDialog,QListView,QIcon
from PyQt4.QtCore import QAbstractListModel,QModelIndex,Qt,QAbstractListModel
from mpxgui_ui import Ui_MainWindow
import ctypeswrapper

import os
keyboard = QIcon(os.getcwd() + "/images/input-keyboard.svgz")
keyboard = QIcon(os.getcwd() + "/images/input-mouse.svgz")

#import argparse
#parser = argparse.ArgumentParser(description='xinput gui')
#parser.add_argument('--sum', dest='accumulate', action='store_const',
#                           const=sum, default=max,
#                                            help='sum the integers (default: find the max)')
#args = parser.parse_args()
#print (args.accumulate(args.integers))

class DevListModel(QAbstractListModel): 
    def __init__(self, datain, parent=None, *args): 
        QAbstractListModel.__init__(self, parent, *args) 
        # we should have only one master anyway
        self.master = list(datain.keys())[0]
        self.listdata = datain[self.master]
 
    def rowCount(self, parent=QModelIndex()): 
        return len(self.listdata)
 
    def data(self, index, role): 
        if index.isValid() and role == Qt.DisplayRole:
            if self.listdata:
                return self.listdata[index.row()]['name'] + " (" + str(self.listdata[index.row()]['deviceid']) + ")"
            else:
                return None
        else: 
            return None

#crappy xinput cli parsing
#import subprocess
#def getOutput(cmd):
#    output = subprocess.check_output(cmd).decode("utf-8")
#    return output
#devices = list(zip(getOutput(['xinput', 'list', '--name-only']).strip().split('\n'), getOutput(['xinput', 'list', '--id-only']).split('\n')))
#devicestrings = ["\t" + d[0] + ":\t" + d[1] + "\n" for d in devices]
#print (repr(devicestrings))

l = ctypeswrapper.XIDeviceInfoList()
devices = [ (l[x]['name'], str(l[x]['deviceid'])) for x in l]
#print(repr(l))
# if a master has an attachment to another master they belong together and form one pointer/keyboard couple
# but only add them once with the lesser index as first
masters = [(x,y) for x in l for y in l if (l[x]['attachment'] == l[y]['deviceid']) and (l[x]['use'] == ctypeswrapper.XIMasterPointer or l[x]['use'] == ctypeswrapper.XIMasterKeyboard)and (l[y]['use'] == ctypeswrapper.XIMasterPointer or l[y]['use'] == ctypeswrapper.XIMasterKeyboard) and l[x]['deviceid'] < l[y]['deviceid']]
print(str(len(masters)) + " masters: " +  repr(masters))

#just for checking whether a slave is connected to a master, we need a list of all masters
#flatten the list and attach the tuple each entry is in with... this...
allmasters = dict([(i, sublist) for sublist in masters for i in sublist])

def constructAttached(l):
    attachedlist = dict()
    for i in masters:
        attachedlist[i] = list()
    
    for x in l:
        if l[x]['use'] == ctypeswrapper.XISlavePointer and l[x]['attachment'] in allmasters and l[x]['enabled']:
            #print("Slavepointer: " + str(l[x]['name']) + "\t" + repr(l[x]))
            attachedlist[allmasters[l[x]['attachment']]].append(l[x])
        if l[x]['use'] == ctypeswrapper.XISlaveKeyboard and l[x]['attachment'] in allmasters and l[x]['enabled']:
            #print("Slavekeyboard: " + str(l[x]['name']) + "\t" + repr(l[x]))
            attachedlist[allmasters[l[x]['attachment']]].append(l[x])
    return attachedlist
attached = constructAttached(l)

app = QApplication(sys.argv)
window = QDialog()
ui = Ui_MainWindow()
ui.setupUi(window)
window.show()

listviews = []
for i in masters:
    model = DevListModel({i: attached[i]})
    lv = QListView()
    lv.setModel(model)
    ui.devicelistlayout.addWidget(lv)

# and one empty one so it's possible to drag and drop to a new master
model = DevListModel({None: []})
lv = QListView()
lv.setModel(model)
ui.devicelistlayout.addWidget(lv)

sys.exit(app.exec_())
