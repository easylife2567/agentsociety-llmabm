# 纯离线分析工具

`extract.py`调用官方analysis query-data读取12次replay，独立核对实际Agent与环境、配置/profile、时钟和发布，再产生CSV。`plot.py`按事先声明的图契约绘图；`chart3b_template.py`是原模板源的未修改冻结副本。`report.py`将已核对数据和人工撰写的中英文解释输出为MD及原生HTML，并写候选综合。`verify.py`从原始Agent记录独立复算27项主指标/差值、检查全部本地链接及零新增调用边界。`offline_guard/sitecustomize.py`只在命令PYTHONPATH显式指定时阻止网络连接，不影响其他进程或主项目.env。

本轮工具均为新增文件，没有修改既有代码；完整最终源保留于本目录，不把试错补丁混入交付。操作命令及依赖见上一级README和checks/dependencies.json。
