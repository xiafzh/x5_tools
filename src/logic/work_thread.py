#encoding:utf-8

import os
import stat
import subprocess
import datetime
import time
import psutil
from PyQt5.QtCore import QThread, pyqtSignal
from src.logic.tools.read_xml import *
from src.logic.tools.date_time import *
from src.logic.main_data import *

# 主要工作线程
class CWorkThread(QThread):
    # 更新时间
    UPDATE_INTERVAL_MIN = 60

    # 执行类型
    ET_Frame = 0 #每帧
    ET_Second = 1 # 每秒
    ET_Minute = 2 # 每分钟
    ET_Hour = 3 # 每小时
    ET_Daily = 4 # 每天
    ET_Weekly = 5 # 每周


    workStart = pyqtSignal(int, dict)

    def __init__(self, data_mgr):
        super(CWorkThread, self).__init__()
        self.data_mgr = data_mgr
        self.local_datetime = time.time()
        self.remote_datetime = GetNetTimeMS()

        print("local_time:", self.local_datetime, ", remote_time:", self.remote_datetime)
        self.last_check_datetime_sec = self.local_datetime
        self.last_check_datatime_min = 0

        self.work_map = {}
        self.exe_map = {}
        self.exe_map[self.ET_Frame] = []
        self.exe_map[self.ET_Second] = []
        self.exe_map[self.ET_Minute] = []
        self.exe_map[self.ET_Hour] = []
        self.exe_map[self.ET_Daily] = []
        self.exe_map[self.ET_Weekly] = []

        self.delete_work = []

    # 增加工作
    def AppendWork(self, type, exe_type, params, interval = 0):
        print("add work %d" % type)
        if exe_type not in self.exe_map:
            return False

        if type in self.work_map:
            pass
        else:
            new_work = STimerInfo()
            new_work.work_type = type
            new_work.exe_type = exe_type
            new_work.params = params
            new_work.start_interval = interval
            self.work_map[type] = new_work
            
            self.exe_map[exe_type].append(type)

        return True

    def DeleteWork(self, type):
        self.delete_work.append(type)

    def ResetDaily(self):
        for key in self.exe_map[self.ET_Daily]:
            if key not in self.work_map:
                self.DeleteWork(key)
                continue

            self.work_map[key].has_executed = False
            print("reset work exe state daily ", key)

    def run(self):
        while True:
            now_date_time = time.time()
            delta_time = now_date_time - self.local_datetime
            
            # 每秒处理的事件

            self.last_check_datetime_sec = now_date_time

            if abs(now_date_time - self.last_check_datatime_min) >= self.UPDATE_INTERVAL_MIN:
                # 每分钟处理的事件


                # 跨天处理的事件
                now_remote_date_time = GetNetTimeMS()
                if not IsSameDay_TS(now_remote_date_time, self.remote_datetime):
                    # 跨天，重置一下每日执行
                    self.ResetDaily()
                    
                self.remote_datetime = now_remote_date_time

                # 计算当前距离每天起始时间的间隔
                daily_interval = (now_remote_date_time + 28800) % 86400
                print("start", len(self.exe_map[self.ET_Daily]), daily_interval)
                for key in self.exe_map[self.ET_Daily]:
                    if key not in self.work_map:
                        self.DeleteWork(key)
                        print("not in work map", key)
                        continue

                    if (self.work_map[key].has_executed):
                        continue
                    
                    print("check work", key, ", start:", self.work_map[key].start_interval)
                    if daily_interval >= self.work_map[key].start_interval:
                        self.work_map[key].has_executed = True
                        self.workStart.emit(self.work_map[key].work_type, self.work_map[key].params)

                    #print(self.work_map[key])
                self.last_check_datatime_min = now_date_time
            
            self.local_datetime = now_date_time


# 启动服务器的线程
class CThreadStartServer(QThread):
    FIRST_PROCESSES = ("app_box", "app_box.exe", "app_box_d", "app_box_d.exe"
        , "admin_proxy", "admin_proxy.exe", "admin_proxy_d", "admin_proxy_d.exe"
        , "admin_client", "admin_client.exe", "admin_client_d", "admin_client_d.exe"
        , "admin_client_new", "admin_client_new.exe", "admin_client_new_d", "admin_client_new_d.exe"
        , "launch_dx_d.exe", "launch_dx_d", "launch_dx.exe", "launch_dx")
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
            #print("start thread is running")
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
        #print(None)
        res = [[], []]
        psids = psutil.pids()
        #print(psids)
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
            #print(stop_plist)
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
            self.is_running = False
            #print("start server over")
        

