#encoding:utf-8

import os
import stat
import subprocess
from PyQt5.QtCore import QThread
from src.logic.tools.read_xml import *

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
    def __init__(self, pwd, mgr, ip):
        super(CThreadStartServer, self).__init__()
        self.pwd = pwd
        self.data_mgr = mgr
        self.ip = ip
    
    def __del__(self):
        self.wait()

    def change_macros_ip(self):
        macros_file = self.pwd + "/config/macros.xml"
        if not os.path.exists(macros_file):
            return False
        
        os.chmod(macros_file, stat.S_IWRITE)

        f_r = open(macros_file, "r")
        all_str = f_r.read()
        f_r.close()

        all_str = all_str.replace("127.0.0.1", self.ip)
        f_w = open(macros_file, "w")
        f_w.write(all_str)
        f_w.close()

    def get_app_box_list(self):
        return GetServerAppBoxList(self.pwd+"/config/macros.xml", self.pwd+"/config/admin_proxy.xml")        

    def run(self):
        port_list = self.get_app_box_list()
        if None == port_list or len(port_list) == 0:
            return

        try:
            self.data_mgr.ThreadSafeChangeDir(self.pwd)

            self.change_macros_ip()            
            for item in port_list:
                subprocess.Popen('start app_box_d -port %s' % item, shell=True, stdout = subprocess.PIPE
                    , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            self.data_mgr.ThreadSafeChangeDirOver()
            #休眠5秒
            self.sleep(5)
            self.data_mgr.ThreadSafeChangeDir(self.pwd)
            subprocess.Popen('start admin_proxy_d ::-autostartall', shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            if os.path.exists("admin_client_new.exe"):
                subprocess.Popen('start admin_client_new', shell=True, stdout = subprocess.PIPE
                    , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            else:
                subprocess.Popen('start admin_client', shell=True, stdout = subprocess.PIPE
                    , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
        except Exception as err:
            self.data_mgr.logger.LogError("start server", err.__str__())
        finally:
            self.data_mgr.ThreadSafeChangeDirOver()
        

