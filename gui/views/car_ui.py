# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'car.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(963, 437)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget = QtWidgets.QWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(500, 300))
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.plotLayout = QtWidgets.QVBoxLayout()
        self.plotLayout.setObjectName("plotLayout")
        self.horizontalLayout_2.addLayout(self.plotLayout)
        self.horizontalLayout.addWidget(self.widget)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.carListWidget = QtWidgets.QListWidget(Form)
        self.carListWidget.setObjectName("carListWidget")
        self.verticalLayout_2.addWidget(self.carListWidget)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.v_t = QtWidgets.QCheckBox(self.groupBox)
        self.v_t.setObjectName("v_t")
        self.verticalLayout.addWidget(self.v_t)
        self.s_t = QtWidgets.QCheckBox(self.groupBox)
        self.s_t.setObjectName("s_t")
        self.verticalLayout.addWidget(self.s_t)
        self.mpv_t = QtWidgets.QCheckBox(self.groupBox)
        self.mpv_t.setObjectName("mpv_t")
        self.verticalLayout.addWidget(self.mpv_t)
        self.mps_t = QtWidgets.QCheckBox(self.groupBox)
        self.mps_t.setObjectName("mps_t")
        self.verticalLayout.addWidget(self.mps_t)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.btnRefresh = QtWidgets.QPushButton(Form)
        self.btnRefresh.setObjectName("btnRefresh")
        self.verticalLayout_2.addWidget(self.btnRefresh)
        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Options"))
        self.v_t.setText(_translate("Form", "v (t)"))
        self.s_t.setText(_translate("Form", "s (t)"))
        self.mpv_t.setText(_translate("Form", "mpv (t)"))
        self.mps_t.setText(_translate("Form", "mps (t)"))
        self.btnRefresh.setText(_translate("Form", "Refresh"))

