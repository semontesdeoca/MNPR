REM Contributor: Santiago Montesdeoca
@echo %off
REM go to directory
cd %~dp0%
REM create directory if it doesn't exist
if not exist ..\dist\shaders\ mkdir ..\dist\shaders\
REM for each *.fx file
for /f "tokens=1* delims=\" %%A in ('forfiles /s /m *.fx /c "cmd /c echo @relpath"') do (
    for %%F in (^"%%B) do (
	echo %%~F
	echo %%~nF
	echo %%~pF
	REM create subdirectory of shader
	for %%C in ("%%~F\..") do (
	    if not %%~nxC == shaders (
		echo "not shaders, create directory"
	    	if not exist ..\dist\shaders\%%~nxC mkdir ..\dist\shaders\%%~nxC
	    )
	)
	"C:\Program Files (x86)\Windows Kits\10\bin\x64\fxc.exe" /T fx_5_0 /Fo ..\dist\shaders\%%~Fo %%F
    )
)
echo "All shaders seem to have been compiled"
pause