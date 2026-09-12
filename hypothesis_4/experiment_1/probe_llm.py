"""一次性探针：分别用 default / coder 两把凭据各发一次 LLM 调用。

只读 .env（不打印任何敏感值），成功则打印延迟与返回片段，失败则打印异常类型。
用后即删，不属于实验产物。
"""

from __future__ import annotations

import os
import time


def load_env(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


load_env()

import litellm  # noqa: E402

PAIRS = [
    ("default", "AGENTSOCIETY_LLM_API_BASE", "AGENTSOCIETY_LLM_API_KEY", "AGENTSOCIETY_LLM_MODEL"),
    ("coder", "AGENTSOCIETY_CODER_LLM_API_BASE", "AGENTSOCIETY_CODER_LLM_API_KEY",
     "AGENTSOCIETY_CODER_LLM_MODEL"),
]

N = int(os.environ.get("PROBE_N", "2"))
for role, base_v, key_v, model_v in PAIRS:
    base = os.environ.get(base_v, "") or os.environ.get("AGENTSOCIETY_LLM_API_BASE", "")
    key = os.environ.get(key_v, "") or os.environ.get("AGENTSOCIETY_LLM_API_KEY", "")
    model = os.environ.get(model_v, "") or os.environ.get("AGENTSOCIETY_LLM_MODEL", "")
    print(f"--- {role}: base={base} model={model} "
          f"key_present={bool(key)} key_len={len(key)} key_prefix={key[:3]!r}")
    for i in range(N):
        t0 = time.time()
        try:
            r = litellm.completion(
                model=f"openai/{model}",
                api_base=base,
                api_key=key,
                messages=[{"role": "user", "content": "回复两个字：收到"}],
                max_tokens=16,
                timeout=60,
            )
            dt = time.time() - t0
            txt = (r.choices[0].message.content or "")[:40].replace("\n", " ")
            print(f"    [{i+1}/{N}] OK {dt:.2f}s -> {txt!r}")
        except Exception as e:  # noqa: BLE001
            dt = time.time() - t0
            print(f"    [{i+1}/{N}] FAIL {dt:.2f}s {type(e).__name__}: {str(e)[:160]}")
        if i < N - 1:
            time.sleep(2)
