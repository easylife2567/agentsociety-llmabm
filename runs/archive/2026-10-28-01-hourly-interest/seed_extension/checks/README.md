# 本批验证证据

本级记录可复查的实际检查，不承担运行状态；状态仍由上一级batch_execution.json单写，人工交接见run README。

| 资产 | 用途 |
|---|---|
| controller_check.log | 12项禁网假进程测试通过，不启动引擎、不对真实PID发信号 |
| runner_preflight.log | 最终103项冻结来源、两份seed0与18次排程的只读启动检查 |
| preflight.json、preflight.log | 18份官方schema/steps/env与1800份真实profile创建恢复，0网络/LLM/Ray启动尝试 |
| review.md | 独立限定范围控制器审查，审查完成后产生 |
| launch_check.json | 启动后实际PID/命令、SOCIETY_STEP/ENV_STATE与Agent决策核验，启动后产生 |
| closeout.log | 全部完成后的20条件实际完整性/回流/官方replay复核及18原始结果复制检查 |
| closeout_check.log | 相同原始来源下--check确定性复算及原始镜像SHA核对，复算后产生 |

上一级runner_check_attempt1.log保留假进程夹具首轮失败；runner_check_final.log与本级controller_check.log记录最终12项全部通过，不能将假进程错误当作真实仿真失败或将最终通过当作首次无错。
