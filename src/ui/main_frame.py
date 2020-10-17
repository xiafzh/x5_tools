# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_tool_ui_iml import *
from src.logic.main_logic import *

class CMainUI:
    def __init__(self):
        self.app = QApplication(sys.argv)

    def Run(self):
        self.main_ui = Ui_MainWindowImpl()
        sys.exit(self.app.exec_())
        