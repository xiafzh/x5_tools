@ECHO OFF
SET INPUT_P4_PATH=%1
SET P4USER=%2
SET P4PASSWD=%3
SET P4PORT=%4
SET P4CLIENT=%5
p4 -u %P4USER% -p %P4PORT% -P %P4PASSWD% -c %P4CLIENT% sync %INPUT_P4_PATH%/exe/debug_bin/...#head

p4 -u %P4USER% -p %P4PORT% -P %P4PASSWD% -c %P4CLIENT% sync -f %INPUT_P4_PATH%/exe/debug_bin/Engine_d.pdb#head
p4 -u %P4USER% -p %P4PORT% -P %P4PASSWD% -c %P4CLIENT% sync -f %INPUT_P4_PATH%/exe/debug_bin/Engine_d.dll#head
p4 -u %P4USER% -p %P4PORT% -P %P4PASSWD% -c %P4CLIENT% sync -f %INPUT_P4_PATH%/exe/debug_bin/Engine.pdb#head
p4 -u %P4USER% -p %P4PORT% -P %P4PASSWD% -c %P4CLIENT% sync -f %INPUT_P4_PATH%/exe/debug_bin/Engine.dll#head
p4 -u %P4USER% -p %P4PORT% -P %P4PASSWD% -c %P4CLIENT% sync -f %INPUT_P4_PATH%/exe/debug_bin/Effect_dx_d.pdb#head
p4 -u %P4USER% -p %P4PORT% -P %P4PASSWD% -c %P4CLIENT% sync -f %INPUT_P4_PATH%/exe/debug_bin/Effect_dx_d.dll#head
p4 -u %P4USER% -p %P4PORT% -P %P4PASSWD% -c %P4CLIENT% sync -f %INPUT_P4_PATH%/exe/debug_bin/Effect_dx.pdb#head
p4 -u %P4USER% -p %P4PORT% -P %P4PASSWD% -c %P4CLIENT% sync -f %INPUT_P4_PATH%/exe/debug_bin/Effect_dx.dll#head
