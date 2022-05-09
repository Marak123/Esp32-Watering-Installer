from PyQt5 import QtCore, QtGui, QtWidgets
import json
import jsbeautifier
import datetime
import os

from .ownHttp import *
from .conf import *

class ConfigWindow(QtWidgets.QWidget, QtCore.QObject):
    def __init__(self, version="",parent=None):
        super(ConfigWindow, self).__init__(parent)
        self.basePathConfig = ".\\temp\\" + version + "\\spiffs-data\\"

    def openFile(self):
        self._configFile = open(self.basePathConfig + "configFile.json", "r")
        try:
            self._config = json.loads(self._configFile.read())
        except:
            self.errorMessageBox("Wystapil problem z plikiem konfiguracyjnym w tej wersji oprogramowania. Sprobuj inna :)")
            self.close()
            
        self._configFile.close()

        self.wifi = self.wifi()
        self.ftp = self.ftp()
        self.account = self.account()
        self.pinsPower = self.pinsPower()
        self.tempPins = self.tempPins()
        self.mainOption = self.mainOption()

    def errorMessageBox(self, message, title="Error"):
        dialog = QtWidgets.QMessageBox()
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setIcon(QtWidgets.QMessageBox.Critical)
        dialog.exec_()

    def saveConfig(self):
        self._configFile = open(self.basePathConfig + "configFile.json", "w")
        self._configFile.write(jsbeautifier.beautify(json.dumps(self._config), 2))
        self._configFile.close()

    def saveWifi(self):
        self._config["WIFI"]["SSID"] = self.wifiName.text()
        self._config["WIFI"]["PASSWORD"] = self.wifiPass.text()
        self._config["WIFI"]["HOSTNAME"] = self.wifiHostName.text()
        if self.wifiIP.text() != "Automatycznie": self._config["WIFI"]["LOCAL_IP"] = self.wifiIP.text()
        if self.wifiMask.text() != "Automatycznie": self._config["WIFI"]["SUBNET"] = self.wifiMask.text()
        if self.wifiGate.text() != "Automatycznie": self._config["WIFI"]["GATEWAY"] = self.wifiGate.text()
        self.saveConfig()

    def wifi(self):
        if "WIFI" not in self._config:
            self._config["WIFI"] = {}
        groupbox = QtWidgets.QGroupBox("Wifi", self)
        groupbox.setGeometry(15, 15, 470, 180)
        groupbox.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Nazwa sieci:")
        lb.setGeometry(18, 10, 100, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.wifiName = QtWidgets.QLineEdit(groupbox)
        self.wifiName.setGeometry(110, 25, 100, 20)
        self.wifiName.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
        self.wifiName.setText(self._config["WIFI"]["SSID"] if "SSID" in self._config["WIFI"] else "")

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Hasło sieci:")
        lb.setGeometry(28, 42, 100, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.wifiPass = QtWidgets.QLineEdit(groupbox)
        self.wifiPass.setGeometry(110, 60, 100, 20)
        self.wifiPass.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
        self.wifiPass.setText(self._config["WIFI"]["PASSWORD"] if "PASSWORD" in self._config["WIFI"] else "")

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Nazwa hosta:")
        lb.setGeometry(8, 77, 100, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.wifiHostName = QtWidgets.QLineEdit(groupbox)
        self.wifiHostName.setGeometry(110, 95, 100, 20)
        self.wifiHostName.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
        self.wifiHostName.setText(self._config["WIFI"]["HOSTNAME"] if "HOSTNAME" in self._config["WIFI"] else "")

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Adres IP:")
        lb.setGeometry(250, 10, 100, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.wifiIP = QtWidgets.QLineEdit(groupbox)
        self.wifiIP.setGeometry(320, 25, 110, 20)
        self.wifiIP.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
        self.wifiIP.setText("Automatycznie" if "LOCAL_IP" not in self._config["WIFI"] or self._config["WIFI"]["LOCAL_IP"] == "" else self._config["WIFI"]["LOCAL_IP"])

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Maska:")
        lb.setGeometry(263, 42, 100, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.wifiMask = QtWidgets.QLineEdit(groupbox)
        self.wifiMask.setGeometry(320, 60, 110, 20)
        self.wifiMask.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
        self.wifiMask.setText("Automatycznie" if "SUBNET" not in self._config["WIFI"] or self._config["WIFI"]["SUBNET"] == "" else self._config["WIFI"]["SUBNET"])

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Brama:")
        lb.setGeometry(260, 77, 100, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.wifiGate = QtWidgets.QLineEdit(groupbox)
        self.wifiGate.setGeometry(320, 95, 110, 20)
        self.wifiGate.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
        self.wifiGate.setText("Automatycznie" if "GATEWAY" not in self._config["WIFI"] or self._config["WIFI"]["GATEWAY"] == "" else self._config["WIFI"]["GATEWAY"])

        self.wifiSave = QtWidgets.QPushButton(groupbox)
        self.wifiSave.setGeometry(300, 140, 150, 30)
        self.wifiSave.setText("Zapisz")
        self.wifiSave.clicked.connect(self.saveWifi)

        return groupbox


    def saveFtp(self):
        if self.ftpUser.text() == "" or self.ftpPass.text() == "" or self.ftpIP.text() == "":
            self.errorMessageBox("Wszystkie podla muszą być wypełnione aby usługa FTP działała poprawnie!")
            return

        self._config["FTP_SERVER"]["USERNAME"] = self.ftpUser.text()
        self._config["FTP_SERVER"]["PASSWORD"] = self.ftpPass.text()
        self._config["FTP_SERVER"]["IP_ADDRESS"] = self.ftpIP.text()
        if self.ftpPort.text() != "": self._config["FTP_SERVER"]["PORT"] = self.ftpPort.text()

        self.saveConfig()

    def ftp(self):
        if "FTP_SERVER" not in self._config:
            self._config["FTP_SERVER"] = {}

        groupbox = QtWidgets.QGroupBox("FTP", self)
        groupbox.setGeometry(15, 200, 470, 150)
        groupbox.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Nazwa użyt.:")
        lb.setGeometry(10, 10, 150, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.ftpUser = QtWidgets.QLineEdit(groupbox)
        self.ftpUser.setGeometry(110, 25, 100, 20)
        self.ftpUser.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Hasło użyt.:")
        lb.setGeometry(19, 42, 100, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.ftpPass = QtWidgets.QLineEdit(groupbox)
        self.ftpPass.setGeometry(110, 60, 100, 20)
        self.ftpPass.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Adres IP:")
        lb.setGeometry(250, 10, 100, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.ftpIP = QtWidgets.QLineEdit(groupbox)
        self.ftpIP.setGeometry(320, 25, 110, 20)
        self.ftpIP.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Port:")
        lb.setGeometry(276, 42, 100, 50)
        lb.setFont(QtGui.QFont("Berlin Sans FB", 13, weight=QtGui.QFont.Normal))

        self.ftpPort = QtWidgets.QLineEdit(groupbox)
        self.ftpPort.setGeometry(320, 60, 110, 20)
        self.ftpPort.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))
        self.ftpPort.setText("21")

        self.ftpSave = QtWidgets.QPushButton(groupbox)
        self.ftpSave.setGeometry(300, 110, 150, 30)
        self.ftpSave.setText("Zapisz")
        self.ftpSave.clicked.connect(self.saveFtp)

        return groupbox

    def renderUser(self):
        id = 0
        self.account.clear()
        for i in self._config["ACCOUNTS"]:
            item = QtWidgets.QTreeWidgetItem(self.account)
            item.setText(0, str(id))
            id += 1
            item.setText(1, i["USERNAME"])
            item.setText(2, i["PASSWORD"])
            if "DATA_CREATE" in i:
                date = str(i["DATA_CREATE"]["DAY"]) + "/" + str(i["DATA_CREATE"]["MONTH"]) + "/" + str(i["DATA_CREATE"]["YEAR"]) + " " + str(i["DATA_CREATE"]["HOUR"]) + ":" + str(i["DATA_CREATE"]["MINUTE"])
                item.setText(3, date)
            item.setText(4, i["RIGHTS"])

    def deleteUser(self, iden):
        if iden != "" and len(self._config['ACCOUNTS'])-1 >= int(iden):
            self._config['ACCOUNTS'].pop(int(iden))
            self.renderUser()
            self.saveConfig()
        else:
            self.errorMessageBox("Nie ma takiego użytkownika!")

    def addUser(self, name, password, rights, idenR):
        if idenR != "":
            try:
                iden = int(idenR)
            except:
                self.errorMessageBox("Niepoprawne ID użytkownika!")
                return

            if len(self._config['ACCOUNTS'])-1 >= int(iden):
                self._config['ACCOUNTS'][int(id)]["USERNAME"] = name
                self._config['ACCOUNTS'][int(id)]["PASSWORD"] = password
                self._config['ACCOUNTS'][int(id)]["RIGHTS"] = "ADMIN" if rights else "USER"
                self.renderUser()
                self.saveConfig()
                return
        for i in self._config['ACCOUNTS'] :
            if i["USERNAME"] == name:
                self.errorMessageBox("Użytkownik o takiej nazwie już istnieje!")
                return
        self._config['ACCOUNTS'].append({"USERNAME": name, "PASSWORD": password, "RIGHTS": "ADMIN" if rights else "USER", "DATA_CREATE": {"DAY": datetime.datetime.now().day, "MONTH": datetime.datetime.now().month, "YEAR": datetime.datetime.now().year, "HOUR": datetime.datetime.now().hour, "MINUTE": datetime.datetime.now().minute}})
        self.renderUser()
        self.saveConfig()

    def account(self):
        if "ACCOUNTS" not in self._config:
            self._config["ACCOUNTS"] = []
        groupbox = QtWidgets.QGroupBox("Konto", self)
        groupbox.setGeometry(15, 350, 470, 240)
        groupbox.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("ID:")
        lb.setGeometry(40, 10, 150, 50)

        accountID = QtWidgets.QLineEdit(groupbox)
        accountID.setGeometry(65, 25, 100, 20)
        accountID.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        deleteUserBtn = QtWidgets.QPushButton(groupbox)
        deleteUserBtn.setGeometry(180, 22, 130, 25)
        deleteUserBtn.setText("Usuń użytkownika")
        deleteUserBtn.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Bold))
        deleteUserBtn.clicked.connect(lambda: self.deleteUser(accountID.text()))


        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Nazwa:")
        lb.setGeometry(10, 45, 100, 50)

        accountName = QtWidgets.QLineEdit(groupbox)
        accountName.setGeometry(65, 60, 100, 20)
        accountName.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Hasło:")
        lb.setGeometry(180, 45, 100, 50)

        accountPass = QtWidgets.QLineEdit(groupbox)
        accountPass.setGeometry(225, 60, 100, 20)
        accountPass.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Admin:")
        lb.setGeometry(350, 45, 100, 50)

        accountLevel = QtWidgets.QCheckBox(parent=groupbox)
        accountLevel.setGeometry(410, 61, 100, 20)
        accountLevel.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        deleteUserBtn = QtWidgets.QPushButton(groupbox)
        deleteUserBtn.setGeometry(320, 22, 130, 25)
        deleteUserBtn.setText("Dodaj / Modyf. Użytk.")
        deleteUserBtn.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Bold))
        deleteUserBtn.clicked.connect(lambda: self.addUser(accountName.text(), accountPass.text(), accountLevel.isChecked(), accountID.text()))


        tree = QtWidgets.QTreeWidget(groupbox)
        tree.setGeometry(10, 100, 450, 130)
        tree.setColumnCount(5)
        tree.setHeaderLabels(["ID", "Nazwa", "Hasło", "Data", "Uprawnienia"])
        tree.setColumnWidth(0, 50)
        tree.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        self.account = tree
        self.renderUser()

        return tree


    def renderPin(self):
        iden = 0
        self.pinsPower.clear()
        for i in self._config["PINS"]["POWER_PINS"]:
            item = QtWidgets.QTreeWidgetItem(self.pinsPower)
            item.setText(0, str(iden))
            item.setText(1, str(i[0]))
            item.setText(2, str(i[1]))
            item.setText(3, str(i[2]))
            iden += 1

    def addPin(self, number, name, state, iden):
        if number == "":
            self.errorMessageBox("Nie wypełniono wszystkich pól!")
            return

        try:
            number = int(number)
        except:
            self.errorMessageBox("Numer pinu musi być liczbą!")
            return
        if iden != "":
            try:
                iden = int(iden)
            except:
                self.errorMessageBox("ID pinu musi być liczbą!")
                return

            if len(self._config["PINS"]["POWER_PINS"])-1 >= iden:
                self._config["PINS"]["POWER_PINS"][iden][0] = number
                self._config["PINS"]["POWER_PINS"][iden][1] = name
                self._config["PINS"]["POWER_PINS"][iden][2] = state
                self.renderPin()
                self.saveConfig()
                return

        for i in self._config["PINS"]["POWER_PINS"]:
            if i[0] == number:
                self.errorMessageBox("Pin o takim numerze już istnieje!")
                return

        self._config["PINS"]["POWER_PINS"].append([number, name, state])
        self.renderPin()
        self.saveConfig()

    def deletePin(self, iden):
        try:
            iden = int(iden)
        except:
            self.errorMessageBox("ID pinu musi być liczbą!")
            return

        if iden != "" and len(self._config["PINS"]["POWER_PINS"])-1 >= iden:
            self._config["PINS"]["POWER_PINS"].pop(iden)
            self.renderPin()
            self.saveConfig()
        else:
            self.errorMessageBox("Nie ma takiego pinu!")


    def pinsPower(self):
        if "PINS" not in self._config:
            self._config["PINS"] = []
        if "POWER_PINS" not in self._config["PINS"]:
            self._config["PINS"]["POWER_PINS"] = []

        groupbox = QtWidgets.QGroupBox("Piny Przełączeniowe / Zasilające", self)
        groupbox.setGeometry(510, 15, 470, 240)
        groupbox.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("ID:")
        lb.setGeometry(40, 10, 150, 50)

        pinID = QtWidgets.QLineEdit(groupbox)
        pinID.setGeometry(65, 25, 100, 20)
        pinID.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        deletePinBtn = QtWidgets.QPushButton(groupbox)
        deletePinBtn.setGeometry(180, 22, 130, 25)
        deletePinBtn.setText("Usuń pin")
        deletePinBtn.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Bold))
        deletePinBtn.clicked.connect(lambda: self.deletePin(pinID.text()))


        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Numer:")
        lb.setGeometry(10, 45, 100, 50)

        pinNumber = QtWidgets.QLineEdit(groupbox)
        pinNumber.setGeometry(65, 60, 100, 20)
        pinNumber.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Nazwa:")
        lb.setGeometry(180, 45, 100, 50)

        pinName = QtWidgets.QLineEdit(groupbox)
        pinName.setGeometry(235, 60, 100, 20)
        pinName.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))


        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Stan pocz.:")
        lb.setGeometry(350, 45, 100, 50)

        pinState = QtWidgets.QCheckBox(parent=groupbox)
        pinState.setGeometry(430, 61, 100, 20)

        savePin = QtWidgets.QPushButton(groupbox)
        savePin.setGeometry(320, 22, 130, 25)
        savePin.setText("Dodaj / Modyf. Pin")
        savePin.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Bold))
        savePin.clicked.connect(lambda: self.addPin(pinNumber.text(), pinName.text(), pinState.isChecked(), pinID.text()))

        tree = QtWidgets.QTreeWidget(groupbox)
        tree.setGeometry(10, 90, 450, 130)
        tree.setColumnCount(4)
        tree.setHeaderLabels(["ID", "Numer", "Nazwa", "Stan początkowy"])
        tree.setColumnWidth(0, 50)
        tree.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        self.pinsPower = tree
        self.renderPin()
        return tree

    def renderTempPin(self):
        self.tempPins.clear()
        iden = 0
        for tp in self._config["PINS"]["TEMP_PINS"]:
            item = QtWidgets.QTreeWidgetItem(self.tempPins)
            item.setText(0, str(iden))
            item.setText(1, str(tp[0]))
            item.setText(2, str(tp[1]))
            for ap in self._config["PINS"]["AIR_PINS"]:
                if ap[2] == tp[0]:
                    item.setText(3, str(ap[0]))
            for hp in self._config["PINS"]["HEAT_PINS"]:
                if hp[2] == tp[0]:
                    item.setText(4, str(hp[0]))
            for td in self._config["PINS"]["TEMP_DATA"]:
                if td[0] == tp[0]:
                    item.setText(5, str(td[1]))
            iden += 1

    def addTempPin(self, number, name, airPin, heatPin, tempData, iden):
        if number == "":
            self.errorMessageBox("Numer pinu nie może być pusty!")
            return

        try:
            number = int(number)
        except:
            self.errorMessageBox("Numer pinu musi być liczbą!")
            return


        try:
            airPin = int(airPin)
        except:
            self.errorMessageBox("Numer pinu powietrza musi być liczbą!")
            return

        try:
            heatPin = int(heatPin)
        except:
            self.errorMessageBox("Numer pinu ogrzewania musi być liczbą!")
            return

        try:
            tempData = float(tempData)
        except:
            self.errorMessageBox("Temperatura musi być liczbą!")
            return
        if iden != "":
            try:
                iden = int(iden)
            except:
                self.errorMessageBox("ID pinu musi być liczbą!")
                return

            if len(self._config["PINS"]["TEMP_PINS"])-1 >= iden:
                for ap in self._config["PINS"]["AIR_PINS"]:
                    if self._config["PINS"]["TEMP_PINS"][iden][0] == ap[2]:
                        ap[2] = number
                for hp in self._config["PINS"]["HEAT_PINS"]:
                    if self._config["PINS"]["TEMP_PINS"][iden][0] == hp[2]:
                        hp[2] = number
                for td in self._config["PINS"]["TEMP_DATA"]:
                    if self._config["PINS"]["TEMP_PINS"][iden][0] == td[0]:
                        td[1] = tempData

                self._config["PINS"]["TEMP_PINS"][iden][0] = number
                self._config["PINS"]["TEMP_PINS"][iden][1] = name

                self.renderTempPin()
                self.saveConfig()
                return

        for i in self._config["PINS"]["TEMP_PINS"]:
            if i[0] == number:
                self.errorMessageBox("Pin o podanym numerze już istnieje!")
                return
        airIS = False
        for i in self._config['PINS']["POWER_PINS"]:
            if i[0] == airPin:
                airIS = True
        if not airIS:
            self.errorMessageBox("Pin chłodzący nie istnieje w tablicy z pinami. Patrzy tabele powyżej!")
            return

        heatIS = False
        for i in self._config['PINS']["POWER_PINS"]:
            if i[0] == heatPin:
                heatIS = True
        if not heatIS:
            self.errorMessageBox("Pin grzejący nie istnieje w tablicy z pinami. Patrzy tabele powyżej!")
            return

        self._config["PINS"]["TEMP_PINS"].append([number, name])
        for i in self._config["PINS"]["POWER_PINS"]:
            if i[0] == airPin:
                self._config["PINS"]["AIR_PINS"].append([airPin, i[1], number])

        for i in self._config['PINS']["POWER_PINS"]:
            if i[0] == heatPin:
                self._config['PINS']["HEAT_PINS"].append([heatPin, i[1], number])
        self._config["PINS"]["TEMP_DATA"].append([number, tempData])
        self.renderTempPin()
        self.saveConfig()

    def delTempPin(self, iden):
        try:
            iden = int(iden)
        except:
            self.errorMessageBox("ID pinu musi być liczbą!")
            return

        if iden != "" and len(self._config["PINS"]["TEMP_PINS"])-1 >= iden:
            for ap in self._config["PINS"]["AIR_PINS"]:
                if self._config["PINS"]["TEMP_PINS"][iden][0] == ap[2]:
                    self._config["PINS"]["AIR_PINS"].remove(ap)
            for hp in self._config["PINS"]["HEAT_PINS"]:
                if self._config["PINS"]["TEMP_PINS"][iden][0] == hp[2]:
                    self._config["PINS"]["HEAT_PINS"].remove(hp)
            for td in self._config["PINS"]["TEMP_DATA"]:
                if self._config["PINS"]["TEMP_PINS"][iden][0] == td[0]:
                    self._config["PINS"]["TEMP_DATA"].remove(td)
            self._config["PINS"]["TEMP_PINS"].remove(self._config["PINS"]["TEMP_PINS"][iden])
            self.renderTempPin()
            self.saveConfig()
        else:
            self.errorMessageBox("Nie ma pinu z takim ID")
        return

    def tempPins(self):
        if "PINS" not in self._config:
            self._config["PINS"] = []
        if "TEMP_PINS" not in self._config["PINS"]:
            self._config["PINS"]["TEMP_PINS"] = []
        if "AIR_PINS" not in self._config["PINS"]:
            self._config["PINS"]["AIR_PINS"] = []
        if "HEAT_PINS" not in self._config["PINS"]:
            self._config["PINS"]["HEAT_PINS"] = []
        if "TEMP_DATA" not in self._config["PINS"]:
            self._config["PINS"]["TEMP_DATA"] = []

        groupbox = QtWidgets.QGroupBox("Piny Czujników Temperatury", self)
        groupbox.setGeometry(510, 260, 470, 240)
        groupbox.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("ID:")
        lb.setGeometry(40, 10, 150, 50)

        pinID = QtWidgets.QLineEdit(groupbox)
        pinID.setGeometry(65, 25, 100, 20)
        pinID.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        deletePinBtn = QtWidgets.QPushButton(groupbox)
        deletePinBtn.setGeometry(180, 22, 130, 25)
        deletePinBtn.setText("Usuń pin")
        deletePinBtn.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Bold))
        deletePinBtn.clicked.connect(lambda: self.delTempPin(pinID.text()))


        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Numer:")
        lb.setGeometry(10, 45, 100, 50)

        pinNumber = QtWidgets.QLineEdit(groupbox)
        pinNumber.setGeometry(65, 60, 50, 20)
        pinNumber.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Nazwa:")
        lb.setGeometry(130, 45, 100, 50)

        pinName = QtWidgets.QLineEdit(groupbox)
        pinName.setGeometry(185, 60, 100, 20)
        pinName.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Pin Chło.:")
        lb.setGeometry(300, 45, 100, 50)

        pinAir = QtWidgets.QLineEdit(groupbox)
        pinAir.setGeometry(370, 60, 50, 20)
        pinAir.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Pin Podgrz.:")
        lb.setGeometry(30, 80, 100, 50)

        pinHeat = QtWidgets.QLineEdit(groupbox)
        pinHeat.setGeometry(125, 95, 50, 20)
        pinHeat.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        lb = QtWidgets.QLabel(groupbox)
        lb.setText("Utrzym. Temp.:")
        lb.setGeometry(190, 80, 100, 50)

        temp = QtWidgets.QLineEdit(groupbox)
        temp.setGeometry(295, 95, 50, 20)
        temp.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        savePin = QtWidgets.QPushButton(groupbox)
        savePin.setGeometry(320, 22, 130, 25)
        savePin.setText("Dodaj / Modyf. Pin")
        savePin.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Bold))
        savePin.clicked.connect(lambda: self.addTempPin(pinNumber.text(), pinName.text(), pinAir.text(), pinHeat.text(), temp.text(), pinID.text()))

        tree = QtWidgets.QTreeWidget(groupbox)
        tree.setGeometry(10, 130, 450, 100)
        tree.setColumnCount(6)
        tree.setHeaderLabels(["ID", "Numer Pinu", "Nazwa", "Pin Chłod.", "Pin Podgrz.", "Utrzym. Temp."])
        tree.setColumnWidth(0, 20)
        tree.setColumnWidth(1, 65)
        tree.setColumnWidth(2, 80)
        tree.setColumnWidth(3, 80)
        tree.setColumnWidth(4, 80)
        tree.setColumnWidth(5, 70)
        tree.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Normal))

        self.tempPins = tree
        self.renderTempPin()

        return tree

    def openConfigFileInEditor(self):
        os.system("notepad.exe " + self.basePathConfig + "configFile.json")

    def openConfigFolder(self):
        os.system("explorer.exe " + os.path.dirname(os.getcwd() + self.basePathConfig))

    def mainOption(self):
        closeBtn = QtWidgets.QPushButton(self)
        closeBtn.setGeometry(750, 525, 200, 50)
        closeBtn.setText("Zapis")
        closeBtn.setFont(QtGui.QFont("Arial", 10, weight=QtGui.QFont.Bold))
        closeBtn.clicked.connect(lambda: QtWidgets.QMessageBox.information(self, "Informacja", "Konfiguracja została zapisana."))

        saveBtn = QtWidgets.QPushButton(self)
        saveBtn.setGeometry(520, 520, 200, 25)
        saveBtn.setText("Otworz Plik Konfiguracyjny")
        saveBtn.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Bold))
        saveBtn.clicked.connect(lambda: self.openConfigFileInEditor())

        saveBtn = QtWidgets.QPushButton(self)
        saveBtn.setGeometry(520, 550, 200, 25)
        saveBtn.setText("Otworz Folder Konfiguracyjny")
        saveBtn.setFont(QtGui.QFont("Arial", 8, weight=QtGui.QFont.Bold))
        saveBtn.clicked.connect(lambda: self.openConfigFolder())

    def closeEvent(self, event):
        self.close()
        event.accept()
