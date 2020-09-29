#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:WILLIAM
@file: main.py
@time: 20:43
@Device: Personal Win10
@Description: 
"""
import os
import sys
import datetime

import pyaudio
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets

from ui.win_define import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    myWin = MainWindow()
    myWin.show()

    reco = app.exec_()
    sys.exit(reco)