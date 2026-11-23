@echo off
REM 定时任务启动脚本
REM 请把下面两个路径改成你自己的实际路径

cd /d D:\path\to\python-office-automation\lesson09_scheduled_task
C:\path\to\python.exe daily_report.py

REM 调试时可以保留，正式运行可以删掉
timeout /t 5
