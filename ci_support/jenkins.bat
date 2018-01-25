set BASH_EXE=C:\Users\EMAN\Miniconda2\Library\bin\bash.exe
set "BASH_CMD=%BASH_EXE% --login -i -c"

%BASH_CMD% "bash C:/Users/EMAN/workspace/build-scripts-cron/cronjob.sh win"
if errorlevel 1 exit 1
