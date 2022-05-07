import subprocess
import os
import io
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from .ownHttp import *
from .conf import *

class Process:
    def __init__(self, console, objPorts):
        self.console = console
        self.objPorts = objPorts
        self.processDone = False
        self.isRunning = False

    def runCommand(self):
        if self.subp.poll() is None:
            with io.open(COMMAND_LOG_FILE + "\\" + self.logFile, "rb") as rl:
                self.console.setPlainText(rl.read().decode("utf-8", errors="ignore"))
                self.console.moveCursor(QtGui.QTextCursor.End)
            return
        elif self.subp.poll() == 0 and self.communicate:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Success", "Operacja zakończona pomyślnie").exec()
        elif self.subp.poll() == 1 and self.communicate:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Port jest zajęty!").exec()
        elif self.subp.poll() == 2 and self.communicate:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Nie można połączyć się z ESP32!").exec()
        elif self.communicate:
            print("Error: " + str(self.subp.poll()))
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Wystąpił problem!").exec()

        self._taskThread.stop()
        self.processDone = True
        self.isRunning = False

    def process(self, command, logFile, communicat=True):
        if self.isRunning:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Poczekaj na zakończenie poprzedniej operaacji!").exec()
            return False

        self.isRunning = True
        self.communicate = communicat
        if not os.path.exists(COMMAND_LOG_FILE):
            os.makedirs(COMMAND_LOG_FILE)
        self.logFile = logFile + "-" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".log"

        with io.open(COMMAND_LOG_FILE + "\\" + self.logFile, "wb") as wl:
            self.subp = subprocess.Popen(command, stdout=wl)

        self._taskThread = QtCore.QTimer(interval=0.1, timeout=self.runCommand)
        self._taskThread.start()
        return True

class UploadService:
    def __init__(self, objPorts, serialWindow, process):
        self.http = MyHttpRequest()
        self.objPorts = objPorts
        self.serialWindow = serialWindow
        self.process = process

    def downloadFile(self, version, name):
        self.http.url = GITHUB_BASE_URL + version + "/" + name
        fileContent = self.http.get()

        if fileContent == None:
            return print('Error: File "'+ self.http.url + '" not found!')
        if not os.path.exists(".\\temp\\" + version):
            os.makedirs(".\\temp\\" + version)

        file = open(".\\temp\\" + version + "\\" + name, "wb")
        file.write(fileContent)
        file.close()

    def checkEndProcess(self):
        if self.process.processDone:
            if self.objPorts.windowOpen:
                self.objPorts.enableWindow()
            self.process.processDone = False
            self._thred.stop()

    def eraseFlash(self, port):
        self.process.process(logFile="eraseFlash", command=".\\app\\esptool.exe --chip esp32 -p " + port + " erase_flash")

    def upload(self, version, port):
        if self.process.isRunning:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Błąd", "Poczekaj na zakończenie poprzedniej operacji!").exec()
            return

        if self.objPorts.windowOpen:
            self.objPorts.disableWindow()

        self.downloadFile(version, "firmware.bin")
        self.process.process(logFile="uploadFirmware", command=".\\app\\esptool.exe --chip esp32 -p " + port + " --baud 921600 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size detect 0xe000 .\\app\\image\\boot_app0.bin 0x1000 .\\app\\image\\bootloader_dio_80m.bin 0x10000 .\\temp\\" + version + "\\firmware.bin")

        self._thred = QtCore.QTimer(interval=0.1, timeout=self.checkEndProcess)
        self._thred.start()

    def unpackSPIFFS(self, version):
        self.downloadFile(version, "spiffs.bin")
        self.process.process(logFile="unpackSPIFFS", command=".\\app\\mkspiffs.exe -u .\\temp\\" + version + "\\spiffs-data -b 4096 -p 256 -s 1507328 .\\temp\\" + version + "\\spiffs.bin", communicat=False)

    def buildSPIFFS(self, version):
        if self.process.isRunning:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Błąd", "Poczekaj na zakończenie poprzedniej operacji!").exec()
            return False

        self.process.process(logFile="buildSPIFFS", command=".\\app\\mkspiffs.exe -c .\\temp\\" + version + "\\spiffs-data -b 4096 -p 256 -s 1507328 .\\temp\\" + version + "\\spiffs.bin", communicat=False)
        return True

    def uploadSPIFFS(self):
        if not self.process.processDone and self.buildRun:
            return
        self.process.processDone = False
        print("dzaila")

        if self.objPorts.windowOpen:
            self.objPorts.disableWindow()

        self.process.process(logFile="uploadSPIFFS", command=".\\app\\esptool.exe --chip esp32 -p " + self._port + " --before default_reset --after hard_reset --baud 921600 write_flash -z --flash_mode dio --flash_freq 80m --flash_size detect 2686976 .\\temp\\" + self._ver + "\\spiffs.bin", communicat=True)

        self._thred = QtCore.QTimer(interval=0.1, timeout=self.checkEndProcess)
        self._thred.start()

    def buidlAndUploadSPIFFS(self, version, port):
        if os.path.exists(".\\temp\\" + version + "\\spiffs-data"):
            self.buildRun = True
            if not self.buildSPIFFS(version):
                return False
        else:
            self.downloadFile(version, "spiffs.bin")
            print("powinien dzialac")
            self.buildRun = False

        self._ver = version
        self._port = port
        self._thred = QtCore.QTimer(interval=0.1, timeout=self.uploadSPIFFS)
        self._thred.start()

