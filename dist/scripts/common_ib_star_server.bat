SET INPUT_P4_PATH=%1
attrib -r %INPUT_P4_PATH%/exe/server/* /S /D
BuildConsole.exe %INPUT_P4_PATH%/src/star/build_server.sln /build /ALL /cfg="service_debug|Win32"	
