@echo off
setlocal

if "%~2"=="" (
  echo Usage: test.bat ^<Tests.dproj^> ^<Win32^|Win64^>
  echo Set TEST_EXE when the project writes its executable elsewhere ^(DCC_ExeOutput^).
  exit /b 2
)

set "TEST_PROJECT=%~1"
set "TEST_PLATFORM=%~2"

call "%~dp0build.bat" "%TEST_PROJECT%" Debug %TEST_PLATFORM%
if errorlevel 1 exit /b %ERRORLEVEL%

if not defined TEST_EXE (
  set "TEST_EXE=%~dpn1.exe"
  if exist "%~dp1%TEST_PLATFORM%\Debug\%~n1.exe" set "TEST_EXE=%~dp1%TEST_PLATFORM%\Debug\%~n1.exe"
)

if not exist "%TEST_EXE%" (
  echo Test executable not found: %TEST_EXE%
  echo Set TEST_EXE to the path the test project writes its executable to.
  exit /b 2
)

"%TEST_EXE%"
exit /b %ERRORLEVEL%
