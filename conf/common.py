#encoding:utf-8

# 主界面长宽
main_frame_size_width = 1280
main_frame_size_mininum = 791


# 登录QQ按钮
login_qq_column_count=6 #单行按钮数
login_qq_x_interval=10 # 列间距
login_qq_y_interval=10 # 行间距
login_qq_width=80 # 按钮宽
login_qq_height=30 # 按钮高

# 登录命令
login_cmd_format = r'start launch_dx_d para DummyGameNet false UseDummyInput true LogQQID %s LogID %s'

# 工作日志
work_logger = "WorkLog"
LogOpt_Init = 0
LogOpt_Add = 1
LogOpt_Del = 2
LogOpt_Upt = 3
LogOpt_Switch = 4

# 通用数据存储配置
common_db_path = "./data/shelve.db"
# 通用配置
common_config_path = "./config/common.ini"

#日志目录
logs_path = "/logs"

# 项目相关参数
star_svn_path = r"http://172.17.100.22/svn/starx52/%s"

trunc_name="trunc"
branch_svn_subfix = r"branches%s/%s"        # 分支SVN后缀格式
video_trunc_name="video_platform"
video_branch_svn_subfix = r'video_branches%s/%s'

branch_p4_prefix = "QQX5_Mainland_"
