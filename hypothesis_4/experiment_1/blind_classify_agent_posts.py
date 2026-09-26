#!/usr/bin/env python3
"""对 1904 条 Agent 生成帖做盲法判类（W2 整改第二步）。

设计要点（为什么这样才算"盲"）
------------------------------
1. 判类模型 = GLM（`glm-5-3-flash-260828`），与生成模型 `deepseek-v4-flash` 不同族；
2. 判定标准 = **与真实帖文打标完全相同的那套 prompt**（从 `data/scripts/batch_label_v3.py` 以 AST
   原样提取，避免抄写漂移），因此生成文本与真实文本由同一把尺子度量、可直接比较；
3. 送给模型的用户消息**只有正文**：不含 arm、不含 pool_type / 身份、不含周次、不含
   环境的四词表及倾向分。脚本启动时对此做断言。

用法
----
    python blind_classify_agent_posts.py [model_id] [workers] [batch_size]
"""

from __future__ import annotations

import ast
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import dotenv
from openai import OpenAI

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
dotenv.load_dotenv(ROOT / ".env")

IN_JSONL = SCRIPT_DIR / "results" / "blind_classification" / "agent_posts.jsonl"
OUT_DIR = SCRIPT_DIR / "results" / "blind_classification"

MODEL = sys.argv[1] if len(sys.argv) > 1 else "glm-5-3-flash-260828"
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 16
BSIZE = int(sys.argv[3]) if len(sys.argv) > 3 else 8

SLUG = MODEL.replace("/", "_")
OUT_JSONL = OUT_DIR / f"judge_{SLUG}.jsonl"

CLIENT = OpenAI(
    api_key=os.environ["AGENTSOCIETY_LLM_API_KEY"],
    base_url=os.environ["AGENTSOCIETY_LLM_API_BASE"],
    timeout=180,
)

VALID_CATS = {"借势营销", "事件悼念讨论", "教育观点讨论", "梗文化讨论", "其他讨论", "爬取噪音"}


def load_system_prompt() -> str:
    """用 AST 从 batch_label_v3.py 原样取出 SYSTEM_PROMPT，保证量尺与真实数据一致。"""
    src = (ROOT / "data" / "scripts" / "batch_label_v3.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SYSTEM_PROMPT":
                    return ast.literal_eval(node.value)
    raise SystemExit("未能从 data/scripts/batch_label_v3.py 提取 SYSTEM_PROMPT")


SYSTEM_PROMPT = load_system_prompt()


def fmt_post(no: int, content: str) -> str:
    """与 batch_label_v3.fmt_post 同构；Agent 帖无平台/标题，留空以保持量尺结构一致。"""
    return f"【帖子{no}】\n平台：\n标题：\n正文：{(content or '')[:2000]}"


def extract_array(txt: str, expect: int) -> dict[int, tuple[str, str, str]]:
    if txt.startswith("```"):
        txt = txt.split("```")[1] if "```" in txt else txt
        if txt.startswith("json"):
            txt = txt[4:]
        txt = txt.strip()
    lo, hi = txt.find("["), txt.rfind("]")
    if lo < 0 or hi <= lo:
        raise ValueError(f"no json array: {txt[:80]}")
    arr = json.loads(txt[lo:hi + 1])
    if not isinstance(arr, list) or len(arr) != expect:
        raise ValueError(f"array len {len(arr) if isinstance(arr, list) else '?'} != {expect}")
    out: dict[int, tuple[str, str, str]] = {}
    for obj in arr:
        no = obj.get("no")
        if not isinstance(no, int) or no in out or not (1 <= no <= expect):
            raise ValueError(f"bad no: {no}")
        cat = obj.get("category", "其他讨论")
        if cat not in VALID_CATS:
            cat = "其他讨论"
        valid = obj.get("valid", "有效")
        if valid not in {"有效", "无效"}:
            valid = "有效"
        out[no] = (cat, str(obj.get("reason", ""))[:200], valid)
    return out


def label_batch(indices: list[int], contents: list[str]) -> list[dict]:
    user_msg = f"请依次判定以下 {len(contents)} 条帖子：\n\n" + "\n\n".join(
        fmt_post(i + 1, contents[i]) for i in range(len(contents))
    )
    # 盲法断言：用户消息里不得出现臂名、身份标签或周次
    lowered = user_msg.lower()
    for forbidden in ("random", "chronological", "interest", "pool_type", "2026-w"):
        if forbidden in lowered:
            raise SystemExit(f"盲法被破坏：用户消息含 {forbidden!r}")
    for attempt in range(3):
        try:
            resp = CLIENT.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.1,
                max_tokens=8000,
            )
            txt = (resp.choices[0].message.content or "").strip()
            got = extract_array(txt, len(contents))
            return [
                {
                    "index": idx,
                    "category": got[i + 1][0],
                    "reason": got[i + 1][1],
                    "valid": got[i + 1][2],
                    "failed": False,
                }
                for i, idx in enumerate(indices)
            ]
        except Exception as exc:  # noqa: BLE001
            if attempt == 2:
                return [
                    {"index": idx, "category": None, "reason": f"{type(exc).__name__}: {exc}"[:200],
                     "valid": None, "failed": True}
                    for idx in indices
                ]
            time.sleep(1.5 * (attempt + 1))
    return []


def main() -> int:
    records = [json.loads(line) for line in IN_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
    total = len(records)
    print(f"[配置] 模型={MODEL} 并发={WORKERS} 每次 {BSIZE} 条 | 待判 {total} 条", flush=True)

    done: dict[int, dict] = {}
    if OUT_JSONL.exists():
        for line in OUT_JSONL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                done[int(row["index"])] = row
        print(f"[断点] 已有 {len(done)} 条", flush=True)

    todo = [i for i in range(total) if i not in done or done[i].get("failed")]
    print(f"[进度] 待判 {len(todo)} 条", flush=True)

    batches = [todo[i:i + BSIZE] for i in range(0, len(todo), BSIZE)]
    lock = threading.Lock()
    handle = OUT_JSONL.open("a", encoding="utf-8")
    written = 0

    def work(batch: list[int]) -> None:
        nonlocal written
        rows = label_batch(batch, [records[i]["content"] for i in batch])
        with lock:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
            handle.flush()
            if written % (BSIZE * 10) < BSIZE:
                print(f"  …已写 {written}/{len(todo)}", flush=True)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(work, b) for b in batches]
        for _ in as_completed(futures):
            pass
    handle.close()

    rows = [json.loads(line) for line in OUT_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
    latest = {int(r["index"]): r for r in rows}
    failed = [i for i in range(total) if latest.get(i, {}).get("failed") or i not in latest]
    print(f"\n完成 {total - len(failed)}/{total}；失败 {len(failed)}", flush=True)
    print(f"✅ 结果：{OUT_JSONL}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
