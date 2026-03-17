@echo off
chcp 65001 >nul
cls
echo.
echo ════════════════════════════════════════════════════════
echo   投票系统 - 快速启动
echo ════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/2] 启动 HTTP 服务器...
echo.
python -m http.server 8899

echo.
echo ════════════════════════════════════════════════════════
echo   服务器已启动！
echo ════════════════════════════════════════════════════════
echo.
echo   投票页面: http://localhost:8899/vote_standalone.html
echo   统计页面: http://localhost:8899/stats_standalone.html
echo.
echo   按 Ctrl+C 停止服务器
echo.
pause
