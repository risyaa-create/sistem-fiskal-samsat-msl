@echo off
title Hentikan Sistem Fiskal Samsat
cd /D "%~dp0"

echo =======================================================================
echo            MENGHENTIKAN SISTEM FISKAL SAMSAT MEDAN SELATAN
echo =======================================================================
echo.
echo [*] Menghentikan server Flask (Port 5000)...
powershell -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

echo [+] Server web Flask berhasil dihentikan.
echo.
set /p stop_mysql="Apakah Anda juga ingin mematikan database MySQL? (Y/T): "
if /I "%stop_mysql%"=="Y" (
    powershell -Command "Get-Process -Name mysqld -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"
    echo [+] Database MySQL berhasil dihentikan.
)

echo.
echo Sistem telah dihentikan.
timeout /t 2 >nul
