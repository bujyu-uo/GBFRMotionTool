@echo off

set pybin=""

if "%pybin%" == "" do (
    echo "(SETUP) Please set variable 'pybin' to target the path of python executable"
)

rem Forcely change to folder batch script in
cd %~dp0

:Loop
IF "%1"=="" GOTO EOF
    %pybin% cli.py -f %1 -a match -t task.json
SHIFT
GOTO Loop

:EOF
pause