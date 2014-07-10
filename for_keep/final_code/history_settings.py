# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'history_dialog.ui'
#
# Created: Sun Jun  8 13:50:08 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(572, 382)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.history_edit = QtGui.QPlainTextEdit(Dialog)
        self.history_edit.setReadOnly(True)
        self.history_edit.setCenterOnScroll(False)
        self.history_edit.setObjectName("history_edit")
        self.verticalLayout.addWidget(self.history_edit)
        self.gridLayout_2.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.refresh_Btn = QtGui.QPushButton(Dialog)
        self.refresh_Btn.setObjectName("refresh_Btn")
        self.horizontalLayout_3.addWidget(self.refresh_Btn)
        self.commands_only = QtGui.QCheckBox(Dialog)
        self.commands_only.setObjectName("commands_only")
        self.horizontalLayout_3.addWidget(self.commands_only)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.clear_history_btn = QtGui.QPushButton(Dialog)
        self.clear_history_btn.setObjectName("clear_history_btn")
        self.horizontalLayout.addWidget(self.clear_history_btn)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh_Btn.setText(QtGui.QApplication.translate("Dialog", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh_Btn.setShortcut(QtGui.QApplication.translate("Dialog", "Meta+R", None, QtGui.QApplication.UnicodeUTF8))
        self.commands_only.setText(QtGui.QApplication.translate("Dialog", "Commands Only", None, QtGui.QApplication.UnicodeUTF8))
        self.clear_history_btn.setText(QtGui.QApplication.translate("Dialog", "Clear History", None, QtGui.QApplication.UnicodeUTF8))

