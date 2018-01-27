@echo on

set "BASH_EXE=C:\Program Files\Git\bin\bash.exe"
set INSTALLER_DIR=C:\Users\EMAN\workspace\win-installers
set INSTALLER_FILE=eman2.21.win64.exe
set INSTALLATION_DIR=eman2-21-win64

set

::"%BASH_EXE%" -c "bash C:/Users/EMAN/workspace/build-scripts-cron/cronjob.sh win release/windows"
::if errorlevel 1 exit 1

rmdir /q /s %INSTALLER_DIR%\%INSTALLATION_DIR%
del /q /f %INSTALLER_DIR%\%INSTALLER_FILE%

start /wait "" %INSTALLER_DIR%\%INSTALLER_FILE% /InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=%INSTALLER_DIR%\%INSTALLATION_DIR%
if errorlevel 1 exit 1

call %INSTALLER_DIR%\%INSTALLATION_DIR%\Scripts\activate.bat
if errorlevel 1 exit 1

call tests\run_tests.bat
if errorlevel 1 exit 1

"%BASH_EXE%" -c "bash tests/run_prog_tests.sh"
if errorlevel 1 exit 1
