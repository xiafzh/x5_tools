# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from src.logic.main_data import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QCursor
from functools import partial
from src.ui.main_tool_ui import *
from src.logic.main_logic import *
from src.logic.thread.thread_create_proj import *
from conf.common import *
import socket


class Ui_MainWindowImpl(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__(*args, **kwargs)
        self.lmgr = CMainLogic(self)
        self.choose_logger = ""

        self.setupUi(self)
        self.init_qq_btns()

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon32.ico"),QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.init_widget_data()
        self.init_event_bind()
        self.on_click_log_switch()

        self.show()

    def closeEvent(self,event):
        self.lmgr.closeWindow()
        

    def init_widget_data(self):
        # 屏蔽掉不可用功能按钮
        self.cbProjects.setEnabled(False)
        self.btnProjPath.setVisible(False)
        self.btnSrcPath.setVisible(False)


        self.cbIP.setEditable(True)
        #self.checkOnlyAdd.setCheckState(False)

        # 分支
        for item in self.lmgr.getAllBranches():
            self.cbBranches.addItem(item.title)
            if item.title == self.lmgr.sel_branch:
                self.cbBranches.setCurrentText(item.title)

        for item in self.lmgr.getAllProjects():
            self.cbProjects.addItem(item)

        self.RefreshWorkLogs(LogOpt_Init, None)

        hostname = socket.gethostname()
        ipaddrs = socket.gethostbyname_ex(hostname)[2]
        for ip in ipaddrs:
            if ip.startswith('192.168'):
                self.cbIP.addItem(ip)
                
    # 初始化QQ按钮
    def init_qq_btns(self):
        self.init_btn_menu()
        self.qq_btns = []
        for row in range(0, 5):
            for col in range(0, login_qq_column_count):
                btn = QPushButton(self.frame_2)
                btn.move(login_qq_x_interval * (col + 1) + login_qq_width * col
                    , login_qq_y_interval * (row + 3) + login_qq_height * row + self.btn_login.height())
                btn.setFixedSize(login_qq_width, login_qq_height)
                btn.setVisible(False)
                btn.clicked.connect(partial(self.on_click_qqbtn, btn))
                self.add_qq_btn_menu(btn)
                self.qq_btns.append(btn)
        self.refresh_qq_btn()

    def init_btn_menu(self):
        self.contextMenu = QMenu() 
        actionA = self.contextMenu.addAction(QIcon("images/0.png"),u'| 删除') 
        actionA.triggered.connect(self.delete_qq)
        actionA = self.contextMenu.addAction(QIcon("images/1.png"), u'| 自定义')
        actionA.triggered.connect(self.define_qq_btn)

    def add_qq_btn_menu(self, btn : QPushButton):
        btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(partial(self.show_context_menu, btn))

    def show_context_menu(self, btn : QPushButton):
        self.menu_btn = btn
        self.contextMenu.exec_(QCursor.pos())
        
    def delete_qq(self):
        if not self.menu_btn:
            return
        
        self.lmgr.RemoveLoginQQ(self.menu_btn.text())
        self.refresh_qq_btn()
        

    # 刷新QQ按钮显示
    def refresh_qq_btn(self, page = 0):
        begin_i = page * login_qq_column_count
        all_qqs = self.lmgr.getAllLoginQQ()
        len_qqs = len(all_qqs)
        for index in range(0, len(self.qq_btns)):
            if index + begin_i >= len_qqs:
                self.qq_btns[index].setVisible(False)
            else:
                self.qq_btns[index].setText(all_qqs[index + begin_i])
                self.qq_btns[index].setVisible(True)

    def init_event_bind(self):
        self.btnLogSwitch.clicked.connect(self.on_click_log_switch)
        self.btnStartServer.clicked.connect(self.slot_click_start_server)
        self.btnRemoveProj.clicked.connect(self.on_remove_proj)
        self.btnCreateProj.clicked.connect(self.slot_click_create_proj)
        self.btnCompile.clicked.connect(self.slot_click_compile)
        
        self.checkAutoCreate.stateChanged.connect(self.on_auto_create_change)
        self.checkOnlyAdd.stateChanged.connect(self.on_auto_create_change)
        self.checkSVN.stateChanged.connect(self.on_auto_create_change)

        self.btn_login.clicked.connect(self.on_click_login)
        self.log_combobox.currentTextChanged.connect(self.on_log_change)

        self.btnVSStarClient.clicked.connect(self.slot_click_vs_star_client)
        self.btnVSStarServer.clicked.connect(self.slot_click_vs_star_server)
        self.btnVSVideoClient.clicked.connect(self.slot_click_vs_video_client)
        self.btnVSVideoServer.clicked.connect(self.slot_click_vs_video_server)

        self.cbBranches.currentTextChanged.connect(self.slot_change_branches)

        self.btnSrcPath.clicked.connect(partial(self.slot_click_choose_dir, self.editResPath))
        self.btnProjPath.clicked.connect(partial(self.slot_click_choose_dir, self.editProjPath))

        self.BtnConsoleReplace.clicked.connect(self.slot_click_console_replacer)
        self.btnUIEditor.clicked.connect(self.slot_click_ui_editor)
        self.btnCancelReadonly.clicked.connect(self.slot_click_cancel_readonly)

    def slot_click_vs_star_client(self):
        self.lmgr.start_vs("star", "build_client.sln", self.cbBranches.currentText())

    def slot_click_vs_star_server(self):
        self.lmgr.start_vs("star", "build_server.sln", self.cbBranches.currentText())

    def slot_click_vs_video_client(self):
        self.lmgr.start_vs("video", "build_video_client.sln", self.cbBranches.currentText())
        
    def slot_click_vs_video_server(self):
        self.lmgr.start_vs("video", "build_video_server.sln", self.cbBranches.currentText())
        
    def on_click_log_switch(self):
        if (self.width() == 1280):
            self.setFixedWidth(791)
            self.btnLogSwitch.setText(">>>")
        else:
            self.setFixedWidth(1280)
            self.btnLogSwitch.setText("<<<")
    
    def on_log_change(self, sel_text):
        self.lmgr.switchLog(sel_text)
    
    def slot_click_start_server(self):
        print('启动服务器')
        self.lmgr.startServer(self.cbBranches.currentText(), self.cbIP.currentText())

    def on_click_login(self):
        qq = self.text_qq.text()
        if self.cb_save_login.isChecked():
            self.lmgr.saveLoginQQ(qq)
            self.refresh_qq_btn()

        self.on_click_qqbtn(self.text_qq)
    
    def on_click_qqbtn(self, widget : QWidget):
        qq = widget.text()
        if not qq.isnumeric():
            self.log_editbox.append('错误的qq %s'%qq)
            return
        
        res = self.lmgr.startLogin(qq, self.cbBranches.currentText(), self.cbDebug.isChecked(), self.cbIP.currentText())
        self.log_editbox.append(res)
      

    def on_add_proj(self):
        p4path = self.editP4Path.text()
        if "" == p4path:
            print("p4null")
            return 

        #如果勾选了，取P4路径计算
        if self.checkAutoCreate.isChecked():
            res, branch_name = self.lmgr.UpdateProjPath(p4path)
            if res:
                self.cbBranches.addItem(branch_name)
            return        
        
        proj_path = self.editProjPath.text()        
        res, branch_name = self.lmgr.UpdateProjPath(p4path, proj_path)
        if res:
            self.cbBranches.addItem(branch_name)
    
    def on_remove_proj(self):
        branch = self.cbBranches.currentText()
        if "" == branch:
            print("p4null")
            return 
        res, branch_index = self.lmgr.RemoveProjPath(branch)
        if res:
            self.cbBranches.removeItem(branch_index)

    def on_auto_create_change(self):
        self.editSVNStar.setEnabled(False)
        self.editSVNVideo.setEnabled(False) 
        self.editResPath.setEnabled(False)
        self.btnSrcPath.setEnabled(False)
        self.editProjPath.setEnabled(False)
        self.btnProjPath.setEnabled(False)
        
        if not self.checkAutoCreate.isChecked():
            self.editProjPath.setEnabled(True)
            self.btnProjPath.setEnabled(True)
            if not self.checkOnlyAdd.isChecked():
                self.editResPath.setEnabled(True)
                self.btnSrcPath.setEnabled(True)
                self.editSVNStar.setEnabled(self.checkSVN.isChecked())
                self.editSVNVideo.setEnabled(self.checkSVN.isChecked())                
           

    def slot_click_create_proj(self):
        if self.checkOnlyAdd.isChecked():
            self.on_add_proj()
        else:
            projpath = self.editProjPath.text()
            respath = self.editResPath.text()
            if self.checkAutoCreate.isChecked():
                projpath = ""
                respath = ""

            svn_star = self.editSVNStar.text()
            svn_video = self.editSVNVideo.text()
            if not self.checkSVN.isChecked():
                svn_star = ""
                svn_video = ""

            res = self.lmgr.CreateNewProj(self.editP4Path.text()
                , projpath, respath, svn_star, svn_video)
            if not res:
                self.log_editbox.append("CreateFailed")
                return
        #TODO::刷新分支
    
    def RefreshWorkLogs(self, log_opt, log_id, log_content = ""):
        #print("refresh log", log_opt, log_id, len(log_content))
        if LogOpt_Init == log_opt:
            self.log_combobox.clear()
            all_logger = self.lmgr.GetAllWorkLogs()
            for key in all_logger:
                self.log_combobox.addItem(key)
            
            self.log_editbox.clear()
            for item in self.lmgr.GetWorkLogsById(work_logger):
                self.log_editbox.append(item)
        elif LogOpt_Add == log_opt:
            self.log_combobox.addItem(log_id)
            self.log_combobox.setCurrentText(log_id)

            self.log_editbox.append(log_content)
        elif LogOpt_Upt == log_opt:
            if log_id == self.log_combobox.currentText():
                self.log_editbox.append(log_content)
        elif LogOpt_Del == log_opt:
            if log_id == self.log_combobox.currentText():
                self.log_combobox.setCurrentText(work_logger)
                self.log_editbox.clear()
                for item in self.lmgr.GetWorkLogsById(work_logger):
                    self.log_editbox.append(item)
            self.log_combobox.removeItem(self.log_combobox.findText(log_id))
        elif LogOpt_Switch == log_opt:
            self.log_combobox.setCurrentText(log_id)
            
            self.log_editbox.clear()
            for item in self.lmgr.GetWorkLogsById(log_id):
                self.log_editbox.append(item)
    
    def slot_change_branches(self, branch):
        self.lmgr.change_select_branches(branch)
    
    def slot_click_choose_dir(self, el):
        print(el, os.getcwd())
        choose_dir = QFileDialog.getExistingDirectory(None, "选择文件夹", os.getcwd())
        if "" == choose_dir:
            return 

        el.setText(choose_dir)

    def slot_click_compile(self):
        self.lmgr.update_and_compile(self.cbBranches.currentText(), self.cbProjects.currentText())

    
    def slot_click_console_replacer(self):
        self.lmgr.start_console_replacer(self.cbBranches.currentText())

    def slot_click_ui_editor(self):
        if self.checkTruncEditor.isChecked():
            self.lmgr.start_ui_editor(trunc_name)
        else:
            self.lmgr.start_ui_editor(self.cbBranches.currentText())

    def slot_click_cancel_readonly(self):
        self.lmgr.cancel_readonly(self.cbBranches.currentText())

    def define_qq_btn(self):
        print("未完成")
