#!/usr/bin/env python3
"""weekly_lag1 的专用批跑入口；复用 run_batch 的幂等与完整性判定。"""

from __future__ import annotations

import json

import run_batch as batch


ROUND_ID = "weekly_lag1"
MANIFEST = batch.CONFIGS_DIR / f"{ROUND_ID}_manifest.json"

batch.ROUND_ID = ROUND_ID
batch.RUNS_ROOT = batch.SCRIPT_DIR / "runs" / ROUND_ID
batch.WEEKLY_STEPS_PATH = batch.SCRIPT_DIR / "init" / "steps_weekly_lag.yaml"
batch.EXP_ID_PREFIX = "h4e1_weekly_lag1_"


def list_weekly_lag_run_ids() -> list[str]:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [str(run_id) for run_id in document["run_ids"]]


batch.list_run_ids = list_weekly_lag_run_ids


if __name__ == "__main__":
    raise SystemExit(batch.main())
