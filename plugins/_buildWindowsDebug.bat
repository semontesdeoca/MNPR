@echo %off
setlocal enableDelayedExpansion
if exist %~dp0%build rmdir /s /q build
if not exist %~dp0%build md build
cd %~dp0%build
set /p M_YEAR=Maya version (year): 
set M_GEN="Visual Studio 15 2017 Win64"
set /p "M_GEN=Enter build generator or press [ENTER] for default [%M_GEN%]: "
cmake ../ -G %M_GEN% -DMAYA_VERSION=%M_YEAR%
cmake --build . --config Debug
endlocal
pause