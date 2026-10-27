"""将合并前的历史证据路径定位到统一主实验目录；不修改证据内容。"""
from functools import lru_cache
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELOCATION = ROOT / 'hypothesis_4/experiment_2/runs/timestamp_v1/relocation.json'


@lru_cache(maxsize=1)
def _moved_entries():
    if not RELOCATION.exists():
        return ()
    entries = json.loads(RELOCATION.read_text())['moved_entries']
    return tuple((ROOT / old, ROOT / new) for old, new in
                 sorted(entries.items(), key=lambda item: len(item[0]), reverse=True))


def resolve_asset_path(path):
    """保留现有路径；缺失的历史路径按迁移清单的最长前缀解析。"""
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    if path.exists():
        return path
    for old, new in _moved_entries():
        if path == old or old in path.parents:
            return new / path.relative_to(old)
    return path
