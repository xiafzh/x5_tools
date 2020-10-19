SET INPUT_P4_PATH=%1
p4 sync %INPUT_P4_PATH%/exe/debug_bin/...#head

p4 sync -f %INPUT_P4_PATH%/exe/debug_bin/Engine_d.pdb#head
p4 sync -f %INPUT_P4_PATH%/exe/debug_bin/Engine_d.dll#head
p4 sync -f %INPUT_P4_PATH%/exe/debug_bin/Engine.pdb#head
p4 sync -f %INPUT_P4_PATH%/exe/debug_bin/Engine.dll#head
p4 sync -f %INPUT_P4_PATH%/exe/debug_bin/Effect_dx_d.pdb#head
p4 sync -f %INPUT_P4_PATH%/exe/debug_bin/Effect_dx_d.dll#head
p4 sync -f %INPUT_P4_PATH%/exe/debug_bin/Effect_dx.pdb#head
p4 sync -f %INPUT_P4_PATH%/exe/debug_bin/Effect_dx.dll#head
