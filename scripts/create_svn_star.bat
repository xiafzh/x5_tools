SET INPUT_PATH=%1
SET SVN_USERNAME=%2
SET SVN_PASSWORD=%3
SET SVN_PROJPATH=%4
svn co --username %SVN_USERNAME% --password %SVN_PASSWORD% %SVN_PROJPATH% %INPUT_PATH%/src/star/

