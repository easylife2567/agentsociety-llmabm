# 两路调度与API变更核对

本轮只修改run专属控制器，不改科学配置、Agent、环境、主项目机器状态。原模型固定deepseek-v4-1-flash-260910；共享额外上限990、请求上界10890和原截止北京时间2026-10-17 20:21:11保持。实时状态统一看run README。

| 直接资产 | 用途 |
|---|---|
| baseline.json | 本轮准确Git/控制器起点、API字段变更类别；不含密钥 |
| run_ablation.before.py | 布局修正后、并行修改前的准确控制器源 |
| run_ablation.final.py | 与当前控制器一致的最终源；从before应用../../parallel-control.patch可恢复 |
| offline-check.json | 合成九条件、接管不重复、并行上限2、共享预算越界和错误联停检查，0网络/LLM调用 |
| serial-state.json | 暂停原监督器后保存的一致状态；当前引擎PID保留 |
| serial-runtime-plan.json | 并行授权变更前的原始第二次运行计划，含原截止/哈希/预算 |
| live-check.json | 实际接管后的进程、冻结文件、模型固定与预算核对摘要（完成核对后写入） |

恢复顺序：原startup-failure控制器起点→output-layout.patch→本目录before→parallel-control.patch；新增check_parallel.py直接保留。最终完整补丁已在准确起点副本执行git apply --check、git apply，并与实际源逐字节相同。旧配置恢复包不变，本轮调度材料单独保存。

交接先向原父监督器发STOP取得一致状态，核对其唯一CLI子进程与状态一致，再发HUP/CONT使父监督器退出并释放原锁；引擎为独立session，保持PID和已有进度。新监督器取得同一锁，接管原引擎并按manifest顺序补充第二路。TERM/INT保留为异常时向两路发送INT的停止入口；宽限180秒后仍存活则TERM，绝不自动重跑或续接checkpoint。

.env默认模型也发生变化，本批新子进程只覆盖模型环境变量为原冻结版本，其余读取交接时新API；当前引擎继续用旧API直到结束或联停。未进行额外模型探针；正式去R seed0已成功取得新接口返回，response_model为原固定版本；已有去D旧接口回传简写标识deepseek-v4-1-flash，与该进程历史记录一致，两路请求环境变量均为冻结的完整版本。合成测试不证明新接口兼容，也不证明消融科学结论。
