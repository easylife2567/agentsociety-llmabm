"""冻结的项目既有DTW函数；只提取函数，不执行历史脚本main。"""
from __future__ import annotations
import numpy as np
WINDOW = 1

def constrained_multivariate_dtw(
    simulated: np.ndarray, observed: np.ndarray, *, window: int = WINDOW
) -> tuple[float, list[tuple[int, int]]]:
    """Return path-normalized multivariate DTW and the optimal path.

    Each time point is the five-dimensional composition vector. Local cost is its
    Euclidean distance. The Sakoe--Chiba window is expressed in weekly indices.
    """
    if simulated.ndim != 2 or observed.ndim != 2:
        raise ValueError("DTW inputs must be two-dimensional [time, type]")
    if simulated.shape[1] != observed.shape[1]:
        raise ValueError("DTW inputs must have the same number of content types")

    n, m = len(simulated), len(observed)
    window = max(window, abs(n - m))
    inf = float("inf")
    cumulative = np.full((n, m), inf, dtype=float)
    path_length = np.zeros((n, m), dtype=int)
    predecessor: dict[tuple[int, int], tuple[int, int]] = {}

    for i in range(n):
        for j in range(max(0, i - window), min(m, i + window + 1)):
            local = float(np.linalg.norm(simulated[i] - observed[j]))
            if i == 0 and j == 0:
                cumulative[i, j] = local
                path_length[i, j] = 1
                continue

            # Prefer the diagonal only when cumulative costs tie.
            candidates = []
            for rank, (pi, pj) in enumerate(((i - 1, j - 1), (i - 1, j), (i, j - 1))):
                if pi >= 0 and pj >= 0 and np.isfinite(cumulative[pi, pj]):
                    candidates.append((cumulative[pi, pj], rank, pi, pj))
            if not candidates:
                continue
            _, _, pi, pj = min(candidates)
            cumulative[i, j] = cumulative[pi, pj] + local
            path_length[i, j] = path_length[pi, pj] + 1
            predecessor[(i, j)] = (pi, pj)

    if not np.isfinite(cumulative[-1, -1]):
        raise ValueError("No admissible DTW path under the selected window")

    path = [(n - 1, m - 1)]
    while path[-1] != (0, 0):
        path.append(predecessor[path[-1]])
    path.reverse()
    score = cumulative[-1, -1] / path_length[-1, -1]
    return score, path
