#encoding:utf-8

import os
import stat
import subprocess
import datetime
import psutil
from PyQt5.QtCore import QThread
from src.logic.tools.read_xml import *
from src.logic.tools.date_time import *

# 主要工作线程
class CWorkThread(QThread):
    # 更新时间
    UPDATE_INTERVAL_MIN = 60

    def __init__(self, data_mgr):
        super(CWorkThread, self).__init__()
        self.data_mgr = data_mgr
        self.remote_datetime = GetNetTime()
        self.last_check_datetime_sec = datetime.datetime.now()
        self.last_check_datatime_min = datetime.datetime.now()

    # 增加工作
    def AppendWork(type):
        print("add work %d" % type)

    def DeleteWork(type):
        print(1)

    def run(self):
        while True:
            now_date_time = datetime.datetime.now()
            
            # 每秒处理的事件

            self.last_check_datetime_sec = now_date_time

            if (now_date_time - self.last_check_datatime_min).seconds >= self.UPDATE_INTERVAL_MIN:
                # 每分钟处理的事件

                now_net_time = GetNetTime()
                # 跨天处理的事件
                if now_net_time.date() != self.remote_datetime.date():
                    print("an other day")

                self.remote_datetime = now_net_time
                self.last_check_datatime_min = now_date_time
            self.sleep(1)

# 启动服务器的线程
class CThreadStartServer(QThread):
    FIRST_PROCESSES = ("app_box", "app_box.exe", "app_box_d", "app_box_d.exe"
        , "admin_proxy", "admin_proxy.exe", "admin_proxy_d", "admin_proxy_d.exe"
        , "admin_client", "admin_client.exe", "admin_client_d", "admin_client_d.exe"
        , "admin_client_new", "admin_client_new.exe", "admin_client_new_d", "admin_client_new_d.exe")
    SECOND_PROCESSES = ("service_box", "service_box.exe", "service_box_d", "service_box_d.exe")


    def __init__(self, mgr):
        super(CThreadStartServer, self).__init__()
        self.data_mgr = mgr

        self.ip = ''
        self.pwd = ''
        self.is_running = False

    def __del__(self):
        self.wait()

    def Start(self, pwd, ip):
        if self.is_running:
            return False

        self.ip = ip
        self.pwd = pwd
        self.is_running = True
        
        self.start()
        return True

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

    def get_stop_process_list(self, path):
        print(None)
        res = [[], []]
        psids = psutil.pids()
        print(psids)
        for item in psids:
            try:
                pinfo = psutil.Process(item)
                #print(item, pinfo.name())
                if pinfo.name() in self.FIRST_PROCESSES:
                    res[0].append(item)
                elif pinfo.name() in self.SECOND_PROCESSES:
                    res[1].append(item)
            except Exception as err:
                print(item, "error:", err.__str__())
        return res

    def run(self):
        try:
            port_list = self.get_app_box_list()
            if None == port_list or len(port_list) == 0:
                return

            stop_plist = self.get_stop_process_list(self.pwd)
            print(stop_plist)
            for plist in stop_plist:
                for pid in plist:
                    os.popen("taskkill /F /pid %d" % pid)
                        
            
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
            print(err.__str__())
            self.data_mgr.logger.LogError("start server", err.__str__())
        finally:
            self.data_mgr.ThreadSafeChangeDirOver()
            self.isRunning = False
        

