@echo off
rem Builds unpack-client.exe on Windows. Tries MSVC (cl), then MinGW (g++).
rem Run it from a "x64 Native Tools Command Prompt" for the MSVC path, or from
rem any shell that has g++ in PATH for the MinGW path.
setlocal
cd /d %~dp0

where cl >nul 2>nul
if %errorlevel%==0 goto msvc

where g++ >nul 2>nul
if %errorlevel%==0 goto mingw

where cmake >nul 2>nul
if %errorlevel%==0 goto cmake

echo No compiler found. Install Visual Studio Build Tools, MinGW-w64 or CMake.
exit /b 1

:msvc
echo [build] MSVC
if not exist build mkdir build
cl /nologo /EHsc /std:c++17 /O2 /W3 /utf-8 /D_CRT_SECURE_NO_WARNINGS /DNOMINMAX ^
   /Isrc /Itests /Fobuild\ /Founpack-client.exe src\*.cpp tests\testsupport.cpp ^
   /link /OUT:unpack-client.exe
if %errorlevel%==0 goto done
echo [build] MSVC failed
exit /b 1

:mingw
echo [build] MinGW
if not exist build mkdir build
g++ -std=c++17 -O2 -Wall -Wextra -Wno-unused-parameter -Isrc -Itests ^
    -static -static-libgcc -static-libstdc++ ^
    -o unpack-client.exe src\*.cpp tests\testsupport.cpp
if %errorlevel%==0 goto done
echo [build] MinGW failed
exit /b 1

:cmake
echo [build] CMake
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j
if %errorlevel%==0 goto done
echo [build] CMake failed
exit /b 1

:done
echo.
echo Built unpack-client.exe - try: unpack-client.exe --help
echo Self test:               unpack-client.exe test
endlocal
