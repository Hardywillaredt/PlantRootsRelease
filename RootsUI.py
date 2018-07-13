# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RootsUI.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RootsUI(object):
    def setupUi(self, RootsUI):
        RootsUI.setObjectName("RootsUI")
        RootsUI.resize(1026, 707)
        self.gridLayout = QtWidgets.QGridLayout(RootsUI)
        self.gridLayout.setObjectName("gridLayout")
        self.LoadFile_4 = QtWidgets.QPushButton(RootsUI)
        self.LoadFile_4.setObjectName("LoadFile_4")
        self.gridLayout.addWidget(self.LoadFile_4, 0, 3, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(RootsUI)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 3, 1, 1)
        self.LoadFile = QtWidgets.QPushButton(RootsUI)
        self.LoadFile.setObjectName("LoadFile")
        self.gridLayout.addWidget(self.LoadFile, 0, 0, 1, 1)
        self.OperationOne = QtWidgets.QPushButton(RootsUI)
        self.OperationOne.setObjectName("OperationOne")
        self.gridLayout.addWidget(self.OperationOne, 0, 1, 1, 1)
        self.LoadFile_3 = QtWidgets.QPushButton(RootsUI)
        self.LoadFile_3.setObjectName("LoadFile_3")
        self.gridLayout.addWidget(self.LoadFile_3, 0, 2, 1, 1)
        self.GLWidgetHolder = QtWidgets.QWidget(RootsUI)
        self.GLWidgetHolder.setObjectName("GLWidgetHolder")
        self.gridLayout.addWidget(self.GLWidgetHolder, 1, 0, 1, 4)

        self.retranslateUi(RootsUI)
        self.buttonBox.accepted.connect(RootsUI.accept)
        self.buttonBox.rejected.connect(RootsUI.reject)
        QtCore.QMetaObject.connectSlotsByName(RootsUI)

    def retranslateUi(self, RootsUI):
        _translate = QtCore.QCoreApplication.translate
        RootsUI.setWindowTitle(_translate("RootsUI", "Dialog"))
        self.LoadFile_4.setText(_translate("RootsUI", "Split"))
        self.LoadFile.setText(_translate("RootsUI", "Load File"))
        self.OperationOne.setText(_translate("RootsUI", "Connect"))
        self.LoadFile_3.setText(_translate("RootsUI", "Disconnect"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    RootsUI = QtWidgets.QDialog()
    ui = Ui_RootsUI()
    ui.setupUi(RootsUI)
    RootsUI.show()
    sys.exit(app.exec_())

