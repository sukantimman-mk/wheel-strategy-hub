@echo off
chcp 65001 >nul
title The Wheel Strategy Hub - Real-Time Sharing Guide
cls
echo ====================================================================
echo   ⚡ The Wheel Strategy Hub - แชร์ราคา Real-time ให้เพื่อน (Zero-Install)
echo ====================================================================
echo.
echo [1] ตรวจสอบ IP เครื่องของคุณสำหรับให้เพื่อนเข้าใช้งาน:
for /f "tokens=4" %%a in ('route print ^| findstr "\<0.0.0.0\>"') do set LOCAL_IP=%%a
echo       IP เครื่องของคุณคือ: http://%LOCAL_IP%:8000
echo.
echo [2] วิธีให้เพื่อนใช้งาน (เครื่องเพื่อนไม่ต้องลง Python แม้แต่น้อย):
echo       1. ให้เครื่องของคุณเปิด "start_server.bat" ทิ้งไว้
echo       2. ถ้าเพื่อนต่อ Wi-Fi เดียวกัน ให้เพื่อนเปิดเบราว์เซอร์แล้วเข้า:
echo          --> http://%LOCAL_IP%:8000
echo       3. เพื่อนจะเห็นราคาตลาดสด Real-time ทันที 100%%
echo.
echo ====================================================================
pause
