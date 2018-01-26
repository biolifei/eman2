set BASH_EXE=C:\Users\EMAN\Miniconda2\Library\bin\bash.exe
set "BASH_CMD=%BASH_EXE% --login -i -c"
set INSTALLER_DIR=C:\Users\EMAN\workspace\win-installers
set INSTALLER_FILE=eman2.21.win64.exe
set INSTALLATION_DIR=eman2-21-win64

%BASH_CMD% "bash C:/Users/EMAN/workspace/build-scripts-cron/cronjob.sh win"
if errorlevel 1 exit 1
