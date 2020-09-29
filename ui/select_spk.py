# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'select_spk.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoadSpkDialog(object):
    def setupUi(self, LoadSpkDialog):
        LoadSpkDialog.setObjectName("LoadSpkDialog")
        LoadSpkDialog.resize(575, 323)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        LoadSpkDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(LoadSpkDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(LoadSpkDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spk_tableWidget = QtWidgets.QTableWidget(LoadSpkDialog)
        self.spk_tableWidget.setObjectName("spk_tableWidget")
        self.spk_tableWidget.setColumnCount(2)
        self.spk_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.spk_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.spk_tableWidget.setHorizontalHeaderItem(1, item)
        self.horizontalLayout.addWidget(self.spk_tableWidget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.frame = QtWidgets.QFrame(LoadSpkDialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.selectButton = QtWidgets.QPushButton(self.frame)
        self.selectButton.setMinimumSize(QtCore.QSize(0, 50))
        self.selectButton.setMaximumSize(QtCore.QSize(120, 16777215))
        self.selectButton.setObjectName("selectButton")
        self.horizontalLayout_2.addWidget(self.selectButton)
        self.cancleButton = QtWidgets.QPushButton(self.frame)
        self.cancleButton.setMinimumSize(QtCore.QSize(0, 50))
        self.cancleButton.setMaximumSize(QtCore.QSize(120, 16777215))
        self.cancleButton.setObjectName("cancleButton")
        self.horizontalLayout_2.addWidget(self.cancleButton)
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(LoadSpkDialog)
        QtCore.QMetaObject.connectSlotsByName(LoadSpkDialog)

    def retranslateUi(self, LoadSpkDialog):
        _translate = QtCore.QCoreApplication.translate
        LoadSpkDialog.setWindowTitle(_translate("LoadSpkDialog", "选择已有说话人"))
        self.label.setText(_translate("LoadSpkDialog", "选择说话人："))
        item = self.spk_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("LoadSpkDialog", "说话人标识"))
        item = self.spk_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("LoadSpkDialog", "说话人名称"))
        self.selectButton.setText(_translate("LoadSpkDialog", "加载"))
        self.cancleButton.setText(_translate("LoadSpkDialog", "取消"))
