@ECHO OFF
SET INPUT_P4_PATH=%1
SET P4USER=%2
SET P4PASSWD=%3
SET P4PORT=%4
SET P4CLIENT=%5
p4 sync -f %INPUT_P4_PATH%/exe/server/...#head
	
