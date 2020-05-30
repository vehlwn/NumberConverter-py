from mainwindow import MainWindow
from PyQt5 import QtWidgets
import sys


def main():
    a = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    main()
