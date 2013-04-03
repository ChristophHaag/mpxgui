#!/usr/bin/python3

import sys
from PyQt4.QtGui import QApplication, QDialog,QListView,QIcon,QAbstractItemView,QDrag
from PyQt4.QtCore import QAbstractListModel,QModelIndex,Qt,QAbstractListModel
from mpxgui_ui import Ui_MainWindow
import ctypeswrapper
from PyQt4 import QtGui,QtCore
import pickle

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

#http://stackoverflow.com/a/1695250
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    #reverse = dict((value, key) for key, value in enums.iteritems())
    #enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

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

l = ctypeswrapper.XIDeviceInfoList()
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
        # we only care about slave pointers or slave keyboards, that are attached to a master and that are enabled
        if (l[x]['use'] in (ctypeswrapper.XISlavePointer, ctypeswrapper.XISlaveKeyboard)) and l[x]['attachment'] in allmasters and l[x]['enabled']:
            #print("Slave: " + str(l[x]['name']) + "\t" + repr(l[x]))
            attachedlist[allmasters[l[x]['attachment']]].append(l[x])
    return attachedlist
attached = constructAttached(l)

app = QApplication(sys.argv)
window = QDialog()
ui = Ui_MainWindow()
ui.setupUi(window)
window.show()

#(MOVE_SLAVE, device id, from master id, to master id)
#(CREATE_MASTER, first master id) (the second id will be assigned automatically)
#(REMOVE_MASTER, master tuple)
#TODO: maybe make class
Actions = enum('MOVE_SLAVE', 'CREATE_MASTER', 'REMOVE_MASTER')
actionstack = []

def actionstack_worker():
    pass

class DNDListView(QListView):
    def __init__(self,parent=None):
        super(DNDListView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        drag = QDrag(self)
        mimeData = QtCore.QMimeData()
        el = self.model().listdata[index.row()]
        print("dragging device with id: " + str(el['deviceid']))
        mimeData.setData("application/x-xinputdevice", pickle.dumps(el))
        drag.setMimeData(mimeData)
        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, self.rectForIndex(index))
        drag.setPixmap(pixmap)
        #drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
        result = drag.start(QtCore.Qt.MoveAction)
        if result == 1:
            self.model().listdata.remove(el)
    def mouseMoveEvent(self, event):
        self.startDrag(event)
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-xinputdevice"):
            event.setDropAction(QtCore.Qt.MoveAction)
            super(DNDListView, self).dragMoveEvent(event)
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-xinputdevice"):
            event.acceptProposedAction()
        else:
            super(DNDListView, self).dragEnterEvent(event)
    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-xinputdevice"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.acceptProposedAction()
            bstream = event.mimeData().retrieveData("application/x-xinputdevice", QtCore.QVariant.ByteArray)
            el = pickle.loads(bstream)
            print("dropped device with id: " + str(el['deviceid']))
            ma = self.model().master
            lda = self.model().listdata
            lda.append(el)
            # not sure why the old model refuses to refresh, with a new one it works TODO
            self.setModel(DevListModel({ma: lda}))
            for act in actionstack:
                if act[0] == Actions.MOVE_SLAVE and act[1] == el['deviceid']:
                    print("removing action: " + repr(act))
                    actionstack.remove(act) # not really safe I think
            act = (Actions.MOVE_SLAVE, el['deviceid'], allmasters[el['attachment']], self.model().master)
            if (act[0] == Actions.MOVE_SLAVE and act[2] == act[3]):
                print("Doing nothing with device " + el['name'] + "(" + str(el['deviceid']) + ")")
            else:
                print("adding action: " + repr(act))
                actionstack.append(act)
            print("new actionstack: " + repr(actionstack))
        else:
            super(DNDListView,self).dropEvent(event)
      
listviews = []
for i in masters:
    model = DevListModel({i: attached[i]})
    lv = DNDListView()
    lv.setModel(model)
    ui.devicelistlayout.addWidget(lv)

# and one empty one so it's possible to drag and drop to a new master
model = DevListModel({(42,43): []}) #TODO: check for already existing ids and generate good new ones, or create one via name and take the new ids
lv = DNDListView()
lv.setModel(model)
ui.devicelistlayout.addWidget(lv)
sys.exit(app.exec_())