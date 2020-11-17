@ECHO OFF
SET SVNPATH=%1
BuildConsole.exe %SVNPATH%\src\star\build_server.sln /build /ALL /cfg="service_debug|Win32"
BuildConsole.exe %SVNPATH%\src\star\build_client.sln /build /ALL /cfg="Debug|Win32"
BuildConsole.exe %SVNPATH%\src\video\build_video_client.sln /build /ALL /cfg="Debug|Win32"
