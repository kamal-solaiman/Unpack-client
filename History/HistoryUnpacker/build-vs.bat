@echo off
setlocal
cd /d "%~dp0"
cmake -S . -B build -G "Visual Studio 18 2026" -A x64
if errorlevel 1 exit /b 1
cmake --build build --config Release
if errorlevel 1 exit /b 1
ctest --test-dir build -C Release --output-on-failure
if errorlevel 1 exit /b 1
echo Built: %CD%\build\Release\HistoryUnpacker.exe
