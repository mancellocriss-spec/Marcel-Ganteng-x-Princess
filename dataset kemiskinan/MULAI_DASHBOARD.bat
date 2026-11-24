@echo off
chcp 65001 >nul
title Dashboard Kemiskinan Indonesia

echo.
echo ============================================================
echo   DASHBOARD KEMISKINAN INDONESIA - LAUNCHER
echo ============================================================
echo.
echo Memeriksa lingkungan Python...
echo.

python --version 2>nul
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan di PATH.
    echo Silakan install Python 3.10+ dari https://python.org
    echo.
    pause
    exit /b 1
)

echo.
echo Memeriksa dependencies...
pip list | findstr /i "streamlit pandas plotly" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Beberapa dependencies belum terinstall.
    echo Menginstall dari requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Gagal menginstall dependencies.
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo   Memulai Dashboard di http://localhost:8501
echo ============================================================
echo.
echo Tekan CTRL+C untuk menghentikan server.
echo.

streamlit run dashboard_kemiskinan.py --server.port 8501 --server.headless true

echo.
echo Server dihentikan.
pause