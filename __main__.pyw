import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import requests

from include.ports import *
from include.uploads import *
from include.ownHttp import *
from include.configWindow import *
from include.conf import *

class window(QtWidgets.QWidget, QtCore.QObject):
   def __init__(self, parent=None):
      super(window, self).__init__(parent)
      self.resize(500,600)
      self.setWindowTitle("Podlewanko")
      # self.setWindowIcon(QtGui.QIcon(ICON_APP_PATH))

      self.myports = MyPorts()
      self._portView = self.genPorts()
      self._activePortString = self.myports.getPortString(0)
      self._activePortShort = self.myports.getPortShort(0)

      self._httpVersion = MyHttpRequest(GITHUB_VERSION_URL)
      self._activeVersion = ""
      self._versionView = self.genVersion()

      self._infoPortLable = self.infoPortLable()
      self._infoVersionLable = self.infoVersionLable()
      self._console = self.console()
      self._process = Process(self._console, self.myports)

      self._serialMonitor =  SerialMonitor()

      self.serialWindow = QtWidgets.QMdiSubWindow()
      self.serialWindow.setWidget(self._serialMonitor)
      self.serialWindow.setWindowTitle("Podlewanko")
      # self.serialWindow.setWindowIcon(QtGui.QIcon(ICON_APP_PATH))
      self.serialWindow.setGeometry(0, 0, 800, 600)
      self._serialMonitor.parent = self.serialWindow

      self._uploads = UploadService(objPorts=self._serialMonitor, serialWindow=self.serialWindow, process=self._process)
      self._configWindow = ConfigWindow()

      self.buttonConfigFileEdit()
      self.buttonSerialMonitor()
      self._buttonUploadFirmware = self.buttonUploadFirmware()
      self._buttonUploadSPIFFS = self.buttonUploadSPIFFS()

      self._taskThread = QtCore.QTimer(interval=1000, timeout=self.tasks)
      self._taskThread.start()

   def tasks(self):
      # Update ports
      if self.myports.scanPort():
         self._portView.clear()
         self._portView.addItems(self.myports.getPorts())
         self._portView.setCurrentIndex(0)
         self._activePortString = self.myports.getPortString(0)
         self._activePortShort = self.myports.getPortShort(0)
         self._uploads.port = self.myports.getPortShort(0)
         self._infoPortLable.setText(self._activePortString)


   def setActivePort(self):
      self._activePortShort = self.myports.getPortShort(self._portView.currentIndex())
      self._activePortString = self.myports.getPortString(self._portView.currentIndex())
      self._infoPortLable.setText(self._activePortString)
      self._uploads.port = self.myports.getPortShort(self._portView.currentIndex())

   def genPorts(self):
      lb = QtWidgets.QLabel(self)
      lb.setText("Wybierz port: ")
      lb.setGeometry(15, -15, 470, 100)
      lb.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))

      portList = QtWidgets.QComboBox(self)
      portList.setGeometry(120, 20, 370, 30)
      portList.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Normal))
      portList.setModel(QtGui.QStandardItemModel())
      portList.addItems(self.myports.getPorts())
      portList.activated.connect(self.setActivePort)
      return portList

   def setActiveVersion(self):
      idxRev = 0
      idx= self._versionView.currentIndex().row()
      for i in range(len(self._httpVersion.getJSON()['older'])-1, -1, -1):
         for j in range(len(self._httpVersion.getJSON()['older'][i]['version'])-1, -1, -1):
            if idxRev == idx:
               self._activeVersion = self._httpVersion.getJSON()['older'][i]['version'][j]['vers']
               self._infoVersionLable.setText(self._activeVersion)
               return
            idxRev += 1

   def genVersion(self):
      lb = QtWidgets.QLabel(self)
      lb.setText("Wybierz wersje:")
      lb.setGeometry(15, 40, 470, 100)
      lb.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))

      versionList = self._httpVersion.getJSON()

      tree = QtWidgets.QTreeWidget(self)
      tree.setGeometry(15, 110, 470, 100)
      tree.setColumnCount(3)
      tree.setHeaderLabels(["Wersja", "Data wydania", "Opis"])
      tree.setColumnWidth(0, 150)
      tree.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Normal))

      for i in range(len(versionList['older'])-1, -1, -1):
         for j in range(len(versionList['older'][i]['version'])-1, -1, -1):
            if i == len(versionList['older'])-1 and j == len(versionList['older'][i]['version'])-1:
               strO = str(versionList['older'][i]['version'][j]['vers']) + " (najnowsza, zalecana)"
               self._activeVersion = versionList['older'][i]['version'][j]['vers']
            else: strO = str(versionList['older'][i]['version'][j]['vers'])

            item = QtWidgets.QTreeWidgetItem(tree)
            item.setText(0, str(strO))
            item.setText(1, str(versionList['older'][i]['version'][j]['date']))
            item.setText(2, str(versionList['older'][i]['version'][j]['desc']))
      tree.itemClicked.connect(self.setActiveVersion)

      return tree

   def infoPortLable(self):
      lbPort = QtWidgets.QLabel(self)
      lbPort.setText("Port: ")
      lbPort.setGeometry(15, 250, 470, 100)
      lbPort.setFont(QtGui.QFont("Arial", 15, weight=QtGui.QFont.Bold))

      lb = QtWidgets.QLabel(self)
      lb.setText(self._activePortString)
      lb.setGeometry(70, 287, 370, 30)
      lb.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
      return lb

   def infoVersionLable(self):
      lbPort = QtWidgets.QLabel(self)
      lbPort.setText("Wersja: ")
      lbPort.setGeometry(15, 290, 470, 100)
      lbPort.setFont(QtGui.QFont("Arial", 15, weight=QtGui.QFont.Bold))

      lb = QtWidgets.QLabel(self)
      lb.setText(self._activeVersion)
      lb.setGeometry(95, 327, 370, 30)
      lb.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
      return lb

   def checkEndProcessConfig(self):
      if self._process.processDone:
         self._process.processDone = False
         self._configWindow = ConfigWindow(version=self._activeVersion)
         self._configWindow.openFile()
         self.subWindow = QtWidgets.QMdiSubWindow()
         self.subWindow.setWidget(self._configWindow)
         self.subWindow.setWindowTitle("Podlewanko")
         self.subWindow.setWindowIcon(QtGui.QIcon(ICON_APP_PATH))
         self.subWindow.setGeometry(0, 0, 1000, 600)
         self.subWindow.show()

   def openConfigWindow(self):
      if self._process.isRunning:
         QtWidgets.QMessageBox(QtGui.QMessageBox.Warning, "Błąd", "Poczekaj na zakończenie poprzedniej operacji!").exec()
         return

      self._uploads.unpackSPIFFS(self._activeVersion)

      self._thrCheck = QtCore.QTimer(interval=0.1, timeout=self.checkEndProcessConfig)
      self._thrCheck.start()

   def buttonConfigFileEdit(self):
      btn = QtWidgets.QPushButton(self)
      btn.setText("Edytuj plik konfiguracyjny")
      btn.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))
      btn.setGeometry(250, 230, 230, 50)
      btn.clicked.connect(self.openConfigWindow)

   def openSerialMonitor(self):
      if self._serialMonitor.isOpen():
         self._serialMonitor.showMaximized()
         self._serialMonitor.showNormal()
         return self._serialMonitor.activateWindow()

      if self._serialMonitor.showMonitor(self._activePortShort):
         self._uploads.objPorts = self._serialMonitor
         self._uploads.serialWindow = self.serialWindow
         self.serialWindow.show()

   def buttonSerialMonitor(self):
      btn = QtWidgets.QPushButton(self)
      btn.setText("Serial Monitor")
      btn.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))
      btn.setGeometry(15, 230, 230, 50)
      btn.clicked.connect(self.openSerialMonitor)


   def buttonUploadFirmware(self):
      btn = QtWidgets.QPushButton(self)
      btn.setText("Wgraj firmware")
      btn.setFont(QtGui.QFont("Arial Black", 13, weight=QtGui.QFont.Bold))
      btn.setGeometry(15, 520, 230, 50)
      btn.clicked.connect(lambda: self._uploads.upload(self._activeVersion, self._activePortShort))

   def buttonUploadSPIFFS(self):
      btn = QtWidgets.QPushButton(self)
      btn.setText("Wgraj SPIFFS")
      btn.setFont(QtGui.QFont("Arial Black", 13, weight=QtGui.QFont.Bold))
      btn.setGeometry(250, 520, 230, 50)
      btn.clicked.connect(lambda: self._uploads.buidlAndUploadSPIFFS(self._activeVersion, self._activePortShort))

   def console(self):
      console = QtWidgets.QTextEdit(self)
      console.setGeometry(15, 380, 470, 130)
      console.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
      console.setReadOnly(True)
      console.setStyleSheet("background-color: white; border-top: 0.5px solid lightgray; border-left: 0.5px solid lightgray; border-right: 0.5px solid lightgray; border-bottom: 0.5px solid lightgray; padding-top: 4px;")

      lbl = QtWidgets.QLabel("Yellow", self)
      lbl.setGeometry(15, 365, 470, 20)
      lbl.setText("Konsola")
      lbl.setFont(QtGui.QFont("Arial", 11, weight=QtGui.QFont.Bold))
      lbl.setStyleSheet("background-color: white; border-top: 0.5px solid lightgray; border-left: 0.5px solid lightgray; border-right: 0.5px solid lightgray; padding-left: 3px;")

      return console

   def closeEvent(self, event):
      self._taskThread.stop()
      event.accept()


# if __name__ == '__main__':
app = QtWidgets.QApplication(sys.argv)
ex = window()
ex.show()

if app.exec_() == 0:
   ex.close()

sys.exit(0)
