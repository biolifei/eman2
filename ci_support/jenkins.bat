set "BASH_EXE=C:\Program Files\Git\bin\bash.exe"
set "BASH_CMD=%BASH_EXE% -c"
set INSTALLER_DIR=C:\Users\EMAN\workspace\win-installers
set INSTALLER_FILE=eman2.21.win64.exe
set INSTALLATION_DIR=eman2-21-win64

"%BASH_CMD%" "bash C:/Users/EMAN/workspace/build-scripts-cron/cronjob.sh win release/windows"
if errorlevel 1 exit 1

rmdir /q /s %INSTALLER_DIR%\%INSTALLATION_DIR%

start /wait "" %INSTALLER_DIR%\%INSTALLER_FILE% /InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=%INSTALLER_DIR%\%INSTALLATION_DIR%
if errorlevel 1 exit 1

call %INSTALLER_DIR%\%INSTALLATION_DIR%\Scripts\activate.bat
if errorlevel 1 exit 1

call tests\run_tests.bat
if errorlevel 1 exit 1

"%BASH_CMD%" "bash tests/run_prog_tests.sh"
if errorlevel 1 exit 1
