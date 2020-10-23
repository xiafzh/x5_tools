#encoding:utf-8

import os
import time
from PyQt5.QtCore import QThread
from conf.common import*


class SLogTypeData:
    def __init__(self, log_file):
        self.file_name = log_file
        self.file_writer = None

class SLogBufferData:
    def __init__(self, log_id, log_lv, content, is_new = False):
        self.log_id = log_id
        self.log_lv = log_lv
        self.is_new = is_new
        self.content = content

class CLogger(QThread):
    LogLv_Debug = 0
    LogLv_Info = 1
    LogLv_Error = 2

    # TODO::先这么搞一下，之后改成配置
    LogLv_Config_LV = 0

    def __init__(self):
        super(CLogger, self).__init__()

        self.log_buffer = [[], []]
        self.write_index = 0
        
        self.all_logger = {}
        self.log_path = os.getcwd() + logs_path
        print(self.log_path)
    
    def WriteLogI(self, *arg):
        #f_w = open(self.file_path, "a")
        #f_w.write(arg.__str__() + "\n")
        #f_w.close()
        pass

    def LogDebug(self, log_id, *args, **kwargs):
        is_new = False
        if "is_new" in kwargs:
            is_new = kwargs["is_new"]
        content_str = ""
        for item in args:
            content_str += item.__str__()
        self.WriteLog(log_id, self.LogLv_Debug, content_str, is_new)
    
    def LogInfo(self, log_id, *args, **kwargs):
        is_new = False
        if "is_new" in kwargs:
            is_new = kwargs["is_new"]
        content_str = ""
        for item in args:
            content_str += item.__str__()
        self.WriteLog(log_id, self.LogLv_Info, content_str, is_new)
        
    def LogError(self, log_id, *args, **kwargs):
        print(args)
        is_new = False
        if "is_new" in kwargs:
            is_new = kwargs["is_new"]
        content_str = ""
        for item in args:
            content_str += item.__str__()
        self.WriteLog(log_id, self.LogLv_Error, content_str, is_new)

    def WriteLog(self, log_id, log_lv, content, is_new = False):
        self.log_buffer[self.write_index].append(SLogBufferData(log_id, log_lv, content, is_new))
        
    def __SwitchIndex(self):
        self.write_index = 1 - self.write_index
        self.log_buffer[self.write_index].clear()
        
    def __CheckLogger(self):
        # 暂时先不处理，所有用到的日志文件全部打开
        pass
    
    def __SaveLogBuffer(self):
        try:
            if os.path.exists(self.log_path) and not os.path.isdir(self.log_path):
                os.remove(self.log_path)

            if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)

            #print(len(self.log_buffer[1 - self.write_index]))
            for item in self.log_buffer[1 - self.write_index]:
                # 低等级日志不输出
                if item.log_lv < self.LogLv_Config_LV:
                    continue;
                # 找type 如果有 更新时间 如果没有新增一个
                logger = None
                if item.log_id in self.all_logger:
                    logger = self.all_logger[item.log_id]
                    if item.is_new:
                        logger.file_writer.close()
                        logger.file_name = "%s/%s%s.log" % (self.log_path, item.log_id, time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
                        logger.file_writer = open(logger.file_name, "a")
                else:
                    logger = SLogTypeData("%s/%s%s.log" % (self.log_path, item.log_id, time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())))
                    logger.file_writer = open(logger.file_name, "a")
                    self.all_logger.update({item.log_id : logger})
                
                #print(logger.file_writer, item.content)
                logger.file_writer.write("%s %s\n" % (self.__GetLogPrefixByLevel(item.log_lv), item.content))

            for key in self.all_logger:
                self.all_logger[key].file_writer.flush()
        except Exception as err:
            print(err)

    def run(self):
        while True:
            # 将缓存区的日志存入本地文件
            self.__SaveLogBuffer()
            # 切换缓存
            self.__SwitchIndex()
            # 检测是否有长期不用的
            self.__CheckLogger()
            
            #self.sleep(1)
    
    @staticmethod
    def __GetLogPrefixByLevel(lv):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if lv == CLogger.LogLv_Error:
            return "%s [Error] " % time_str
        elif lv == CLogger.LogLv_Debug:
            return "%s [Debug] " % time_str
        elif lv == CLogger.LogLv_Info:
            return "%s [Info] " % time_str
        else:
            return "%s [Default] " % time_str