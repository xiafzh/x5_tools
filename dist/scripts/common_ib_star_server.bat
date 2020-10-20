SET INPUT_P4_PATH=%1

BuildConsole.exe %INPUT_P4_PATH%/src/star/build_server.sln /build /ALL /cfg="service_debug|Win32"	
