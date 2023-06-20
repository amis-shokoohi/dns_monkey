@echo off

if exist "DNS Monkey.spec" del /q "DNS Monkey.spec"
if exist "build" rmdir /q /s "build"
if exist "dist" rmdir /q /s "dist"

pyinstaller --name "DNS Monkey" --windowed --uac-admin --icon dns_monkey.ico dns_monkey.py

copy "dns_monkey.ico" "dist\DNS Monkey\"
copy "LICENSE" "dist\DNS Monkey\"