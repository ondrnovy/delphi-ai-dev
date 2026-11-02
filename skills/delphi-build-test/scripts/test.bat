@echo off
setlocal

if "%~2"=="" (
  echo Usage: test.bat ^<Tests.dproj^> ^<Win32^|Win64^>
  exit /b 2
)

set "PROJECT=%~1"
set "PLATFORM=%~2"

call "%~dp0build.bat" "%PROJECT%" Debug %PLATFORM%
if errorlevel 1 exit /b %ERRORLEVEL%

set "TEST_EXE=%~dpn1.exe"
for %%D in ("%~dp1%PLATFORM%\Debug\%~n1.exe") do if exist "%%~fD" set "TEST_EXE=%%~fD"

if not exist "%TEST_EXE%" (
  echo Test executable not found: %TEST_EXE%
  exit /b 2
)

"%TEST_EXE%"
exit /b %ERRORLEVEL%
