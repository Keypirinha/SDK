@if "%KEYPIRINHA_SDK%"=="" call "%~dp0env.cmd"

@rem KPSDK_PYTHON_ARCH allows to force the use of a specific python binary
@rem instead of relying upon autodetect
@if "%KPSDK_PYTHON_ARCH%"=="" set KPSDK_PYTHON_ARCH=%KPSDK_ARCH%

@set PYTHONHOME=%KEYPIRINHA_SDK%\bin\python\%KPSDK_PYTHON_ARCH%

@set PYTHONPATH=%~dp0lib
@set PYTHONPATH=%PYTHONPATH%;%KEYPIRINHA_SDK%\bin\python\lib\site
@set PYTHONPATH=%PYTHONPATH%;%KEYPIRINHA_SDK%\bin\python\lib\lib.zip
@set PYTHONPATH=%PYTHONPATH%;%KEYPIRINHA_SDK%\bin\python\%KPSDK_PYTHON_ARCH%\dlls

@set PYTHONDONTWRITEBYTECODE=1
@set PYTHONNOUSERSITE=1
@set PYTHONUNBUFFERED=1

@set KPSDK_PYTHONEXE=%PYTHONHOME%\python.exe
