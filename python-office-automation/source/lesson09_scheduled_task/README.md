# 第9课：定时任务

## 运行一次

```bash
python daily_report.py
```

会读取 `data/sales.xlsx`，在 `output/` 生成日报，并把运行记录写入 `run_log.txt`。

## Windows 任务计划程序

1. Win + S 搜索「任务计划程序」；
2. 右侧「创建基本任务」；
3. 触发器选择「每天」，设置时间；
4. 操作选择「启动程序」；
5. 程序/脚本选择：
   - 打包后的 `daily_report.exe`，或
   - 本目录的 `run_task.bat`；
6. 「起始于」填本目录的绝对路径；
7. 属性里勾选「不管用户是否登录都要运行」和「使用最高权限运行」；
8. 右键任务 →「运行」测试。

## 注意

- 不要把 `.py` 直接填进任务计划程序，除非你确认 Python 环境变量正确；
- 先把 `run_task.bat` 里的 Python 路径和项目路径改成你自己的；
- 后台运行不要用 `input()`，日志写到 `run_log.txt`；
- 相对路径容易出错，`daily_report.py` 已经用 `os.chdir(BASE_DIR)` 固定到脚本目录。
