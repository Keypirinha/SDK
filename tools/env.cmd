@set KEYPIRINHA_SDK=%~dp0..

@set KPSDK_PATH=%KEYPIRINHA_SDK%\cmd

@set KPSDK_ARCH=x64
@reg query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" >NUL && set KPSDK_ARCH=x86
