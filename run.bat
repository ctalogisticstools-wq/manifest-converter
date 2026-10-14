@echo off
title Manifest Converter
cd /d "%~dp0"
call .venv\Scripts\activate
echo.
echo =====================================
echo   Starting Manifest Converter...
echo =====================================
echo.
echo Do not close this window while using the app.
echo Press Ctrl+C to stop.
echo.
streamlit run app.py
pause