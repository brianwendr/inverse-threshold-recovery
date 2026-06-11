#!/usr/bin/env python3
"""Replicate main-text tables, Supplementary Table S1, and trace files for the ORL acquire-divest hysteresis manuscript.

The script is intentionally dependency-light. It reads capability parameters from
config/capabilities.csv and regenerates the threshold, decomposition, band-order,
and budget-path trace CSV files used in the manuscript.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)


def read_capabilities() -> List[Dict[str, str]]:
    with (CONFIG / "capabilities.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f4(x: float) -> str:
    return f"{x:.4f}"


def thresholds(row: Dict[str, str]) -> Dict[str, float]:
    alpha = float(row["alpha"])
    eta = float(row["eta"])
    c_plus = float(row["c_plus"])
    c_minus = float(row["c_minus"])
    phi = alpha / eta
    a = c_plus / eta
    b = c_minus / eta
    t_plus = (alpha - c_plus) / eta
    t_minus = (alpha + c_minus) / eta
    rho = (c_plus + c_minus) / eta
    ceil_plus = math.ceil(t_plus)
    ceil_minus = math.ceil(t_minus)
    abs_error = abs((ceil_minus - ceil_plus) - rho)
    return {
        "phi": phi,
        "a": a,
        "b": b,
        "T_plus": t_plus,
        "T_minus": t_minus,
        "rho": rho,
        "ceil_T_plus": ceil_plus,
        "ceil_T_minus": ceil_minus,
        "abs_error": abs_error,
    }


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def generate_tables(caps: List[Dict[str, str]]) -> Dict[str, Dict[str, float]]:
    th = {row["capability"]: thresholds(row) for row in caps}
    # Table 2: carry-through parameters.
    write_csv(
        OUTPUT / "manuscript_table2_capability_parameters.csv",
        [
            {
                "capability": r["capability"],
                "description": r["description"],
                "d": r["d"],
                "alpha": r["alpha"],
                "eta": r["eta"],
                "c_plus": r["c_plus"],
                "c_minus": r["c_minus"],
                "phi": f4(th[r["capability"]]["phi"]),
                "prerequisites": r["prerequisites"] or "-",
            }
            for r in caps
        ],
        ["capability", "description", "d", "alpha", "eta", "c_plus", "c_minus", "phi", "prerequisites"],
    )
    # Table 3: thresholds and integer-grid error.
    write_csv(
        OUTPUT / "manuscript_table3_threshold_verification.csv",
        [
            {
                "capability": c,
                "T_plus": f4(v["T_plus"]),
                "T_minus": f4(v["T_minus"]),
                "ceil_T_plus": v["ceil_T_plus"],
                "ceil_T_minus": v["ceil_T_minus"],
                "rho": f4(v["rho"]),
                "abs_error": f4(v["abs_error"]),
            }
            for c, v in th.items()
        ],
        ["capability", "T_plus", "T_minus", "ceil_T_plus", "ceil_T_minus", "rho", "abs_error"],
    )
    # Table 4: decomposition.
    write_csv(
        OUTPUT / "supplementary_tableS1_frictionless_friction_decomposition.csv",
        [
            {
                "capability": c,
                "phi": f4(v["phi"]),
                "a": f4(v["a"]),
                "b": f4(v["b"]),
                "T_plus": f4(v["T_plus"]),
                "T_minus": f4(v["T_minus"]),
                "rho": f4(v["rho"]),
            }
            for c, v in th.items()
        ],
        ["capability", "phi", "a", "b", "T_plus", "T_minus", "rho"],
    )
    # Table 5: prerequisite pair ordering.
    pairs = [("c1", "c2"), ("c1", "c3"), ("c2", "c4"), ("c2", "c5"), ("c3", "c5"), ("c2", "c6")]
    rows = []
    for u, k in pairs:
        du = th[u]
        dk = th[k]
        phi_diff = du["phi"] - dk["phi"]
        max_term = max(du["a"] - dk["a"], -(du["b"] - dk["b"]))
        sep_term = du["a"] + dk["b"]
        rows.append(
            {
                "u": u,
                "k": k,
                "phi_u_minus_phi_k": f4(phi_diff),
                "max_term": f4(max_term),
                "condition_iii": "yes" if phi_diff >= max_term - 1e-10 else "no",
                "a_u_plus_b_k": f4(sep_term),
                "condition_iv": "yes" if phi_diff >= sep_term - 1e-10 else "no",
                "Tplus_u_ge_Tplus_k": "yes" if du["T_plus"] >= dk["T_plus"] - 1e-10 else "no",
                "Tminus_u_ge_Tminus_k": "yes" if du["T_minus"] >= dk["T_minus"] - 1e-10 else "no",
            }
        )
    write_csv(
        OUTPUT / "manuscript_table4_band_ordering_verification.csv",
        rows,
        [
            "u", "k", "phi_u_minus_phi_k", "max_term", "condition_iii",
            "a_u_plus_b_k", "condition_iv", "Tplus_u_ge_Tplus_k", "Tminus_u_ge_Tminus_k",
        ],
    )
    return th


def region(s: float, t_plus: float, t_minus: float) -> str:
    if s < t_plus:
        return "below T_plus / acquire side"
    if s >= t_minus:
        return "above T_minus / divest side"
    return "inside band"


def update_state(s_prev: float, s_cur: float, state: int, t_plus: float, t_minus: float) -> Tuple[int, str]:
    """Componentwise relay update for a single segment."""
    # Downward crossing below T_plus triggers acquisition.
    if state == 0 and s_prev >= t_plus and s_cur < t_plus:
        return 1, "acquire"
    # Upward crossing reaching or crossing T_minus triggers divestiture.
    if state == 1 and s_prev < t_minus and s_cur >= t_minus:
        return 0, "divest"
    return state, "retain" if state == 1 else "remain absent"


def generate_traces(th: Dict[str, Dict[str, float]]) -> None:
    t_plus = th["c1"]["T_plus"]
    t_minus = th["c1"]["T_minus"]
    table6_path = [6.00, 4.80, 6.00, 9.00, 6.00]
    state = 0
    rows = []
    for i, s in enumerate(table6_path):
        if i == 0:
            action = "absent"
        else:
            state, action = update_state(table6_path[i - 1], s, state, t_plus, t_minus)
        rows.append({"step": i, "s": f"{s:.2f}", "region": region(s, t_plus, t_minus), "action": action, "y1": state})
    write_csv(OUTPUT / "manuscript_table5_dynamic_budget_loop_c1.csv", rows, ["step", "s", "region", "action", "y1"])

    table7_rows = [
        {
            "case": "Saturated return",
            "path": "9.50 -> 4.50 -> 9.50",
            "initial_state": "absent at 9.50",
            "threshold_events": "acquire below 5.00; divest at 8.75",
            "final_state": "absent at 9.50",
        },
        {
            "case": "Band-interior non-return",
            "path": "6.00 -> 4.50 -> 6.00",
            "initial_state": "absent at 6.00",
            "threshold_events": "acquire below 5.00; no divest crossing",
            "final_state": "held at 6.00",
        },
        {
            "case": "Dual non-return",
            "path": "6.00 -> 9.00 -> 6.00",
            "initial_state": "held at 6.00",
            "threshold_events": "divest at 8.75; no acquire",
            "final_state": "absent at 6.00",
        },
    ]
    write_csv(
        OUTPUT / "manuscript_table6_return_point_trace_certificate.csv",
        table7_rows,
        ["case", "path", "initial_state", "threshold_events", "final_state"],
    )

    # Additional supplementary trace for Section 5.6 prerequisite partial loop.
    partial_rows = [
        {"step": 0, "s": "6.00", "event": "start", "portfolio": "{}", "closed": "yes"},
        {"step": 1, "s": "4.50", "event": "c1 crosses below T1_plus=5.00; acquire c1", "portfolio": "{c1}", "closed": "yes"},
        {"step": 2, "s": "6.00", "event": "return to band; no c2 acquisition because T2_plus=2.00 not crossed", "portfolio": "{c1}", "closed": "yes"},
    ]
    write_csv(
        OUTPUT / "supplement_partial_prerequisite_loop_trace.csv",
        partial_rows,
        ["step", "s", "event", "portfolio", "closed"],
    )


def main() -> None:
    caps = read_capabilities()
    th = generate_tables(caps)
    generate_traces(th)
    print("Replication outputs written to", OUTPUT)


if __name__ == "__main__":
    main()
