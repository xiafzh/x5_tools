
REM 游戏部分和视频部分使用独立的app_box管理
start app_box_d
start app_box_d -port 27153
start app_box_d -port 27154
start app_box_d -port 27155

ping -n 5 127.0.0.1 > nul 2>&1

start admin_proxy_d ::-autostartall
start admin_client_new
