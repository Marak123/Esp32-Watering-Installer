from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class window(QtWidgets.QWidget, QtCore.QObject):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.resize(500,600)
        self.setWindowTitle("Base APP")

        self.button = QtWidgets.QPushButton("Click me!")
        self.button.clicked.connect(self.on_click)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("QLabel { background-color : #A0A0A0; color : #FFFFFF; font-size : 30px; }")
        self.label.setText("Hello World!")
        self.label.setGeometry(0, 0, 500, 100)
        self.label.show()

    def on_click(self):
        print("Clicked!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = window()
    window.show()
    sys.exit(app.exec_())