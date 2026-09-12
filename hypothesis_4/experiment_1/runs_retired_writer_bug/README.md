# 退役 run：replay 写入器被覆盖为 dict（2026-09-13）

## 目录内容

- `interest_s1/` —— 9-run 批跑（3 并发）中第 2 次触发同一崩溃的 run。

## 事故形态

引擎把 run **申报成 completed**（`stdout.log` 末尾 `Experiment completed successfully`），
但 `pid.json` 里 `step_count: 0`，replay 里**只有 `core_agent_profile` 100 行**
（= 100 agent × 1），curation_dynamics 两张表**一行都没有**。

崩溃栈（`interest_s1/stderr.log`）：

```
File ".../custom/envs/curation_dynamics_space.py", line 1209, in step
    await self._write_env_state(self._step_index, t, **self._env_row(week, merged))
File ".../agentsociety2/env/base.py", line 836, in _write_env_state
    await self._replay_writer.write(table_name, {"step": step, "t": t, **data})
AttributeError: 'dict' object has no attribute 'write'
```

同一形态在 `random_s2` 上也出现过一次（见 `runs_retired_pre_batch/random_s2`），
即 9 次运行中命中 2 次，命中率约 22%，且**不报错、不留行**。

## 根因（静态排查结论）

`EnvBase.set_replay_writer`（`env/base.py:635-651`）先赋值 `self._replay_writer = writer`，
再 `loop.create_task(self._register_state_tables())` **异步**注册表。而
`EnvRouterActor.set_replay_writer`（`env_router_actor.py:132-140`）与
`Society.init()`（`society/society.py:374`，fire-and-forget）**都会写同一个属性**。

于是存在这样的交错：

1. 好写入器 A 就位 → 调度注册任务 T1；
2. T1 跑到一半（`await` 让出）时，迟到的 `set_replay_writer(坏对象)` 把属性改成 B；
3. T1 收尾，置 `_state_tables_registered = True`；
4. 之后 `_write_env_state`：`_replay_writer` 非 None → 跳过注册守卫 → 对 B 调 `.write` → 崩。

坏对象是**普通 dict**，形状 `{"replay_dir": …, "enabled": …}` —— 正是
`ReplayProxy.__getstate__()` 的返回形状。已排除 Ray 往返本身：
`ReplayProxy` 在 pickle / copy / deepcopy / ray 往返中类型均保持不变。

## 处置

1. `custom/envs/curation_dynamics_space.py` 增加 `set_replay_writer` 守卫：
   **拒绝非写入器对象、保留原有好写入器**，并把传入类型 + 调用栈打成 ERROR。
   宁可少一次覆盖，也不能让非写入器把整张表写空。
2. `interest_s1` 清空重跑。
3. 曾把「引擎自称 completed」当成通过口径——该 bug 正是靠 `pid.json` 的
   step 数校验才被发现的，故 `verify_experiment.py` 的 B10（replay 行数 =
   n_agents × 11）是这条防线上不可省的一环。
