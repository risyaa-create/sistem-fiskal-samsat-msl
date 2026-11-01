@echo off
title Sistem Informasi Digitalisasi Data Fiskal SAMSAT Medan Selatan
cd /D "%~dp0"

echo =======================================================================
echo    SISTEM INFORMASI DIGITALISASI DATA FISKAL MUTASI KENDARAAN
echo                      SAMSAT MEDAN SELATAN
echo =======================================================================
echo.
echo [*] Memeriksa status database MySQL (Port 3306)...

powershell -Command "$t = Test-NetConnection -ComputerName 127.0.0.1 -Port 3306 -WarningAction SilentlyContinue; if (!$t.TcpTestSucceeded) { exit 1 } else { exit 0 }"
if %ERRORLEVEL% NEQ 0 (
    echo [*] MySQL belum aktif. Menjalankan MySQL XAMPP secara otomatis di latar belakang...
    if exist "C:\xampp\mysql\bin\mysqld.exe" (
        start "" /B "C:\xampp\mysql\bin\mysqld.exe" --defaults-file="C:\xampp\mysql\bin\my.ini" --standalone
        timeout /t 3 /nobreak >nul
        echo [+] MySQL XAMPP berhasil dijalankan!
    ) else (
        echo [!] Peringatan: Path C:\xampp\mysql\bin\mysqld.exe tidak ditemukan.
    )
) else (
    echo [+] Database MySQL sudah aktif (Port 3306).
)

echo.
echo [*] Menjalankan server aplikasi web (Flask)...
powershell -Command "$t = Test-NetConnection -ComputerName 127.0.0.1 -Port 5000 -WarningAction SilentlyContinue; if (!$t.TcpTestSucceeded) { exit 1 } else { exit 0 }"
if %ERRORLEVEL% NEQ 0 (
    start "Sistem Fiskal Samsat Flask" /MIN python app.py
    timeout /t 3 /nobreak >nul
    echo [+] Server Flask berhasil diaktifkan!
) else (
    echo [+] Server Flask sudah aktif (Port 5000).
)

:: Deteksi alamat IP Wi-Fi / LAN lokal secara otomatis
for /f "tokens=*" %%a in ('powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike '*Loopback*' -and $_.IPAddress -notlike '169.254*' } | Select-Object -First 1).IPAddress"') do set LOCAL_IP=%%a
if "%LOCAL_IP%"=="" set LOCAL_IP=127.0.0.1

echo.
echo =======================================================================
echo  SISTEM BERHASIL DIAKTIFKAN DAN SIAP DIGUNAKAN!
echo =======================================================================
echo.
echo  [1] Akses dari laptop ini:
echo      http://localhost:5000
echo.
echo  [2] Akses dari laptop/HP lain dalam satu jaringan Wi-Fi:
echo      http://%LOCAL_IP%:5000
echo.
echo  (Browser akan otomatis terbuka dalam beberapa detik...)
echo =======================================================================

start http://localhost:5000

echo.
echo Tekan tombol apa saja untuk menutup jendela informasi ini.
echo (Sistem tetap akan berjalan di latar belakang).
pause >nul
