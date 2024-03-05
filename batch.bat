@echo off

set pybin=""

if "%pybin%" == "" (
    echo "(SETUP) Please set variable 'pybin' to target the path of python executable"
    GOTO EOF
)

rem Forcely change to folder batch script in
cd %~dp0

:Loop
IF "%1"=="" GOTO EOF
    %pybin% cli.py -f %1 -a dump
SHIFT
GOTO Loop

:EOF
pause