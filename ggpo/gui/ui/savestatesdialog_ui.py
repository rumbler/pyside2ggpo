# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ggpo/gui/ui/savestatesdialog.ui'
#
# Created: Tue Aug 25 22:55:14 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SavestatesDialog(object):
    def setupUi(self, SavestatesDialog):
        SavestatesDialog.setObjectName(_fromUtf8("SavestatesDialog"))
        SavestatesDialog.resize(630, 600)
        self.verticalLayout = QtGui.QVBoxLayout(SavestatesDialog)
        self.verticalLayout.setContentsMargins(2, 0, 2, 6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(SavestatesDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.uiFilterLineEdit = QtGui.QLineEdit(SavestatesDialog)
        self.uiFilterLineEdit.setText(_fromUtf8(""))
        self.uiFilterLineEdit.setObjectName(_fromUtf8("uiFilterLineEdit"))
        self.horizontalLayout.addWidget(self.uiFilterLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.uiSavestatesTblv = QtGui.QTableView(SavestatesDialog)
        self.uiSavestatesTblv.setObjectName(_fromUtf8("uiSavestatesTblv"))
        self.verticalLayout.addWidget(self.uiSavestatesTblv)
        self.uiButtonBox = QtGui.QDialogButtonBox(SavestatesDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.verticalLayout.addWidget(self.uiButtonBox)

        self.retranslateUi(SavestatesDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SavestatesDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SavestatesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SavestatesDialog)
        SavestatesDialog.setTabOrder(self.uiFilterLineEdit, self.uiSavestatesTblv)
        SavestatesDialog.setTabOrder(self.uiSavestatesTblv, self.uiButtonBox)

    def retranslateUi(self, SavestatesDialog):
        SavestatesDialog.setWindowTitle(_translate("SavestatesDialog", "Unsupported game savestates", None))
        self.label.setText(_translate("SavestatesDialog", "Filter:", None))

