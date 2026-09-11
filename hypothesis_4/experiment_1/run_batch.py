#!/usr/bin/env python3
"""run_batch: CurationDynamics H4E1 18-run 批量调度器（幂等 + 可选并发 + 崩溃续跑）。

布局约定（与 monitor.py 的 runs/* 自动发现对齐）：
    runs/<run_id>/           每个 run 独立目录
         ├─ pid.json            引擎 CLI 接管：status(running/completed/failed)/step_count/simulation_time
         ├─ SOCIETY_STEP.json   每 step 原子重写（本实验 11 步=11 周）
         ├─ stdout.log stderr.log   调度器重定向（同现有 ags.py 惯例）
         └─ replay/ env/ agents/ …  引擎产物（monitor 数据源）

幂等判定（每次调用重入安全，可反复跑"补齐缺口"）：
    completed        SOCIETY_STEP.step_count >= 11 且 terminated，或 pid.json.status == completed
    running          进程存活且 pid.json.status == running     → 等待，不重复启动
    failed           pid.json.status == failed                 → 跳过（或 --force 重跑）
    interrupted      有残留但未完结且进程已死                   → --resume-failed 时以 --resume 续跑
    pending          目录缺失/无数据                            → 正常启动

并发：
    --concurrency N 同时运行 N 个 run。默认 1=串行（最稳，无 Ray 端口/内存/缓存竞态）。
    引擎每进程独立 ray.init() 本地 head；并行时各 head 自动选端口，object_store 各 1GB。
    16GB 机器建议 ≤3；cache.pkl 已按 run 隔离（AGENTSOCIETY_HOME_DIR=agentsociety_data/runs/<id>）。

用法：
    # 串行补齐全部 18（已完成的自动跳过；可反复执行）
    $PYTHON_PATH hypothesis_4/experiment_1/run_batch.py
    # 并发 2；只跑指定 run；演练不启动
    $PYTHON_PATH hypothesis_4/experiment_1/run_batch.py --concurrency 2
    $PYTHON_PATH hypothesis_4/experiment_1/run_batch.py --only random_normal_s0,interest_sustained_hot_s2
    $PYTHON_PATH hypothesis_4/experiment_1/run_batch.py --dry-run
    # 中断残留续跑
    $PYTHON_PATH hypothesis_4/experiment_1/run_batch.py --resume-failed
    # 每个 run 完成后刷新 monitor 快照
    $PYTHON_PATH hypothesis_4/experiment_1/run_batch.py --with-monitor
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------- 路径 ----------------

SCRIPT_DIR = Path(__file__).resolve().parent          # hypothesis_4/experiment_1
WORKSPACE = SCRIPT_DIR.parents[1]                     # 仓库根
CONFIGS_DIR = SCRIPT_DIR / "init" / "configs"
STEPS_PATH = SCRIPT_DIR / "init" / "steps.yaml"
RUNS_ROOT = SCRIPT_DIR / "runs"
DATA_ROOT = WORKSPACE / "agentsociety_data" / "runs"  # 每个 run 隔离的 cache.home

EXP_ID_PREFIX = "h4e1_"
EXPECTED_STEPS = 11                                   # W12 → W22，11 ticks

# ---------------- .env ----------------

def load_env() -> dict[str, str]:
    """读取仓库 .env，返回需注入子进程的环境变量字典。只读，绝不打印敏感值。"""
    env = os.environ.copy()
    env_path = WORKSPACE / ".env"
    if not env_path.exists():
        return env
    try:
        from dotenv import dotenv_values
        vals = {k: str(v) for k, v in dotenv_values(env_path).items() if v is not None}
    except ModuleNotFoundError:
        # 无 python-dotenv 时退化为简单解析（键=值，# 注释，# 号不在引号值内）
        from_dotenv: dict[str, str] = {}
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            from_dotenv[k.strip()] = v.strip()
        vals = from_dotenv
    for k, v in vals.items():
        # .env 显式置空的不覆盖环境（保持默认），其余注入
        if v != "" or k not in env:
            env[k] = v
    return env


def resolve_python(env: dict[str, str]) -> str:
    return env.get("PYTHON_PATH") or sys.executable


# ---------------- run 状态 ----------------

def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _pid_alive(pid: int) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def classify_run(run_dir: Path) -> tuple[str, dict]:
    """返回 (state, detail)。state ∈ completed/running/failed/interrupted/pending。"""
    if not run_dir.is_dir():
        return "pending", {}
    pid_data = _read_json(run_dir / "pid.json")
    step_data = _read_json(run_dir / "SOCIETY_STEP.json")
    step = int(step_data.get("step_count", 0) or 0)
    terminated = bool(step_data.get("terminated"))
    status = pid_data.get("status")
    proc_pid = int(pid_data.get("pid") or 0)
    alive = _pid_alive(proc_pid)

    has_data = bool(step_data) or bool(pid_data) or (run_dir / "SOCIETY.json").exists()

    if status == "completed" or (step >= EXPECTED_STEPS and terminated):
        return "completed", {"step": step, "end": pid_data.get("end_time")}
    if status == "failed":
        return "failed", {"step": step, "reason": pid_data.get("reason", "pid.status=failed")}
    if status == "running" or (alive and has_data):
        return "running", {"pid": proc_pid, "step": step, "alive": alive}
    if has_data:  # 有残留数据，但既非 running 也未正式 completed/failed
        return "interrupted", {"step": step, "pid": proc_pid}
    return "pending", {}


def list_run_ids() -> list[str]:
    """按 manifest 顺序返回 18 个 run_id；manifest 缺失时按 configs/*.json 排序兜底。"""
    manifest = _read_json(CONFIGS_DIR / "manifest.json")
    ids = manifest.get("run_ids") or []
    if not ids:
        ids = sorted(p.stem for p in CONFIGS_DIR.glob("*.json") if p.stem != "manifest")
    return ids


def build_plan(run_ids: list[str], args) -> list[tuple[str, str, str]]:
    """返回 [(run_id, state, action)]。action ∈ start/resume/wait/skip/force。"""
    plan: list[tuple[str, str, str]] = []
    for rid in run_ids:
        state, _ = classify_run(RUNS_ROOT / rid)
        if args.force and state in ("completed", "failed"):
            plan.append((rid, state, "force"))
        elif state == "completed":
            plan.append((rid, state, "skip"))
        elif state == "running":
            plan.append((rid, state, "wait"))
        elif state == "interrupted":
            plan.append((rid, state, "resume" if args.resume_failed else "skip"))
        elif state == "failed":
            plan.append((rid, state, "skip"))
        else:
            plan.append((rid, state, "start"))
    return plan


# ---------------- 执行 ----------------

def _spawn_cli(
    py: str, run_id: str, env: dict[str, str],
    *,
    resume: bool = False,
    timeout_h: float = 6.0,
) -> subprocess.Popen:
    run_dir = RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg = CONFIGS_DIR / f"{run_id}.json"
    if not cfg.exists():
        raise FileNotFoundError(f"{cfg} 不存在（configs/ 应含全部 18 cell 配置）")
    cmd = [
        py, "-m", "agentsociety2.society.cli",
        "--config", str(cfg),
        "--steps", str(STEPS_PATH),
        "--run-dir", str(run_dir),
        "--experiment-id", f"{EXP_ID_PREFIX}{run_id}",
        "--log-level", "INFO",
    ]
    if resume:
        cmd.append("--resume")

    # 注入隔离 cache 目录（每个 run 独立 pkl，杜绝并发写竞态）
    run_env = env.copy()
    run_env["AGENTSOCIETY_HOME_DIR"] = str(DATA_ROOT / run_id)
    (DATA_ROOT / run_id).mkdir(parents=True, exist_ok=True)

    # 前置写 pid.json（CLI 随后接管并持续更新；前置保证 monitor 不报"无心跳"）
    from pathlib import Path as _P
    pid_f = _P(run_dir / "pid.json")
    pid_f.write_text(json.dumps({
        "pid": 0, "status": "running",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "experiment_id": f"{EXP_ID_PREFIX}{run_id}", "step_count": 0,
    }, indent=2), encoding="utf-8")

    with open(run_dir / "stdout.log", "ab") as so, open(run_dir / "stderr.log", "ab") as se:
        proc = subprocess.Popen(
            cmd, cwd=str(WORKSPACE), env=run_env,
            stdout=so, stderr=se, start_new_session=True, close_fds=True,
        )
    # 把真实 pid 回写（保留 CLI 使用的其余字段）
    pid_f.write_text(json.dumps({
        "pid": proc.pid, "status": "running",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "experiment_id": f"{EXP_ID_PREFIX}{run_id}", "step_count": 0,
    }, indent=2), encoding="utf-8")
    return proc


def _run_finished(run_dir: Path, timeout_h: float) -> tuple[bool, dict]:
    """run 是否已结束。返回 (finished, detail)。"""
    pid_data = _read_json(run_dir / "pid.json")
    step_data = _read_json(run_dir / "SOCIETY_STEP.json")
    step = int(step_data.get("step_count", 0) or 0)
    done = bool(pid_data.get("status") in ("completed", "failed"))
    done = done or (step >= EXPECTED_STEPS and bool(step_data.get("terminated")))
    return done, {"step": step, "pid_status": pid_data.get("status")}


async def run_one(
    py: str, run_id: str, env: dict[str, str],
    *,
    resume: bool, timeout_h: float, interval: float,
) -> dict:
    """启动一个 run 并阻塞至结束（或超时）。返回结束 meta。"""
    run_dir = RUNS_ROOT / run_id
    try:
        proc = _spawn_cli(py, run_id, env, resume=resume, timeout_h=timeout_h)
    except FileNotFoundError as e:
        return {"run_id": run_id, "launch": "error", "detail": str(e)}
    print(f"  [spawn] {run_id} pid={proc.pid} {'(resume)' if resume else ''} 启动于 {run_dir.name}")

    deadline = time.monotonic() + timeout_h * 3600
    last_log_ts = 0.0
    while time.monotonic() < deadline:
        finished, meta = _run_finished(run_dir, timeout_h)
        if finished:
            break
        # 进程已死但状态未写 completed：按残留处理（超时窗口内给 CLI 时间落盘）
        if not _pid_alive(proc.pid):
            await asyncio.sleep(3)
            finished, meta = _run_finished(run_dir, timeout_h)
            if not finished:
                break
        now = time.time()
        if now - last_log_ts >= 120:
            last_log_ts = now
            print(f"  [tick]  {run_id} step={meta.get('step','?')}/11")
        await asyncio.sleep(interval)

    # 最终状态
    finished, meta = _run_finished(run_dir, timeout_h)
    if _pid_alive(proc.pid):
        pid_data = _read_json(run_dir / "pid.json")
        if not finished:
            print(f"  [timeout] {run_id} 超过 {timeout_h}h 未完成，终止进程")
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            await asyncio.sleep(2)
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            # 标记 failed（保留 CLI 字段）
            pid_data["status"] = "failed"
            pid_data["reason"] = f"timeout>{timeout_h}h in run_batch"
            (run_dir / "pid.json").write_text(json.dumps(pid_data, indent=2), encoding="utf-8")
    step = _read_json(run_dir / "SOCIETY_STEP.json").get("step_count", 0)
    pid_status = _read_json(run_dir / "pid.json").get("status")
    outcome = "completed" if (pid_status == "completed" or int(step or 0) >= EXPECTED_STEPS) else (pid_status or "interrupted")
    print(f"  [done]  {run_id} outcome={outcome} step={step}/11")
    return {"run_id": run_id, "outcome": outcome, "step": step}


async def main_async(args) -> int:
    env = load_env()
    py = resolve_python(env)
    print(f"PYTHON: {py}")
    print(f"runs root: {RUNS_ROOT}")

    run_ids = args.only or list_run_ids() or sorted(
        p.stem for p in CONFIGS_DIR.glob("*.json") if p.stem != "manifest"
    )
    if args.skip:
        skipped = set(args.skip)
        run_ids = [r for r in run_ids if r not in skipped]

    plan = build_plan(run_ids, args)
    n_start = sum(1 for _, _, a in plan if a in ("start", "force", "resume"))
    n_skip = sum(1 for _, _, a in plan if a in ("skip", "wait"))
    print(f"\n计划：{len(plan)} 个 run → 启动 {n_start}，跳过/等待 {n_skip}")
    for rid, state, action in plan:
        print(f"    {rid:32s} state={state:10s} action={action}")
    if args.dry_run:
        print("\n[dry-run] 未启动任何进程。")
        return 0
    if n_start == 0:
        print("无待启动 run，结束。")
        return 0

    if args.without_confirm:
        pass  # 无人值守（cron/CI）用
    else:
        try:
            input("\n回车确认启动（Ctrl-C 取消）… ")
        except (KeyboardInterrupt, EOFError):
            print("\n已取消。")
            return 1

    # 并发槽位：维护至多 N 个中的子进程，逐个补位
    to_run = [(rid, action) for rid, _, action in plan if action in ("start", "force", "resume")]
    results: list[dict] = []
    sem = asyncio.Semaphore(max(1, args.concurrency))
    # 先进先出，严格保持 manifest 顺序（前序 cell 优先补齐）

    async def worker(rid: str, action: str):
        async with sem:
            r = await run_one(py, rid, env, resume=(action == "resume"),
                              timeout_h=args.timeout_h, interval=args.interval)
            results.append(r)
            if args.with_monitor:
                subprocess.run(
                    [py, str(SCRIPT_DIR / "monitor.py"), "--overview-only"],
                    cwd=str(WORKSPACE), env=env, timeout=600,
                )
            return r

    tasks = [asyncio.create_task(worker(rid, action)) for rid, action in to_run]
    await asyncio.gather(*tasks)

    # 汇总
    ok = [r for r in results if r.get("outcome") == "completed"]
    err = [r for r in results if r.get("outcome") != "completed"]
    print(f"\n==== 批量结束：{len(ok)} 完成 / {len(err)} 异常 ====")
    for r in results:
        print(f"    {r['run_id']:32s} {r.get('outcome','?'):11s} step={r.get('step','?')}")
    return 0 if not err else 2


def main() -> int:
    ap = argparse.ArgumentParser(description="H4E1 18-run 幂等批量调度器")
    ap.add_argument("--concurrency", type=int, default=1, help="并发 run 数（默认 1=串行；建议 ≤3）")
    ap.add_argument("--only", nargs="?", help="只跑指定 run_ids，逗号分隔")
    ap.add_argument("--skip", nargs="?", help="跳过指定 run_ids，逗号分隔")
    ap.add_argument("--force", action="store_true", help="强制重跑已完成/失败的 run")
    ap.add_argument("--resume-failed", action="store_true", help="中断残留以 --resume 续跑")
    ap.add_argument("--timeout-h", type=float, default=6.0, help="单 run 超时上限（小时，默认 6）")
    ap.add_argument("--interval", type=float, default=20.0, help="轮询间隔秒（默认 20）")
    ap.add_argument("--with-monitor", action="store_true", help="每完成一个 run 后刷新 monitor 总览")
    ap.add_argument("--without-confirm", action="store_true", help="启动前不询问（无人值守）")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划不启动")
    args = ap.parse_args()

    if args.only:
        args.only = [x.strip() for x in args.only.split(",") if x.strip()]
    if args.skip:
        args.skip = {x.strip() for x in args.skip.split(",") if x.strip()}

    try:
        return asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\n用户中断。已完成的 run 保持 completed（幂等，重跑会自动跳过）。")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())