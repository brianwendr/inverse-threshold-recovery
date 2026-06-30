#!/usr/bin/env python3
"""Minimal deterministic replication code for the RAIRO-Operations Research manuscript.

It regenerates the finite calculations reported in Section 6:
Table 1: base instance;
Table 2: boundary verification;
Table 3: systematic finite-instance verification.

No external data, no stochastic simulation, and no third-party packages are used.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

EPS = 1e-6
OUTDIR = Path("results")


def first_crossing(C, sigma: float, N: int) -> int:
    """Return min{q in {0,...,N}: C(q) <= -sigma}, or N+1 if none."""
    for q in range(N + 1):
        if C(q) <= -sigma + 1e-12:
            return q
    return N + 1


def interval(C, t: int, N: int):
    """Feasible sigma interval for threshold t."""
    if t == 0:
        return -math.inf, -C(0)
    if t == N + 1:
        return -C(N), math.inf
    return -C(t - 1), -C(t)


def fmt_interval(lo: float, hi: float) -> str:
    if math.isinf(lo):
        return f"(-inf, {hi:.3f}]"
    if math.isinf(hi):
        return f"({lo:.3f}, +inf)"
    return f"({lo:.3f}, {hi:.3f}]"


def near_origin(lo: float, hi: float) -> str:
    """Sparse near-origin representative used in the manuscript tables."""
    if lo < 0.0 <= hi:
        return "0"
    if hi < 0.0:
        return f"{hi:.3f}"
    return f"{lo:.3f}+"  # open lower endpoint, approached from the right


def write_csv(name: str, rows: list[dict], columns: list[str]) -> None:
    OUTDIR.mkdir(exist_ok=True)
    with (OUTDIR / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def table1_and_table2():
    N = 9
    C = {
        1: lambda q: 1.1 - 0.5 * q,
        2: lambda q: 0.5 - 0.4 * q,
    }
    sigma = {
        (1, 1): 1.0, (1, 2): 2.0,
        (2, 1): 2.0, (2, 2): 3.0,
        (3, 1): 0.0, (3, 2): 1.0,
    }

    table1, table2 = [], []
    for m in (1, 2, 3):
        T, I, reps = {}, {}, {}
        for a in (1, 2):
            T[a] = first_crossing(C[a], sigma[(m, a)], N)
            lo, hi = interval(C[a], T[a], N)
            I[a] = (lo, hi)
            reps[a] = near_origin(lo, hi)

            above_hi = hi + EPS
            below_lo = lo - EPS
            t_above = first_crossing(C[a], above_hi, N)
            t_below = first_crossing(C[a], below_lo, N)
            table2.append({
                "pair": f"({m},{a})",
                "interval_delta": f"{fmt_interval(lo, hi)} [{hi - lo:.3f}]",
                "forward_sigma": f"{sigma[(m, a)]:.3f}",
                "above_hi": f"{hi:.3f}+eps",
                "threshold_above_hi": f"{t_above} ({t_above - T[a]:+d})",
                "below_lo": f"{lo:.3f}-eps",
                "threshold_below_lo": f"{t_below} ({t_below - T[a]:+d})",
            })

        table1.append({
            "m": m,
            "T1_m": T[1],
            "T2_m": T[2],
            "I_m1_delta_0.500": fmt_interval(*I[1]),
            "I_m2_delta_0.400": fmt_interval(*I[2]),
            "near_origin_representative": f"Sigma_{m}1={reps[1]}, Sigma_{m}2={reps[2]}",
        })
    return table1, table2


def parametric_row(K: int, N: int) -> dict:
    widths = [(2 * a - 1) * 0.25 * 9.0 / N for a in range(1, K)]
    all_widths, volume = [], 1.0
    for width in widths:
        for _m in range(1, K + 1):
            all_widths.append(width)
            volume *= width
    delta_min = min(all_widths)
    return {
        "K": K,
        "N": N,
        "dim": K * (K - 1),
        "vol": f"{volume:.3e}",
        "delta_bar": f"{sum(all_widths) / len(all_widths):.4f}",
        "delta_min": f"{delta_min:.4f}",
        "inverse_delta_min": f"{1.0 / delta_min:.3f}",
        "irrelevant_pairs": K - 1,
        "type": "Param.",
    }


def independent_row() -> dict:
    N, K = 10, 3
    C = {
        1: lambda q: 1.5 - 0.6 * q,
        2: lambda q: 0.8 - 0.35 * q,
    }
    sigma = {
        (1, 1): 0.5, (1, 2): 1.2,
        (2, 1): 1.8, (2, 2): 2.6,
        (3, 1): 0.1, (3, 2): 0.7,
    }
    expected_T = {(1, 1): 4, (2, 1): 6, (3, 1): 3,
                  (1, 2): 6, (2, 2): 10, (3, 2): 5}
    widths, volume, irrelevant = [], 1.0, 0
    for key, sig in sigma.items():
        _m, a = key
        t = first_crossing(C[a], sig, N)
        assert t == expected_T[key]
        lo, hi = interval(C[a], t, N)
        widths.append(hi - lo)
        volume *= hi - lo
        if lo < 0.0 <= hi:
            irrelevant += 1
    return {
        "K": K,
        "N": N,
        "dim": K * (K - 1),
        "vol": f"{volume:.3e}",
        "delta_bar": f"{sum(widths) / len(widths):.4f}",
        "delta_min": f"{min(widths):.4f}",
        "inverse_delta_min": f"{1.0 / min(widths):.3f}",
        "irrelevant_pairs": irrelevant,
        "type": "Indep.",
    }


def table3():
    rows = [parametric_row(K, N) for K in (2, 3, 4) for N in (9, 19, 49)]
    rows.append(independent_row())
    return rows


def main() -> None:
    t1, t2 = table1_and_table2()
    t3 = table3()
    write_csv("table1_base_instance.csv", t1,
              ["m", "T1_m", "T2_m", "I_m1_delta_0.500", "I_m2_delta_0.400", "near_origin_representative"])
    write_csv("table2_boundary_verification.csv", t2,
              ["pair", "interval_delta", "forward_sigma", "above_hi", "threshold_above_hi", "below_lo", "threshold_below_lo"])
    write_csv("table3_systematic_verification.csv", t3,
              ["K", "N", "dim", "vol", "delta_bar", "delta_min", "inverse_delta_min", "irrelevant_pairs", "type"])
    print("Regenerated Section 6 CSV files in ./results")


if __name__ == "__main__":
    main()
