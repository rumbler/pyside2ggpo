# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ggpo/gui/ui/logindialog.ui'
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

class Ui_DialogLogin(object):
    def setupUi(self, DialogLogin):
        DialogLogin.setObjectName(_fromUtf8("DialogLogin"))
        DialogLogin.resize(430, 286)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/assets/icon-128.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogLogin.setWindowIcon(icon)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(DialogLogin)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.labelGGPOLogo = QtGui.QLabel(DialogLogin)
        self.labelGGPOLogo.setText(_fromUtf8(""))
        self.labelGGPOLogo.setPixmap(QtGui.QPixmap(_fromUtf8(":/assets/logo-vertical.png")))
        self.labelGGPOLogo.setObjectName(_fromUtf8("labelGGPOLogo"))
        self.horizontalLayout_2.addWidget(self.labelGGPOLogo)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.labelUsername = QtGui.QLabel(DialogLogin)
        self.labelUsername.setObjectName(_fromUtf8("labelUsername"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.labelUsername)
        self.uiUsernameLine = QtGui.QLineEdit(DialogLogin)
        self.uiUsernameLine.setObjectName(_fromUtf8("uiUsernameLine"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.uiUsernameLine)
        self.labelPassword = QtGui.QLabel(DialogLogin)
        self.labelPassword.setObjectName(_fromUtf8("labelPassword"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.labelPassword)
        self.uiPasswordLine = QtGui.QLineEdit(DialogLogin)
        self.uiPasswordLine.setEchoMode(QtGui.QLineEdit.Password)
        self.uiPasswordLine.setObjectName(_fromUtf8("uiPasswordLine"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.uiPasswordLine)
        self.uiSavePasswordChk = QtGui.QCheckBox(DialogLogin)
        self.uiSavePasswordChk.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.uiSavePasswordChk.setChecked(True)
        self.uiSavePasswordChk.setObjectName(_fromUtf8("uiSavePasswordChk"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.uiSavePasswordChk)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiRegisterLink = QtGui.QCommandLinkButton(DialogLogin)
        self.uiRegisterLink.setObjectName(_fromUtf8("uiRegisterLink"))
        self.horizontalLayout.addWidget(self.uiRegisterLink)
        self.uiLoginBtn = QtGui.QCommandLinkButton(DialogLogin)
        self.uiLoginBtn.setObjectName(_fromUtf8("uiLoginBtn"))
        self.horizontalLayout.addWidget(self.uiLoginBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.uiErrorLbl = QtGui.QLabel(DialogLogin)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiErrorLbl.sizePolicy().hasHeightForWidth())
        self.uiErrorLbl.setSizePolicy(sizePolicy)
        self.uiErrorLbl.setMouseTracking(False)
        self.uiErrorLbl.setStyleSheet(_fromUtf8("QLabel { color : red; font-weight: bold}"))
        self.uiErrorLbl.setText(_fromUtf8(""))
        self.uiErrorLbl.setTextFormat(QtCore.Qt.PlainText)
        self.uiErrorLbl.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.uiErrorLbl.setWordWrap(True)
        self.uiErrorLbl.setObjectName(_fromUtf8("uiErrorLbl"))
        self.verticalLayout.addWidget(self.uiErrorLbl)
        self.horizontalLayout_21 = QtGui.QHBoxLayout()
        self.horizontalLayout_21.setObjectName(_fromUtf8("horizontalLayout_21"))
        self.uiNewVersionLink = QtGui.QCommandLinkButton(DialogLogin)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiNewVersionLink.sizePolicy().hasHeightForWidth())
        self.uiNewVersionLink.setSizePolicy(sizePolicy)
        self.uiNewVersionLink.setObjectName(_fromUtf8("uiNewVersionLink"))
        self.horizontalLayout_21.addWidget(self.uiNewVersionLink)
        self.uiVersionLbl = QtGui.QLabel(DialogLogin)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVersionLbl.sizePolicy().hasHeightForWidth())
        self.uiVersionLbl.setSizePolicy(sizePolicy)
        self.uiVersionLbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.uiVersionLbl.setObjectName(_fromUtf8("uiVersionLbl"))
        self.horizontalLayout_21.addWidget(self.uiVersionLbl)
        self.verticalLayout.addLayout(self.horizontalLayout_21)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.labelUsername.setBuddy(self.uiUsernameLine)
        self.labelPassword.setBuddy(self.uiPasswordLine)

        self.retranslateUi(DialogLogin)
        QtCore.QMetaObject.connectSlotsByName(DialogLogin)
        DialogLogin.setTabOrder(self.uiUsernameLine, self.uiPasswordLine)
        DialogLogin.setTabOrder(self.uiPasswordLine, self.uiSavePasswordChk)
        DialogLogin.setTabOrder(self.uiSavePasswordChk, self.uiLoginBtn)
        DialogLogin.setTabOrder(self.uiLoginBtn, self.uiRegisterLink)

    def retranslateUi(self, DialogLogin):
        DialogLogin.setWindowTitle(_translate("DialogLogin", "FightCade", None))
        self.labelUsername.setText(_translate("DialogLogin", "Username", None))
        self.labelPassword.setText(_translate("DialogLogin", "Password", None))
        self.uiSavePasswordChk.setText(_translate("DialogLogin", "Save Password", None))
        self.uiRegisterLink.setText(_translate("DialogLogin", "Create Account...", None))
        self.uiLoginBtn.setText(_translate("DialogLogin", "Login", None))
        self.uiNewVersionLink.setText(_translate("DialogLogin", "Download Update...", None))
        self.uiVersionLbl.setText(_translate("DialogLogin", "version", None))

#import ggpo_rc
