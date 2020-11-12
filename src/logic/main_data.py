#encoding:utf-8

class SBranchItem:
    def __init__(self, title, proj_path, p4_path, workspace):
        self.title = title
        self.projpath = proj_path
        self.p4path = p4_path
        self.workspace = workspace
    def __str__(self):
        return "{0} {1} {2}".format(self.title, self.projpath, self.p4path)

class SProjectItem:
    def __init__(self, title):
        self.title = title


WT_Invalid = 0
WT_COMPILE = 1  # 定时编译


class STimerInfo:
    def __init__(self):
        # 工作类型
        self.work_type = 0
        # 执行类型
        self.exe_type = 0
        # 回调参数
        self.param = {}

        # 是否已经执行和执行距离起始间隔时间 daily以上可用
        # 最好不要超过执行类型对应的间隔
        self.has_executed = True    # 默认为已经执行过
        self.start_interval = 0
        

    def __str__(self):
        return ("{0} {1} {2}".format(self.work_type, self.exe_type, self.has_executed))
