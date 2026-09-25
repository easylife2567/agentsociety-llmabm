#!/usr/bin/env python3
"""
失败行逐条重试脚本（通用版，任意模型轮次可用）。

背景：batch_label_v3.py 批量模式下，一批 8 条中任一条触发方舟内容审核即整批 400，
其余 7 条被"连坐"；且早期版本的末尾重试轮只认 dict 行，数组格式的失败从未被重试。
本脚本对 JSONL 中"无任何成功记录"的行做逐条单发重试：
  - max_tokens 提升（缓解思考耗尽导致的空 content）
  - 单条隔离（缓解批量连坐；单条仍被拒的才是真敏感内容）
结果以 dict 格式追加回同一 JSONL（与 v2/v3 断点文件兼容）。

用法: python retry_failed.py <model_id> <slug> [workers] [max_tokens]
"""
import os, sys, json, time, dotenv, openpyxl
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

dotenv.load_dotenv("/Users/easylife/Project/AgentSociety/.env")
API_KEY = os.environ["AGENTSOCIETY_LLM_API_KEY"]
API_BASE = os.environ["AGENTSOCIETY_LLM_API_BASE"]

MODEL = sys.argv[1]
SLUG = sys.argv[2]
WORKERS = int(sys.argv[3]) if len(sys.argv) > 3 else 16
MAX_TOKENS = int(sys.argv[4]) if len(sys.argv) > 4 else 16000
ATTEMPTS = 2

ROOT = "/Users/easylife/Project/AgentSociety"
SRC = f"{ROOT}/抖音微博小红书-全量已打标.xlsx"
JSONL = f"{ROOT}/.label_results_{SLUG}.jsonl"

print(f"[配置] 模型={MODEL} | 并发={WORKERS} | max_tokens={MAX_TOKENS} | 每次尝试={ATTEMPTS}", flush=True)

CLIENT = OpenAI(api_key=API_KEY, base_url=API_BASE, timeout=180)

# 判定标准与 batch_label.py / v2 / v3 完全一致
SYSTEM_PROMPT = """你是一个中文社交媒体内容分析助手。请对每条帖子进行三方面判定。

【内容类别 - 六选一，不允许自创】
- 借势营销：以商品、服务、账号引流、带货、二维码、价格、链接、限时优惠等为目的的推广内容；或借某热点人物/事件为特定产品/服务背书引流
- 事件悼念讨论：对逝者、事故、灾害、公共事件的缅怀、哀悼、点烛、RIP、默哀类内容；或围绕此类事件的严肃讨论
- 教育观点讨论：知识科普、观点输出、教育理念讨论、人生感悟、有信息增量的分析类内容（非营销）
- 梗文化讨论：meme、谐音梗、段子、玩梗、跟风玩梗、无实义的网络流行语、搞笑吐槽类内容
- 其他讨论：以上四类都不符合，但仍是正常有意义的帖子（如日常分享、生活记录、提问求助、情感抒发）
- 爬取噪音：乱码、纯表情、@好友无意义内容、无意义短文本、广告刷屏残留、空内容、格式损坏等无实质信息的条目

【数据有效性 - 二选一】
- 有效：包含可用于后续研究分析的实质内容
- 无效：无实质内容、纯噪音、纯营销引流无研究价值、或内容过于残缺无法分析

【判定原则】
1. 先判断是否为噪音：内容残缺/乱码/纯@人/纯表情 → 爬取噪音，无效
2. 再判断是否为营销：带货/引流/推广 → 借势营销，无效
3. 再判断是否为悼念：对逝者/事故/灾害的缅怀 → 事件悼念讨论，有效
4. 再判断是否为玩梗：meme/段子/谐音梗/跟风玩梗 → 梗文化讨论，有效
5. 再判断是否为教育观点：知识输出/观点分析/教育理念/人生感悟 → 教育观点讨论，有效
6. 以上都不符合 → 其他讨论，根据是否有实质内容判断有效性

【输出格式 - 严格 JSON 数组，不要任何其他文字】
对用户消息里的每条帖子依次判定，输出一个 JSON 数组，元素个数和顺序与输入帖子一一对应：
[{"no": 1, "category": "类别名", "reason": "一句话依据", "valid": "有效|无效"}, ...]"""

VALID_CATS = {"借势营销", "事件悼念讨论", "教育观点讨论", "梗文化讨论", "其他讨论", "爬取噪音"}


def load_records():
    """兼容 dict 行与 v3 数组行，返回 {row_num: [按序records]}。"""
    out = {}
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if isinstance(o, dict) and "row_num" in o:
                rec = o
            elif isinstance(o, list) and len(o) == 5 and isinstance(o[0], int):
                rec = {"row_num": o[0], "category": str(o[1]), "reason": str(o[2]),
                       "valid": str(o[3]), "failed": bool(o[4])}
            else:
                continue
            out.setdefault(rec["row_num"], []).append(rec)
    return out


def fmt_post(k, title, content, media):
    return f"【帖子{k}】\n平台：{media or ''}\n标题：{title or ''}\n正文：{(content or '')[:2000]}"


def extract_array(txt, expect):
    if txt.startswith("```"):
        txt = txt.split("```")[1] if "```" in txt else txt
        if txt.startswith("json"):
            txt = txt[4:]
        txt = txt.strip()
    lo, hi = txt.find("["), txt.rfind("]")
    if lo < 0 or hi <= lo:
        raise ValueError(f"no json array: {txt[:60]}")
    arr = json.loads(txt[lo:hi + 1])
    if not isinstance(arr, list) or len(arr) != expect:
        raise ValueError(f"array len {len(arr) if isinstance(arr, list) else '?'} != {expect}")
    out = {}
    for obj in arr:
        no = obj.get("no")
        if not isinstance(no, int) or no in out or not (1 <= no <= expect):
            raise ValueError(f"bad no: {no}")
        cat = obj.get("category", "其他讨论")
        reason = str(obj.get("reason", ""))[:200]
        valid = obj.get("valid", "有效")
        if cat not in VALID_CATS:
            cat = "其他讨论"
        if valid not in {"有效", "无效"}:
            valid = "有效"
        out[no] = (cat, reason, valid)
    return out


def label_one(rn, title, content, media):
    user_msg = "请依次判定以下 1 条帖子：\n\n" + fmt_post(1, title, content, media)
    for attempt in range(ATTEMPTS):
        try:
            r = CLIENT.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.1, max_tokens=MAX_TOKENS,
            )
            txt = (r.choices[0].message.content or "").strip()
            if not txt:
                raise ValueError("empty content (thinking exhausted max_tokens?)")
            cat, reason, valid = extract_array(txt, 1)[1]
            return {"row_num": rn, "category": cat, "reason": reason, "valid": valid, "failed": False}
        except Exception as e:
            if attempt == ATTEMPTS - 1:
                return {"row_num": rn, "category": "其他讨论",
                        "reason": f"[API失败:{str(e)[:80]}]", "valid": "无效", "failed": True}
            time.sleep(2)


def append_jsonl(recs):
    with open(JSONL, "a") as f:
        for rec in recs:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main():
    t0 = time.time()
    print("读取源数据...", flush=True)
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb["Sheet1"]
    it = ws.iter_rows(values_only=True)
    header = list(next(it))
    idx = {name: header.index(name) for name in ["title", "content", "full_content", "media_type"]}
    rows = {}
    rn = 1
    for row in it:
        rn += 1
        if row is None or all(v is None for v in row):
            continue
        rows[rn] = row
    wb.close()

    records = load_records()
    failed_rows = sorted(n for n, rs in records.items() if not any(not r.get("failed") for r in rs))
    print(f"全程失败待重试：{len(failed_rows)} 条", flush=True)
    if not failed_rows:
        print("无可重试行", flush=True)
        return

    buf, ok_cnt, fail_cnt = [], 0, 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(label_one, n, rows[n][idx["title"]],
                          rows[n][idx["content"]] or rows[n][idx["full_content"]],
                          rows[n][idx["media_type"]]): n for n in failed_rows}
        for fut in as_completed(futs):
            rec = fut.result()
            buf.append(rec)
            if rec.get("failed"):
                fail_cnt += 1
            else:
                ok_cnt += 1
            done = ok_cnt + fail_cnt
            if len(buf) >= 50:
                append_jsonl(buf)
                buf = []
            if done % 100 == 0:
                elapsed = time.time() - t0
                print(f"进度 {done}/{len(failed_rows)} | 成功 {ok_cnt} 仍失败 {fail_cnt} | "
                      f"{elapsed/60:.1f} 分钟", flush=True)
    if buf:
        append_jsonl(buf)

    print(f"\n重试完成：成功 {ok_cnt}，仍失败 {fail_cnt}", flush=True)
    records = load_records()
    still = sorted(n for n, rs in records.items() if not any(not r.get("failed") for r in rs))
    print(f"最终仍无成功判定：{len(still)} 条", flush=True)
    if still:
        print(f"行号：{still}", flush=True)


if __name__ == "__main__":
    main()
