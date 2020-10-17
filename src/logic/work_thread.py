#encoding:utf-8

import os
import subprocess
from PyQt5.QtCore import QThread

# 主要工作线程
class CWorkThread(QThread):
    def __init__(self, data_mgr):
        super(CWorkThread, self).__init__()
        self.data_mgr = data_mgr


    def run(self):
        while True:
            #print("main_work_thread run")
            self.sleep(1)

class CThreadStartServer(QThread):
    def __init__(self, pwd, mgr):
        super(CThreadStartServer, self).__init__()
        self.pwd = pwd
        self.data_mgr = mgr
    
    def __del__(self):
        self.wait()

    def run(self):
        try:
            self.data_mgr.ThreadSafeChangeDir(self.pwd)
            # 通过admin_proxy获取
            subprocess.Popen('start app_box_d', shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            subprocess.Popen('start app_box_d -port 27153', shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            subprocess.Popen('start app_box_d -port 27154', shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            self.data_mgr.ThreadSafeChangeDirOver()  
            #休眠5秒
            self.sleep(5)
            self.data_mgr.ThreadSafeChangeDir(self.pwd)
            subprocess.Popen('start admin_proxy_d ::-autostartall', shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            subprocess.Popen('start admin_client_new', shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            self.data_mgr.ThreadSafeChangeDirOver()
        except Exception as err:
            self.data_mgr.logger.LogError("start server", err.__str__())

