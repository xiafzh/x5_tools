#encoding:utf-8

import os
import subprocess
import shelve
import re
import time
from configparser import *
from src.logic.main_data import *
from conf.common import *
from PyQt5 import QtCore
from src.logger.logger import *
from src.logic.work_thread import *
from src.logic.thread.thread_create_proj import *
from src.logic.thread.thread_update import *

# 不耗时的逻辑处理、数据缓存
class CMainLogic:
    def __init__(self, ui):
        self.ui = ui
        self.work_logs = { work_logger : [],} 

        self.mutex = QtCore.QMutex()
        self.dir_mutex = QtCore.QMutex()
        self.logger = CLogger()
        self.logger.start()

        (dirp, filep) = os.path.split(common_db_path)
        if not os.path.exists(dirp):
            os.makedirs(dirp)
        
        (dirp, filep) = os.path.split(common_config_path)
        if not os.path.exists(dirp):
            os.makedirs(dirp)
        
        shelve_data = shelve.open(common_db_path, flag='c', protocol=2, writeback=True)
        # 初始化db
        if 'qq' not in shelve_data:
            shelve_data['qq'] = []
        if 'branch' not in shelve_data:
            shelve_data['branch'] = []

        # 初始化数据
        self.all_qqs = shelve_data['qq']
        self.all_braches = shelve_data['branch']
        if 'sel_branch' in shelve_data:
            self.sel_branch = shelve_data['sel_branch']
        else:
            self.sel_branch = ''
        shelve_data.close()

        configer = ConfigParser()
        configer.read(common_config_path)
        
        section = "common"
        option = "projpath"
        if configer.has_option(section, option):
           self.config_proj_path = configer.get(section, option)
           self.config_proj_path.replace("\\", "/")
           if self.config_proj_path[-1:] != "/":
               self.config_proj_path += "/"
        
        configer.clear()

        self.update_thread = CUpdateThreadLogic(self)

    def closeWindow(self):
        pass

    def saveShelveData(self, key, value):
        self.mutex.lock()
        shelve_data = shelve.open(common_db_path, flag='c', protocol=2, writeback=True)
        shelve_data[key] = value
        shelve_data.close()
        self.mutex.unlock()
    
    # 逻辑接口
    def startCompile(self):
        print("compile")
    
    def start_vs(self, path, solution, branch):
        try:
            target_path = self._transBranchToPath(branch) + "/src/" + path
            
            cur_path = os.getcwd()
            os.chdir(target_path)
            subprocess.Popen("start %s" % solution, shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            os.chdir(cur_path)
            self.logger.LogDebug(work_logger, "start vs ", path, solution)
        except Exception as err:
            self.logger.LogError(work_logger, "start server error:", err.__str__())


    def startLogin(self, qq, branch, is_debug, ip):
        try:
            cur_path = os.getcwd()
            target_path = self._transBranchToPath(branch) + "/exe"
            if is_debug:
                target_path += '/debug_bin'
            else:
                target_path += '/bin'
            if not self._checkTargetIp(ip, target_path):
                return
            os.chdir(target_path)
            subprocess.Popen(login_cmd_format % (qq, qq), shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            os.chdir(cur_path)
            self.logger.LogDebug(work_logger, "login ", qq)
            return qq
        except Exception as err:
            self.logger.LogError(work_logger, type(err), err.__str__())
            return err.__str__()
    
    def startServer(self, branch):
        try:
            target_path = self._transBranchToPath(branch) + "/exe"
            
            thread = CThreadStartServer(target_path + '/server', self)
            thread.start()
            thread.wait()
            self.logger.LogDebug(work_logger, "start server")
        except Exception as err:
            self.logger.LogError(work_logger, "start server error:", err.__str__())

    def saveLoginQQ(self, qq):
        if qq in self.all_qqs:
            return;

        self.all_qqs.append(qq)
        self.saveShelveData('qq', self.all_qqs)

    def RemoveLoginQQ(self, qq):
        if qq not in self.all_qqs:
            return

        self.all_qqs.remove(qq)
        self.saveShelveData('qq', self.all_qqs)

    # 数据接口    
    def getAllBranches(self):
        return self.all_braches

    def getAllProjects(self):
        return ('更新编译', '仅编译', '仅编译客户端', '仅编译服务器')

    def getAllLoginQQ(self):
        return self.all_qqs
    
    
    def UpdateProjPath(self, p4path, projpath, respath):
        (year, title) = self._transP4PathToBranchParam(p4path)

        for item in self.all_braches:
            if item.title == title:
                item.path = projpath
                self.saveShelveData('branch', self.all_braches)
                return False, ""

        branch_item = SBranchItem(p4path, projpath, p4path, '', '')
        (year, title) = self._transP4PathToBranchParam(p4path)
        if title == trunc_name:
            branch_item.svnpath = star_svn_path % trunc_name
            branch_item.video_svn_path = star_svn_path % video_trunc_name
        else:
            branch_item.svnpath = star_svn_path % branch_svn_subfix % (year, title)
            branch_item.video_svn_path = star_svn_path % video_branch_svn_subfix % (year, title)

        self.all_braches.append(branch_item)
        self.saveShelveData('branch', self.all_braches)

        return True, title
    
    def UpdateProjPath(self, p4path):
        #self.logger.WriteLogI(p4path)
        (year, title) = self._transP4PathToBranchParam(p4path)
        branch_item = SBranchItem(title, "", p4path, "", '')
        if title == trunc_name:
            branch_item.svnpath = star_svn_path % trunc_name
            branch_item.video_svn_path = star_svn_path % video_trunc_name
        else:
            branch_item.svnpath = star_svn_path % branch_svn_subfix % (year, title)
            branch_item.video_svn_path = star_svn_path % video_branch_svn_subfix % (year, title)

        branch_item.projpath = self.config_proj_path + p4path[28:]
        self.all_braches.append(branch_item)
        self.saveShelveData('branch', self.all_braches)
        
        return True, title

    def RemoveProjPath(self, branch):
        for index in range(0, len(self.all_braches)):
            if self.all_braches[index].title == branch:
                self.all_braches.remove(self.all_braches[index])
                self.saveShelveData('branch', self.all_braches)
                return True, index

        return False, -1

    def CreateNewProj(self, p4path, is_auto, proj_path = "", res_path = ""):
        print(p4path, is_auto, proj_path, res_path) 
        if '' == p4path:
            return False

        svn_path, video_svn_path = self._transP4PathToSvnPath(p4path)

        if not is_auto:
            if proj_path == "" or res_path == "" :
                return False
            proj_path = proj_path.rstrip("\\").rstrip("/")
            res_path = res_path.rstrip("\\").rstrip("/")

            # 判断路径是否存在
            if not os.path.exists(proj_path):
                os.makedirs(proj_path)
            
            if not os.path.exists(res_path):
                os.makedirs(res_path)

            #创建软链接
            os.symlink(res_path, "%s/%s" % (proj_path, "/exe/resources"))
        else:    
            projpath = self.config_proj_path + p4path[28:]
        
        self.update_thread.start_update_and_compile(CUpdateThreadLogic.EOT_Create
            , p4path, projpath, svn_path, video_svn_path)
        return True

    def CBCreateNewProj(self):
        print("over")
    
    def ThreadSafeChangeDir(self, pwd):
        self.dir_mutex.lock()
        #print("ThreadSafeChangeDir mutex lock")
        self.old_path = os.getcwd()
        os.chdir(pwd)
    
    def ThreadSafeChangeDirOver(self):
        os.chdir(self.old_path)
        self.dir_mutex.unlock()
        #print("ThreadSafeChangeDirOver mutex unlock")

    def appendLog(self, log_id, log_content):
        #print("UpdateCreateLog" + log_id)
        self.mutex.lock()
        #print("appendLog mutex lock")
        if log_id in self.work_logs:            
            self.work_logs[log_id].extend(log_content)
            log_len = len(self.work_logs[log_id])
            if log_len > 50:
                self.work_logs[log_id] = self.work_logs[log_id][log_len-50:]
                
            self.ui.RefreshWorkLogs(LogOpt_Upt, log_id, log_content)
            self.logger.LogInfo(log_id, log_content)
        else:
            self.work_logs.update({log_id:log_content})
            self.ui.RefreshWorkLogs(LogOpt_Add, log_id, log_content)
            self.logger.LogInfo(log_id, log_content, is_new = True)
        self.mutex.unlock()
        #print("appendLog mutex unlock")
    
    def deleteLog(self, log_id):
        #print("DelteCreateLog" + log_id)
        self.mutex.lock()        
        #print("deleteLog mutex lock")
        if log_id in self.work_logs:
            del self.work_logs[log_id]
        self.ui.RefreshWorkLogs(LogOpt_Del, log_id)
        self.mutex.unlock()        
        #print("deleteLog mutex unlock")
    
    def switchLog(self, log_id):
        self.mutex.lock()
        #print("switchLog mutex lock")
        if log_id in self.work_logs:
            self.ui.RefreshWorkLogs(LogOpt_Switch, log_id, self.work_logs[log_id])
        self.mutex.unlock()
        #print("switchLog mutex unlock")

    def GetAllWorkLogs(self):
        return self.work_logs
    
    def GetWorkLogsById(self, id):
        if id in self.work_logs:
            return self.work_logs[id]
        return None

    def change_select_branches(self, branch):
        self.saveShelveData("sel_branch", branch)

    def update_and_compile(self, branch, proj):
        branch_item = None
        for item in self.all_braches:
            if item.title == branch:
                branch_item = item
                break
        if None == branch_item:
            return False
        
        self.update_thread.start_update_and_compile(self.update_thread.EOT_Update
            , branch_item.p4path, branch_item.projpath)
   
    def start_console_replacer(self, branch):
        branch_item = self._find_branch_by_name(branch)
        cmd = "start %s/exe/debug_bin/ConsoleReplacer.exe" % branch_item.projpath
        subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE
            , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")


    def start_ui_editor(self, branch):
        branch_item = self._find_branch_by_name(branch)
        cmd = "start %s/exe/NewUIEditor/uieditor/界面编辑器.bat" % branch_item.projpath
        subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")

    # 分支换路径
    def _transBranchToPath(self, branch):
        choose_item = None
        for item in self.all_braches:
            if item.title == branch:
                choose_item = item
                break
        if not choose_item:
            return ""
        
        proj_path = choose_item.projpath
        return proj_path

    def _find_branch_by_name(self, branch):
        choose_item = None
        for item in self.all_braches:
            if item.title == branch:
                choose_item = item
                break
        return choose_item
        

    # check登录目标IP
    def _checkTargetIp(self, ip, path):
        config_file = path + "/config/user.ini"
        self.logger.WriteLogI(config_file)
        # 配置文件不存在
        if not os.path.exists(config_file):
            return False
        
        self.mutex.lock()
        try:
            configer = ConfigParser()
            configer.read(config_file)
            
            section = "Network"
            option = "hallserverip"
            if not configer.has_option(section, option):        
                return False

            config_ip = configer.get(section, option) 
            if ip == config_ip:
                return True
            
            configer.set(section, option, ip)     
            file_w = open(config_file, 'w', encoding='ansi')
            configer.write(file_w)
            file_w.close()
            # debug

            print(config_file+ time.strftime("%Y%m%d%H%M%S", time.localtime()))
            file_debug = open(config_file+ time.strftime("%Y%m%d%H%M%S", time.localtime()), 'w')
            configer.write(file_debug)
            file_debug.close()
            return True
        except Exception as err:
            print(err)
        finally:
            configer.clear()
            self.mutex.unlock()
        
    # p4path换分支名
    def _transP4PathToBranchParam(self, p4path):
        data_array = p4path.split("/")        
        branch_name = data_array[4]
        if (branch_name == trunc_name):
            return ("", trunc_name)
        else:
            year = data_array[4].split("_")[1]
            name_array = data_array[5].split("_")
            if re.match("[0-9]\.[0-9]\.[0-9]", name_array[2]):
                return(year, name_array[2])
            else:
                return (year, data_array[5][len(branch_p4_prefix):])
        #end _transP4PathToBranchParam
    
    # p4path换svn名
    def _transP4PathToSvnPath(self, p4path):
        year, branch_name = self._transP4PathToBranchParam(p4path)
        #print(year, branch_name)
        svn_path = ""
        video_svn_path = ""
        if branch_name == trunc_name:
            svn_path = star_svn_path % trunc_name
            video_svn_path = star_svn_path % video_trunc_name
        else:
            svn_path = star_svn_path % branch_svn_subfix % (year, branch_name)
            video_svn_path = star_svn_path % video_branch_svn_subfix % (year, branch_name)

        return svn_path, video_svn_path
 

    # 一些测试代码
    def test_thread(self):
        self.logger.LogDebug("compile", "ssss", "dddd")
        self.logger.LogRelease("compile", "ssss", "dddd")
        self.logger.LogError("compile", "ssss", "dddd")
        

    def testSlotStr(self, s, l):
        print(s, l)