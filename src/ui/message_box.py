# -*- coding:utf-8 -*-

from PyQt5.QtWidgets import QMessageBox

class CMyMessageBox(QMessageBox):
    def __init__(self, parent=None):
        pass

    def showEvent(self, event):
        print("show")
        __super().showEvent(event)
        self.setFixedSize(640, 480)
