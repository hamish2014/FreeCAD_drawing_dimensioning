# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'toleranceDialog.ui'
#
# Created: Mon Jun  8 14:50:14 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from drawingDimensioning.py3_helpers import translate
from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(209, 149)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.placeButton = QtGui.QPushButton(Dialog)
        self.placeButton.setObjectName("placeButton")
        self.gridLayout_2.addWidget(self.placeButton, 2, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(61, 0))
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.upperLineEdit = QtGui.QLineEdit(Dialog)
        self.upperLineEdit.setObjectName("upperLineEdit")
        self.gridLayout.addWidget(self.upperLineEdit, 0, 1, 1, 1)
        self.lowerLineEdit = QtGui.QLineEdit(Dialog)
        self.lowerLineEdit.setObjectName("lowerLineEdit")
        self.gridLayout.addWidget(self.lowerLineEdit, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.scaleDoubleSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.scaleDoubleSpinBox.setMinimum(0.05)
        self.scaleDoubleSpinBox.setSingleStep(0.05)
        self.scaleDoubleSpinBox.setProperty("value", 0.8)
        self.scaleDoubleSpinBox.setObjectName("scaleDoubleSpinBox")
        self.gridLayout.addWidget(self.scaleDoubleSpinBox, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.placeButton, QtCore.SIGNAL("released()"), Dialog.accept)
        QtCore.QObject.connect(self.upperLineEdit, QtCore.SIGNAL("returnPressed()"), Dialog.accept)
        QtCore.QObject.connect(self.lowerLineEdit, QtCore.SIGNAL("returnPressed()"), Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(translate("Dialog", "Add tolerance", None))
        self.placeButton.setText(translate("Dialog", "Add", None))
        self.label.setText(translate("Dialog", "upper", None))
        self.label_2.setText(translate("Dialog", "lower", None))
        self.upperLineEdit.setText(translate("Dialog", "+0", None))
        self.lowerLineEdit.setText(translate("Dialog", "-0", None))
        self.label_3.setText(translate("Dialog", "font scale", None))

