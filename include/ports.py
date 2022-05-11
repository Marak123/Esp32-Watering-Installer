from PyQt5 import QtCore, QtGui, QtWidgets
import serial
import serial.tools.list_ports
import datetime

from .configWindow import *
from .conf import *


class MyPorts:
    def __init__(self):
        self.ports

    def getPorts(self):
      self.ports = serial.tools.list_ports.comports()
      string = []
      for port, desc, hwid in self.ports:
         string.append("{}: {}".format(port, desc))
      return string

    def ports(self):
        return self.ports

    def getPortString(self, iden):
        if(len(self.ports) > iden):
            return str(self.ports[iden])
        else:
            return "No ports found"

    def getPortShort(self, iden):
        if(len(self.ports) > iden):
            return str(self.ports[iden]).split(" ")[0]
        else:
            return "No ports found"

    def scanPort(self):
        return self.ports != serial.tools.list_ports.comports()

class SerialMonitor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SerialMonitor, self).__init__(parent)
        self.renderElements()

        self.parent = parent
        self.windowOpen = False
        self.serial = serial.Serial(baudrate=115200, timeout=0.01, xonxoff=False, rtscts=False, dsrdtr=False)
        self._taskThread = QtCore.QTimer(interval=0.5, timeout=self.printMainData)

    def closeEvent(self, a0):
        self.serial.close()
        self._taskThread.stop()
        self.windowOpen = False
        self.hide()
        a0.Hide = True

    def disableWindow(self):
        self._taskThread.stop()
        self.serial.close()
        self.parent.setEnabled(False)

    def enableWindow(self):
        self.serial.open()
        self._taskThread.start()
        self.parent.setEnabled(True)

    def checkBusyPort(self):
        try:
            self.serial.open()
            self.serial.close()
            return False
        except IOError:
            return True

    def showMonitor(self, port=None):
        if port is not None:
            self.port = port
            self.serial.port = self.port
        else:
            ConfigWindow.errorMessageBox(self, message="Nie wybrano portu", title="Port is None")

        if self.checkBusyPort():
            ConfigWindow.errorMessageBox(self, message="Port {} jest zajęty".format(self.port), title="Busy")
            return False

        self.textBox.clear()
        self.serial.open()
        self.windowOpen = True
        self.serial.flushInput()
        self.serial.flushOutput()
        self._taskThread.start()
        self.show()
        return True

    def setBaudrate(self, baudrate):
        self.serial.close()
        self.serial.baudrate = int(baudrate)
        self.serial.open()

    def read(self):
        return self.serial.readline()

    def write(self, data):
        if self.isOpen():
            if self.serial.write(data) == len(data):
                self.textBox.append("Wysłałeś: " + data.decode("utf-8", errors="ignore") + "\n")
        else:
            print("Port is closed")

    def isOpen(self):
        return self.serial.isOpen()

    def printMainData(self):
        if self.isOpen():
            if self.serial.inWaiting() > 0:
                data = self.read().decode("utf-8", errors="ignore")
                if self.timeStamp.isChecked():
                    now = datetime.datetime.now()
                    self.textBox.insertPlainText(str(now.time())[0:12] + " -> " + data)
                else:
                    self.textBox.insertPlainText(data)

                if self.autoScrool.isChecked():
                    self.textBox.moveCursor(QtGui.QTextCursor.End)

    def renderElements(self):
        self.textBox = QtWidgets.QTextEdit(self)
        self.textBox.setReadOnly(True)
        self.textBox.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.textBox.setFont(QtGui.QFont("Courier New", 10))
        self.textBox.setGeometry(QtCore.QRect(0, 30, 800, 530))
        self.cursorPos = QtGui.QTextCursor(self.textBox.document())
        self.textBox.setTextCursor(QtGui.QTextCursor(self.cursorPos))

        self.textInput = QtWidgets.QLineEdit(self)
        self.textInput.setGeometry(QtCore.QRect(5, 6, 700, 20))
        self.textInput.setFont(QtGui.QFont("Courier New", 10))

        self.sendButton = QtWidgets.QPushButton(self)
        self.sendButton.setText("Wyślij")
        self.sendButton.setGeometry(QtCore.QRect(710, 3, 85, 25))
        self.sendButton.clicked.connect(lambda: self.write(self.textInput.text().encode("utf-8")))

        self.clearButton = QtWidgets.QPushButton(self)
        self.clearButton.setText("Wyczyść Okno")
        self.clearButton.setGeometry(QtCore.QRect(690, 568, 100, 25))
        self.clearButton.clicked.connect(lambda: self.textBox.clear())

        self.autoScrool = QtWidgets.QCheckBox(self)
        self.autoScrool.setText("AutoScroll")
        self.autoScrool.setGeometry(QtCore.QRect(5, 568, 100, 20))
        self.autoScrool.stateChanged.connect(lambda: self.textBox.setLineWrapMode(QtWidgets.QTextEdit.NoWrap) if self.autoScrool.isChecked() else self.textBox.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth))

        self.timeStamp = QtWidgets.QCheckBox(self)
        self.timeStamp.setText("Pokaż znacznik czasu")
        self.timeStamp.setGeometry(QtCore.QRect(90, 568, 150, 20))

        self.baudrate = QtWidgets.QComboBox(self)
        self.baudrate.setGeometry(QtCore.QRect(585, 571, 100, 20))
        self.baudrate.addItems(["300", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", "250000", "460800", "500000", "921600", "1000000", "2000000"])
        self.baudrate.setCurrentText("115200")
        self.baudrate.currentTextChanged.connect(lambda: self.setBaudrate(self.baudrate.currentText()))