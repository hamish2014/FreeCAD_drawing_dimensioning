# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'textAddDialog.ui'
#
# Created: Mon Feb 16 15:24:58 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(245, 179)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout.setObjectName("gridLayout")
        self.textLineEdit = QtGui.QLineEdit(Dialog)
        self.textLineEdit.setObjectName("textLineEdit")
        self.gridLayout.addWidget(self.textLineEdit, 0, 2, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(61, 0))
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.colorLineEdit = QtGui.QLineEdit(Dialog)
        self.colorLineEdit.setObjectName("colorLineEdit")
        self.gridLayout.addWidget(self.colorLineEdit, 2, 2, 1, 1)
        self.sizeLineEdit = QtGui.QLineEdit(Dialog)
        self.sizeLineEdit.setObjectName("sizeLineEdit")
        self.gridLayout.addWidget(self.sizeLineEdit, 1, 2, 1, 1)
        self.familyLineEdit = QtGui.QLineEdit(Dialog)
        self.familyLineEdit.setObjectName("familyLineEdit")
        self.gridLayout.addWidget(self.familyLineEdit, 3, 2, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.placeButton = QtGui.QPushButton(Dialog)
        self.placeButton.setObjectName("placeButton")
        self.gridLayout_2.addWidget(self.placeButton, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.placeButton, QtCore.SIGNAL("released()"), Dialog.accept)
        QtCore.QObject.connect(self.textLineEdit, QtCore.SIGNAL("returnPressed()"), Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Add Text", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Text:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Font-size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Color", None, QtGui.QApplication.UnicodeUTF8))
        self.colorLineEdit.setText(QtGui.QApplication.translate("Dialog", "rgb(255,0,0)", None, QtGui.QApplication.UnicodeUTF8))
        self.sizeLineEdit.setText(QtGui.QApplication.translate("Dialog", "4pt", None, QtGui.QApplication.UnicodeUTF8))
        self.familyLineEdit.setText(QtGui.QApplication.translate("Dialog", "Verdana", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Family", None, QtGui.QApplication.UnicodeUTF8))
        self.placeButton.setText(QtGui.QApplication.translate("Dialog", "Place Text", None, QtGui.QApplication.UnicodeUTF8))

