SET INPUT_P4_PATH=%1
attrib -r %INPUT_P4_PATH%/exe/bin/* /S /D
attrib -r %INPUT_P4_PATH%/exe/debug_bin/* /S /D
BuildConsole.exe %INPUT_P4_PATH%/src/video/build_video_client.sln /build /ALL /cfg="Debug|Win32"
