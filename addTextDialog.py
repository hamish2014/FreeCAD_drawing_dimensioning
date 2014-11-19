# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addTextDialog.ui'
#
# Created: Wed Oct 29 11:28:43 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(263, 146)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout.setObjectName("gridLayout")
        self.textSizeSpinBox = QtGui.QSpinBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textSizeSpinBox.sizePolicy().hasHeightForWidth())
        self.textSizeSpinBox.setSizePolicy(sizePolicy)
        self.textSizeSpinBox.setMinimum(2)
        self.textSizeSpinBox.setProperty("value", 6)
        self.textSizeSpinBox.setObjectName("textSizeSpinBox")
        self.gridLayout.addWidget(self.textSizeSpinBox, 1, 2, 1, 1)
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
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.placeButton = QtGui.QPushButton(Dialog)
        self.placeButton.setObjectName("placeButton")
        self.gridLayout_2.addWidget(self.placeButton, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.placeButton, QtCore.SIGNAL("released()"), Dialog.accept)
        QtCore.QObject.connect(self.textLineEdit, QtCore.SIGNAL("returnPressed()"), Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.textLineEdit, self.textSizeSpinBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Add Text", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Text:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Font-size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Color", None, QtGui.QApplication.UnicodeUTF8))
        self.colorLineEdit.setText(QtGui.QApplication.translate("Dialog", "rgb(0,0,0)", None, QtGui.QApplication.UnicodeUTF8))
        self.placeButton.setText(QtGui.QApplication.translate("Dialog", "Place Text", None, QtGui.QApplication.UnicodeUTF8))

