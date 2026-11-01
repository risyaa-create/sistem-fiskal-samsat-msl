@echo off
title Buka Akses Port 5000 Windows Firewall - SAMSAT Medan Selatan
echo ====================================================================
echo  MEMBUKA AKSES PORT 5000 AGAR BISA DIAKSES DARI LAPTOP LAIN
echo ====================================================================
echo.
echo Sedang meminta izin Administrator Windows...
powershell -Command "Start-Process cmd -ArgumentList '/c netsh advfirewall firewall add rule name=\"Sistem Fiskal Samsat Port 5000\" dir=in action=allow protocol=TCP localport=5000 && echo. && echo Aturan firewall BERHASIL ditambahkan! Port 5000 sekarang terbuka untuk laptop lain. && pause' -Verb RunAs"
echo.
echo Silakan klik 'Yes' jika muncul jendela konfirmasi Administrator.
