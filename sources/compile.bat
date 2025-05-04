@echo off
cd /d ./
pyinstaller pngencoder.py --noconsole --onedir -i icon.ico
pause