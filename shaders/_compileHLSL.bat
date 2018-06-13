REM Contributor: Santiago Montesdeoca
@echo %off
setlocal enabledelayedexpansion
REM Find effect compiler
set FXC_PATH="C:\Program Files (x86)\Windows Kits\10\bin\x64\fxc.exe"
if not exist !FXC_PATH! (
set FXC_PATH="C:\Program Files (x86)\Windows Kits\10\bin\10.0.15063.0\x64\fxc.exe"
if not exist !FXC_PATH! (
set FXC_PATH="C:\Program Files (x86)\Windows Kits\10\bin\10.0.16299.0\x64\fxc.exe"
if not exist !FXC_PATH! (
set FXC_PATH="C:\Program Files (x86)\Windows Kits\10\bin\10.0.17134.0\x64\fxc.exe"
if not exist !FXC_PATH! (
set FXC_PATH="C:\Program Files (x86)\Windows Kits\8.1\bin\x64\fxc.exe"
if not exist !FXC_PATH! (
echo fxc.exe not found on this computer
pause
exit
)))))
if exist !FXC_PATH! (
echo Effect compiler found
echo %FXC_PATH%
pause
)

REM Compile
cd %~dp0%
REM for each *.fx file
for /f "tokens=1* delims=\" %%A in ('forfiles /s /m *.fx /c "cmd /c echo @relpath"') do (
    for %%F in (^"%%B) do (
	REM echo %%~F
	REM echo %%~nF
	REM echo %%~pF
	!FXC_PATH! /T fx_5_0 /Fo %%~Fo %%F
    )
)
echo All shaders seem to have been compiled
pause
exit
