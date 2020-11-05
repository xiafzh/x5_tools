#encoding:utf-8

import os
import subprocess
import copy
import time
from PyQt5.QtCore import QThread,pyqtSignal
import xml.dom.minidom
from src.logic.tools.read_xml import *
from x51_tools import X51Compiler
from conf.common import *

class STopoData:
    S_IDLE = 0
    S_RUNNING = 1
    S_OVER = 2

    def __init__(self, id, type, cmd, desc):
        self.id = id
        self.type = type
        self.cmd = cmd
        self.desc = desc
        self.next = []
        self.entry = 0
        self.state = self.S_IDLE
    
    def __str__(self):
        return "%s %d %s %s" % (self.id, self.entry, self.desc, self.cmd)

class CUpdateThreadLogic:
    EOT_Create = 0
    EOT_Update = 1

    ECT_P4Snc = 0
    ECT_SvnCOStar = 1
    ECT_Compile = 2
    ECT_SvnCOVideo = 3
    ECT_SvnUpdate = 4

    def __init__(self, mgr):
        self.lmgr = mgr
        self.topo_data_copy = {}
        self.topo_data = {} # STopoData
        self.update_thread = {}
        self.is_running = False

        # 构造拓扑图
        conf_data = GetCommonXMLData("./config/common_config.xml", "CommonConfig/CreateTopos")
        self.init_topo_data(conf_data, self.EOT_Create);
        conf_data = GetCommonXMLData("./config/common_config.xml", "CommonConfig/UpdateTopos")
        self.init_topo_data(conf_data, self.EOT_Update)

    def init_topo_data(self, conf_data, type):
        if conf_data == None:
            return
        self.topo_data_copy[type] = {}
        topo_items = conf_data.getElementsByTagName("TopoItem")
        for item in topo_items:
            new_id = item.getAttribute("id")
            new_data = STopoData(new_id, item.getAttribute("type")
                , item.getAttribute("cmd"), item.getAttribute("desc"))
            for ni in item.getElementsByTagName("NextItem"):
                id_str = ni.getAttribute("id")
                new_data.next.append(id_str)
                self.topo_data_copy[type][id_str].entry += 1
            self.topo_data_copy[type].update({new_id : new_data})
        
    def start_update_and_compile(self, type, p4path, projpath, svnpath = "", videosvnpath = ""):
        if self.is_running:
            return False
        self.is_running = True
        self.p4path = p4path
        self.projpath = projpath
        self.svnpath = svnpath
        self.videosvnpath = videosvnpath

        self.topo_data = copy.deepcopy(self.topo_data_copy[type])
        self.check_update_running()
        return True

    def check_update_running(self):
        try:
            for key in self.topo_data:
                topo = self.topo_data[key]
                if 0 == topo.entry and topo.state == STopoData.S_IDLE:
                    exe_cmd = self.__GetExecuteCMD(topo.type, topo.cmd)

                    topo.state = STopoData.S_RUNNING
                    self.lmgr.ThreadSafeChangeDir(os.getcwd() + "/scripts")
                    self.update_thread[topo.id] = CThreadCreateProj(topo.id, topo.desc, topo.cmd, exe_cmd)
                    self.lmgr.ThreadSafeChangeDirOver()
                    
                    self.update_thread[topo.id].finishSin.connect(self.on_create_thread_finish)
                    self.update_thread[topo.id].logAddSin.connect(self.on_create_thread_running)
                    self.update_thread[topo.id].start()
                    self.lmgr.appendLog(work_logger, "begin %s %s %s" % (topo.desc, topo.cmd, exe_cmd))
        except Exception as err:
            self.lmgr.appendLog(work_logger, err.__str__())

    def on_create_thread_finish(self, id, res):
        try:
            if id not in self.update_thread:
                print("no ", id)
                return
            
            self.update_thread[id].exit(0)
            del self.update_thread[id]

            for key in self.topo_data:
                topo = self.topo_data[key]
                if topo.id == id:
                    for del_id in topo.next:
                        self.topo_data[del_id].entry -= 1 
                    del self.topo_data[key]
                    break
            
            self.check_update_running()

            if len(self.update_thread) == 0:
                self.is_running = False
                print(self.is_running)
                self.lmgr.UpdateProjPath(self.p4path, self.projpath)
        except Exception as err:
            self.lmgr.appendLog(work_logger, "on_create_thread_finish %s" % err.__str__())
    
    def on_create_thread_running(self, id, log):
        self.lmgr.appendLog(id, log)
       
    def __GetExecuteCMD(self, type, cmd):
        type_value = int(type)
        if type_value == self.ECT_P4Snc:
            return self.p4path
        elif type_value == self.ECT_SvnCOStar:
            return "%s %s %s %s" % (self.projpath, self.lmgr.svn_username, self.lmgr.svn_password, self.svnpath)
        elif type_value == self.ECT_SvnCOVideo:
            return "%s %s %s %s" % (self.projpath, self.lmgr.svn_username, self.lmgr.svn_password, self.videosvnpath)
        elif type_value == self.ECT_Compile:
            return self.projpath
        elif type_value == self.ECT_SvnUpdate:
            return self.projpath
        return cmd


# 主要工作线程
class CThreadCreateProj(QThread):

    logAddSin = pyqtSignal(str, str)
    finishSin = pyqtSignal(str, int)

    def __init__(self, id, desc, bat, cmd):
        super(CThreadCreateProj, self).__init__()
        self.id = id
        self.desc = desc
        self.cmd = cmd
        print("start running", self.id, bat, self.cmd, os.getcwd())
        self.proc = X51Compiler()
        proc_id = self.proc.ExecuteFile(bat, cmd, os.getcwd())
        
    def stopRun(self):
        print("del")

    def run(self):
        res = None
        while (True):
            is_finish = self.proc.Finished()
            
            while True:
                out_str = self.proc.GetOutputString()
                if "" == out_str:
                    break
                self.logAddSin.emit(self.desc, out_str)
            
            if is_finish:
                break
        
        print("run finish", self.id, self.cmd, res)
        self.finishSin.emit(self.id, res)

 
