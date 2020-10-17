#encoding:utf-8

import os
import subprocess
import copy
from PyQt5.QtCore import QThread,pyqtSignal
import xml.dom.minidom
from src.logic.tools.read_xml import *

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
        return "%s %d" % (self.id, self.entry)

class SSubProcessData:
    def __init__(self, id, subproc, desc):
        self.id = id
        self.subproc = subproc
        self.desc = desc
        self.log = ""

# 主要工作线程
class CThreadCreateProj(QThread):
    EOT_Create = 0
    EOT_Update = 1

    ##########
    ECT_P4Snc = 0
    ECT_SvnCOStar = 1
    ECT_Compile = 2
    ECT_SvnCOVideo = 3
    ECT_SvnUpdate = 4

    logAddSin = pyqtSignal(str, list)
    logDelSin = pyqtSignal(str)

    def __init__(self):
        super(CThreadCreateProj, self).__init__()
        self.subprocs = [] # SSubProcessData
        self.topo_data_copy = {}
        self.topo_data = {} # STopoData

        # 构造拓扑图
        conf_data = GetCommonXMLData("./config/common_config.xml", "CommonConfig/CreateTopos")
        self.init_topo_data(conf_data, self.EOT_Create);
        conf_data = GetCommonXMLData("./config/common_config.xml", "CommonConfig/UpdateTopos")
        self.init_topo_data(conf_data, self.EOT_Update)

    def stopRun(self):
        print("del")
        for item in self.subprocs:
            res = item.subproc.poll()
            if res == None:
                print(item.desc)
                item.subproc.kill()
    
    def __del__(self):
        self.wait()
    
    def init(self, type, p4path, svnpath, videosvnpath, projpath, respath, cbfun):
        # 构造数据
        print(p4path, svnpath, videosvnpath, projpath, respath, cbfun)
        self.p4path = p4path
        self.svnpath = svnpath
        self.videosvnpath = videosvnpath
        self.projpath = projpath
        self.respath = respath
        self.cbfun = cbfun
        
        self.topo_data = copy.deepcopy(self.topo_data_copy[type])

    def run(self):
        while (True):            
            print("++++++++++++++++++++++++++++++")
            # Check Finish
            self.__check_finished()
            print("finished check")

            # Check Run
            self.__check_running()
            print("running check")
            
            # 拓扑图为空，表示全部执行完成
            if len(self.topo_data) == 0:
                break
            #self.sleep(1)
            print("frame over")

        print("run finish")
        self.cbfun()

    def init_topo_data(self, conf_data, type):
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
        

    def __check_running(self):
        #print("begin check running")
        for key in self.topo_data:
            topo = self.topo_data[key]
            if 0 == topo.entry and topo.state == STopoData.S_IDLE:
                exe_cmd = self.__GetExecuteCMD(topo.type, topo.cmd)
                print(topo.type, exe_cmd)
                sp = subprocess.Popen(exe_cmd, shell=True, stdout = subprocess.PIPE
                    , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")

                topo.state = STopoData.S_RUNNING

                sp_data = SSubProcessData(topo.id, sp, topo.desc)
                self.subprocs.append(sp_data)
        
        #print("end check runnin %d" % len(self.subprocs))

    def __check_finished(self):
        #print("begin check finished")
        over_sp = []
        for sp in self.subprocs:
            if sp.subproc.stdout.readable():
                #log_context = sp.subproc.stdout.readlines(4096)
                log_context = sp.subproc.stdout.read(4096)
                self.logAddSin.emit(sp.desc, [log_context,])
            res = sp.subproc.poll()
            if res != None:
                over_sp.append(sp)
                self.logDelSin.emit(sp.desc)
                print("finish", sp.desc)
            
            
        print("----start delete")
        for sp in over_sp:
            for key in self.topo_data:
                topo = self.topo_data[key]
                if topo.id == sp.id:
                    for del_id in topo.next:
                        self.topo_data[del_id].entry -= 1 
                    
                    del self.topo_data[key]
                    break
        
            self.subprocs.remove(sp)
        
        #print("end check finished %d" % len(self.topo_data))

    def __GetExecuteCMD(self, type, cmd):
        type_value = int(type)
        if type_value == self.ECT_P4Snc:
            return cmd % self.projpath
        elif type_value == self.ECT_SvnCOStar:
            return cmd % ('zhangxiafei', 'rni7ik', self.svnpath, self.projpath)
        elif type_value == self.ECT_SvnCOVideo:
            return cmd % ('zhangxiafei', 'rni7ik', self.videosvnpath, self.projpath)
        elif type_value == self.ECT_Compile:
            return cmd % self.projpath
        elif type_value == self.ECT_SvnUpdate:
            return cmd % self.projpath
        return cmd


class CThreadTest(QThread):
    testSin = pyqtSignal(str, list)
    def __init__(self):
        super(CThreadTest, self).__init__()

    def run(self):
        i = 0
        l = []
        while i  < 3:
            l.append(i)
            self.testSin.emit("%d" % i, l)
            i += 1  

