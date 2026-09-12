@echo off
REM ============================================
REM 一键推送 multi-agent-roundtable 到 GitHub
REM 用法：网络恢复后双击本文件，或在此目录运行 push.bat
REM ============================================
cd /d "C:\Users\Administrator\Desktop\multi-agent-roundtable"

REM 使用 PortableGit
set GIT="C:\Users\Administrator\.workbuddy\binaries\PortableGit\versions\1.2.0\cmd\git.exe"

REM 本机代理：基础环境预置了坏代理 52532(到 github.com 超时/502)。
REM 真正生效的 Clash HTTP 出口在本机 7897（如 Clash 改端口请同步修改下面两行）。
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897

REM 跳过 PortableGit 系统级 gitconfig（含 helper-selector，且易报锁错误）；
REM 凭据走本仓库 .git/config 里设置的 wincred（Windows 凭据管理器，加密）。
set GIT_CONFIG_NOSYSTEM=1

echo ============================================
echo 正在推送到 GitHub...
echo ============================================
%GIT% push -u origin main

if %errorlevel%==0 (
    echo.
    echo [成功] 已推送完成！
    echo 仓库地址: https://github.com/cailibingvincent/multi-agent-roundtable
) else (
    echo.
    echo [失败] 推送失败，可能是网络到 GitHub 不通。
    echo 请检查代理/VPN 是否开启，然后重新运行本脚本。
)

pause
