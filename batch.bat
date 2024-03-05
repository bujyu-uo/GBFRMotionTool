@echo off

set pybin="c:\Users\USER\.local\python-3.11.8-embed-amd64\python.exe"

rem Forcely change to folder batch script in
cd %~dp0

:Loop
IF "%1"=="" GOTO EOF
    %pybin% cli.py -f %1 -a match -t task.json
SHIFT
GOTO Loop

:EOF
pause