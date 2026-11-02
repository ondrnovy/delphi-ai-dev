@echo off
setlocal

if "%~3"=="" (
  echo Usage: build.bat ^<Project.dproj^> ^<Debug^|Release^> ^<Win32^|Win64^>
  exit /b 2
)

set "PROJECT=%~1"
set "CONFIG=%~2"
set "PLATFORM=%~3"

if "%BDS_RSVARS%"=="" set "BDS_RSVARS=C:\Program Files (x86)\Embarcadero\Studio\15.0\bin\rsvars.bat"

if not exist "%BDS_RSVARS%" (
  echo rsvars.bat not found: %BDS_RSVARS%
  echo Set BDS_RSVARS to the rsvars.bat of the Delphi installation.
  exit /b 2
)

call "%BDS_RSVARS%"
msbuild "%PROJECT%" /t:Build /p:Config=%CONFIG% /p:Platform=%PLATFORM% /nologo /v:minimal
exit /b %ERRORLEVEL%
