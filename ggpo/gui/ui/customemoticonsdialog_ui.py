# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ggpo/gui/ui/customemoticonsdialog.ui'
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

class Ui_EmoticonDialog(object):
    def setupUi(self, EmoticonDialog):
        EmoticonDialog.setObjectName(_fromUtf8("EmoticonDialog"))
        EmoticonDialog.resize(300, 500)
        self.verticalLayout = QtGui.QVBoxLayout(EmoticonDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(EmoticonDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.uiEmoticonTextEdit = QtGui.QTextEdit(EmoticonDialog)
        self.uiEmoticonTextEdit.setObjectName(_fromUtf8("uiEmoticonTextEdit"))
        self.verticalLayout.addWidget(self.uiEmoticonTextEdit)
        self.buttonBox = QtGui.QDialogButtonBox(EmoticonDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(EmoticonDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EmoticonDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EmoticonDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EmoticonDialog)

    def retranslateUi(self, EmoticonDialog):
        EmoticonDialog.setWindowTitle(_translate("EmoticonDialog", "Custom Emoticons", None))
        self.label.setText(_translate("EmoticonDialog", "One emoticon per line", None))

