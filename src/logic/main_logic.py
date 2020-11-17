#encoding:utf-8

import os
import subprocess
import shelve
import re
import time
import stat
import socket
from configparser import *
from src.logic.main_data import *
from conf.common import *
from PyQt5 import QtCore
from src.logger.logger import *
from src.logic.work_thread import *
from src.logic.thread.thread_create_proj import *
from src.logic.thread.thread_update import *
from x51_tools import X51Compiler
from src.logic.tools.date_time import *

# 不耗时的逻辑处理、数据缓存
class CMainLogic:
    def __init__(self, ui):
        self.ui = ui
        self.main_path = os.getcwd()
        self.work_logs = { work_logger : [],} 

        self.mutex = QtCore.QMutex()
        self.dir_mutex = QtCore.QMutex()
        self.log_mutex = QtCore.QMutex()
        self.logger = CLogger()
        self.logger.start()

        (dirp, filep) = os.path.split(common_db_path)
        if not os.path.exists(dirp):
            os.makedirs(dirp)
        
        (dirp, filep) = os.path.split(common_config_path)
        if not os.path.exists(dirp):
            os.makedirs(dirp)

        self.init_shelve_data()
        self.read_common_config()
        self.init_workspace()

        self.start_server_thread = CThreadStartServer(self)

        self.update_thread = CUpdateThreadLogic(self)
        #self.update_thread.msgboxSin.connect(self.ui.slot_show_message_box)

        # 常规工作进程-主要处理Update(time)
        self.work_thread = CWorkThread(self)
        self.work_thread.workStart.connect(self.WorkStart)
        self.work_thread.start()

    def closeWindow(self):
        pass

    def init_shelve_data(self):        
        shelve_data = shelve.open(common_db_path, flag='c', protocol=2, writeback=True)
        # 初始化db
        if 'qq' not in shelve_data:
            shelve_data['qq'] = []
        if 'branch' not in shelve_data:
            shelve_data['branch'] = []
        if 'config' not in shelve_data:
            shelve_data['config'] = {}

        # 初始化数据
        self.all_qqs = shelve_data['qq']
        self.save_config = shelve_data['config']
        self.all_braches = shelve_data['branch']
        if 'sel_branch' in shelve_data:
            self.sel_branch = shelve_data['sel_branch']
        else:
            self.sel_branch = ''

        shelve_data.close()

    def read_common_config(self):
        configer = ConfigParser()
        configer.read(common_config_path)
        
        section = "common"
        option = "projpath"
        if configer.has_option(section, option):
           self.config_proj_path = configer.get(section, option)
           self.config_proj_path.replace("\\", "/")
           if self.config_proj_path[-1:] != "/":
               self.config_proj_path += "/"
        
        option = "log_level"
        if configer.has_option(section, option):
            self.log_level = configer.get(section, option)
        
        section = "svn"
        option = "username"
        if configer.has_option(section, option):
            self.svn_username = configer.get(section, option)
        
        option = "password"
        if configer.has_option(section, option):
            self.svn_password = configer.get(section, option)

        section = "p4"
        option = "username"
        if configer.has_option(section, option):
            self.p4_username = configer.get(section, option)
        
        option = "password"
        if configer.has_option(section, option):
            self.p4_password = configer.get(section, option)

        option = "host"
        if configer.has_option(section, option):
            self.p4_host = configer.get(section, option)

        configer.clear()

    def init_workspace(self):
        try:
            self.ThreadSafeChangeDir("./scripts")
            cpobj = X51Compiler()
            print(self.p4_username, self.p4_password, self.p4_host)
            cpobj.ExecuteFile("p4_common_clients.bat", "{0} {1} {2}".format(self.p4_username, self.p4_password, self.p4_host), os.getcwd())
            workspace_list = []
            while True:
                is_finish = cpobj.Finished()
                        
                while True:
                    out_str = cpobj.GetOutputString()
                    if "" == out_str:
                        break
                    
                    data_arr = out_str.split(" ")
                    if len(data_arr) < 2 or data_arr[0] != "Client":
                        continue
                    
                    workspace_list.append(data_arr[1])
                    
                if is_finish:
                    break
            print(workspace_list)
            host_name = socket.gethostname()
            print(host_name)
            
            self.workspaces = []
            for key in workspace_list:
                print("{0} {1}".format(key, os.getcwd()))
                cpobj.ExecuteFile("p4_common_workspace.bat", '{0} {1} {2} {3}'.format(key, self.p4_username, self.p4_password, self.p4_host), os.getcwd())
                while True:
                    is_finish = cpobj.Finished()
                    
                    while True:
                        out_str = cpobj.GetOutputString()
                        if "" == out_str:
                            break
                        
                        if out_str.startswith("Host"):
                            data_arr = out_str.split("\t")
                            if len(data_arr) >= 2 and data_arr[1] == host_name:
                                self.workspaces.append(key)
                        
                    if is_finish:
                        break
            print(self.workspaces)
            # end for
        finally:
            self.ThreadSafeChangeDirOver()
        

    def saveShelveData(self, key, value):
        try:
            shelve_data = shelve.open(common_db_path, flag='c', protocol=2, writeback=True)
            shelve_data[key] = value
            shelve_data.close()
        except Exception as err:
            self.appendLog(work_logger, err.__str__())
    
    def getShelveConfigData(self, key):
        if key not in self.save_config:
            return None
        
        return self.save_config[key]
    
    def setShelveConfigData(self, key, value):
        print(key, value, self.save_config)
        self.save_config[key] = value
        self.saveShelveData('config', self.save_config)    

    # 逻辑接口    
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
            res, res_str = self._checkTargetIp(ip, target_path)
            if not res:
                self.appendLog(work_logger, "start_login %s" % res_str)
                return
            os.chdir(target_path)
            subprocess.Popen(login_cmd_format % (qq, qq), shell=True, stdout = subprocess.PIPE
                , stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding="gb18030")
            os.chdir(cur_path)
            self.logger.LogDebug(work_logger, "login ", qq)
            return qq
        except Exception as err:
            self.appendLog(work_logger, err.__str__())
            return err.__str__()
    
    def startServer(self, branch, ip):
        try:
            target_path = self._transBranchToPath(branch) + "/exe"
            self.start_server_thread.Start(target_path + '/server', ip)
            
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
        return ('更新编译', '仅编译')

    def getAllLoginQQ(self):
        return self.all_qqs
    
    def UpdateProjPath(self, p4path, workspace, projpath = ""):
        try:
            p4path = p4path.rstrip("/").rstrip("\\")
            projpath = projpath.rstrip("/").rstrip("\\")
            (year, title) = self._transP4PathToBranchParam(p4path)
            print(year, title, p4path)
            if "" == projpath:
                projpath = self.config_proj_path + p4path[28:]

            for item in self.all_braches:
                if item.title == title:
                    item.p4path = p4path
                    item.projpath = projpath
                    item.workspace = workspace
                    self.saveShelveData('branch', self.all_braches)
                    return False, ""

            branch_item = SBranchItem(title, projpath, p4path, workspace)
    
            self.all_braches.append(branch_item)
            self.saveShelveData('branch', self.all_braches)

            self.appendLog(work_logger, "append_branch %s %s" % (title, branch_item.projpath))
            return True, title
        except Exception as err:
            self.appendLog(work_logger, "UpdateProjPath %s" % err.__str__())
        
        return False, ""
       
    
    def RemoveProjPath(self, branch):
        for index in range(0, len(self.all_braches)):
            print(self.all_braches[index].title)
            if self.all_braches[index].title == branch:
                self.all_braches.remove(self.all_braches[index])
                self.saveShelveData('branch', self.all_braches)
                return True, index

        return False, -1

    def CreateNewProj(self, p4path, workspace, proj_path = "", res_path = "", star_svn = "", video_svn = ""):
        print(p4path, proj_path, res_path, star_svn, video_svn) 
        if '' == p4path:
            return False
        p4path = p4path.rstrip("\\").rstrip("/")
        proj_path = proj_path.rstrip("\\").rstrip("/")
        res_path = res_path.rstrip("\\").rstrip("/")

        if "" == proj_path:            
            proj_path = self.config_proj_path + p4path[28:]

        if "" != res_path:           
            # 判断路径是否存在
            if not os.path.exists(proj_path):
                os.makedirs(proj_path)
            
            if not os.path.exists(res_path):
                os.makedirs(res_path)

            #创建软链接
            os.symlink(res_path, "%s/%s" % (proj_path, "/exe/resources"))
        
        svn_path, video_svn_path = self._transP4PathToSvnPath(p4path)
        if "" != star_svn:
            svn_path = star_svn
        if "" != video_svn:
            video_svn_path = video_svn

        self.update_thread.start_update_and_compile(self.update_thread.EOT_Create
            , p4path, proj_path, workspace, svn_path, video_svn_path)
        return True

    def CBCreateNewProj(self):
        print("over")
    
    def ThreadSafeChangeDir(self, pwd):
        #self.dir_mutex.lock()
        #print("ThreadSafeChangeDir mutex lock")
        self.old_path = os.getcwd()
        os.chdir(pwd)
    
    def ThreadSafeChangeDirOver(self):
        os.chdir(self.old_path)
        #self.dir_mutex.unlock()
        #print("ThreadSafeChangeDirOver mutex unlock")

    def appendLog(self, log_id, log_content):
        #print("UpdateCreateLog" + log_id)
        #print("appendLog mutex lock")
        if log_id in self.work_logs:            
            self.work_logs[log_id].append(log_content)
            log_len = len(self.work_logs[log_id])
            if log_len > 100:
                self.work_logs[log_id] = self.work_logs[log_id][log_len-80:]
                
            self.ui.RefreshWorkLogs(LogOpt_Upt, log_id, log_content)
            self.logger.LogInfo(log_id, log_content)
        else:
            self.work_logs.update({log_id:[]})
            self.work_logs[log_id].append(log_content)
            self.ui.RefreshWorkLogs(LogOpt_Add, log_id, log_content)
            self.logger.LogInfo(log_id, log_content, is_new = True)
        #print("appendLog mutex unlock")
    
    def deleteLog(self, log_id):
        #print("DelteCreateLog" + log_id)
        #print("deleteLog mutex lock")
        if log_id in self.work_logs:
            del self.work_logs[log_id]
        self.ui.RefreshWorkLogs(LogOpt_Del, log_id)
        #print("deleteLog mutex unlock")
    
    def switchLog(self, log_id):
        #print("switchLog mutex lock")
        if log_id in self.work_logs:
            self.ui.RefreshWorkLogs(LogOpt_Switch, log_id, ""
            #self.work_logs[log_id]
            )
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
        
        if not hasattr(branch_item, "workspace"):
            branch_item.workspace = self.ui.CBWorkSpace.currentText()
        
        compile_type = self.update_thread.EOT_Update
        if proj == "仅编译":
            compile_type = self.update_thread.EOT_Compile

        self.update_thread.start_update_and_compile(compile_type
            , branch_item.p4path, branch_item.projpath, branch_item.workspace)
   
    def start_console_replacer(self, branch):
        branch_item = self._find_branch_by_name(branch)
        self._ExecuteCMD("%s/exe/debug_bin/" % branch_item.projpath, "start ConsoleReplacer.exe")

    def start_ui_editor(self, branch):
        branch_item = self._find_branch_by_name(branch)
        
        os.system(r"attrib -r %s/exe/NewUIEditor/resources/editor/domain/layout/Layout_Config.local.xml" % branch_item.projpath)
        
        cmd = "start /b editor.exe Layout"
        self._ExecuteCMD("%s/exe/NewUIEditor/editor" % branch_item.projpath, cmd)
        

    def cancel_readonly(self, branch):
        branch_item = self._find_branch_by_name(branch)
        if None == branch_item:
            return False
        try:
            print("begin cancel", branch_item.projpath)
            os.system(r"attrib -r %s/exe/bin/* /S /D" % branch_item.projpath)
            os.system(r"attrib -r %s/exe/debug_bin/* /S /D" % branch_item.projpath)
            os.system(r"attrib -r %s/exe/server/* /S /D" % branch_item.projpath)
            os.system(r"attrib -r %s/exe/VideoAdminClient/* /S /D" % branch_item.projpath)
            print("end cancel", branch_item.projpath)
        except Exception as e:
            print(e)
        finally:
            return True

    def setTimingCompile(self, is_open):
        self.setShelveConfigData("timing_compile", True)
        if is_open:
            self.work_thread.AppendWork(WT_COMPILE, CWorkThread.ET_Daily, {}, 10800)
        else:
            self.work_thread.DeleteWork(WT_COMPILE)


    def WorkStart(self, type, params):
        self.logger.LogDebug(work_logger, "start work ", type, " param", params)
        try:
            if WT_COMPILE == type:
                self.update_and_compile(self.ui.cbBranches.currentText(), self.ui.cbProjects.currentText())
        except Exception as err:
            self.logger.LogError("work start", err.__str__())

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
        client_config_file = path + "/config/client_config.ini"
        # 配置文件不存在
        if not os.path.exists(config_file) or not os.path.exists(client_config_file):
            return False, "path err %s" % path
        
        try:
            configer = ConfigParser()
            configer.read(config_file)
            
            section = "Network"
            option = "hallserverip"
            if not configer.has_option(section, option):        
                return False, "no ip config"

            config_ip = configer.get(section, option) 
            if ip == config_ip:
                return True, ""
            
            # 取消只读
            os.chmod(config_file, stat.S_IWRITE)
            os.chmod(client_config_file, stat.S_IWRITE)

            configer.set(section, option, ip)     
            file_w = open(config_file, 'w', encoding='ansi')
            configer.write(file_w)
            file_w.close()
            return True, ""
        except Exception as err:
            return False, err.__str__()
        finally:
            configer.clear()
        
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
 
    def _ExecuteCMD(self, path, cmd):
        exe_cmder = X51Compiler()
        exe_cmder.ExecuteCommand(cmd, path)
        while True:
            is_finish = exe_cmder.Finished()
            while True:
                out_str = exe_cmder.GetOutputString()
                if "" == out_str:
                    break
            if is_finish:
                break
        return True

    # 一些测试代码
    def test_thread(self):
        self.logger.LogDebug("compile", "ssss", "dddd")
        self.logger.LogRelease("compile", "ssss", "dddd")
        self.logger.LogError("compile", "ssss", "dddd")
        
    def test_fun(self):
        print(GetNetTime())


    def testSlotStr(self, s, l):
        print(s, l)