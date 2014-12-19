# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../ui_files/new_dev.ui'
#
# Created: Fri Dec 19 12:53:11 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(619, 391)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(Dialog)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.address_label = QtGui.QLabel(Dialog)
        self.address_label.setObjectName("address_label")
        self.horizontalLayout.addWidget(self.address_label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.address_box = QtGui.QComboBox(Dialog)
        self.address_box.setObjectName("address_box")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.address_box.addItem("")
        self.horizontalLayout.addWidget(self.address_box)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.listWidget = QtGui.QListWidget(Dialog)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.address_label.setText(QtGui.QApplication.translate("Dialog", "Pump Address", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(0, QtGui.QApplication.translate("Dialog", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(1, QtGui.QApplication.translate("Dialog", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(2, QtGui.QApplication.translate("Dialog", "2", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(3, QtGui.QApplication.translate("Dialog", "3", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(4, QtGui.QApplication.translate("Dialog", "4", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(5, QtGui.QApplication.translate("Dialog", "5", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(6, QtGui.QApplication.translate("Dialog", "6", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(7, QtGui.QApplication.translate("Dialog", "7", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(8, QtGui.QApplication.translate("Dialog", "8", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(9, QtGui.QApplication.translate("Dialog", "9", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(10, QtGui.QApplication.translate("Dialog", "A", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(11, QtGui.QApplication.translate("Dialog", "B", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(12, QtGui.QApplication.translate("Dialog", "C", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(13, QtGui.QApplication.translate("Dialog", "D", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(14, QtGui.QApplication.translate("Dialog", "E", None, QtGui.QApplication.UnicodeUTF8))
        self.address_box.setItemText(15, QtGui.QApplication.translate("Dialog", "F", None, QtGui.QApplication.UnicodeUTF8))

