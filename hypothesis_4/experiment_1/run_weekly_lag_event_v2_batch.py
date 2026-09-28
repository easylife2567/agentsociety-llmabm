#!/usr/bin/env python3
"""weekly_lag1_event_v2 专用批跑入口；仅在用户审核后手动启动。"""

from __future__ import annotations

import json

import run_batch as batch


ROUND_ID = "weekly_lag1_event_v2"
MANIFEST = batch.CONFIGS_DIR / f"{ROUND_ID}_manifest.json"

batch.ROUND_ID = ROUND_ID
batch.RUNS_ROOT = batch.SCRIPT_DIR / "runs" / ROUND_ID
batch.WEEKLY_STEPS_PATH = (
    batch.SCRIPT_DIR / "init" / f"steps_{ROUND_ID}.yaml"
)
batch.EXP_ID_PREFIX = "h4e1_weekly_lag1_event_v2_"
batch.EXPECTED_STEPS = 12


def list_event_v2_run_ids() -> list[str]:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [str(run_id) for run_id in document["run_ids"]]


batch.list_run_ids = list_event_v2_run_ids


if __name__ == "__main__":
    raise SystemExit(batch.main())
