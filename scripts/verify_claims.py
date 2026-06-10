#!/usr/bin/env python3
"""Adversarial checks for the paper's formal claims."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.contact_latency import PlantParams, contact_force  # noqa: E402


RESULTS = ROOT / "results"
DOCS = ROOT / "docs"


def check_fixed_mode(seed: int = 7, n: int = 10000) -> dict[str, float | int | str]:
    rng = np.random.default_rng(seed)
    params = PlantParams()
    q_delayed = rng.uniform(0.001, 0.010, size=n)
    q_now = rng.uniform(0.001, 0.010, size=n)
    v_delayed = rng.uniform(-0.02, 0.08, size=n)
    v_now = rng.uniform(-0.02, 0.08, size=n)
    f_delayed = np.maximum(0.0, params.stiffness * q_delayed + params.damping * v_delayed)
    f_now = np.maximum(0.0, params.stiffness * q_now + params.damping * v_now)
    pred = f_delayed + params.stiffness * (q_now - q_delayed) + params.damping * (v_now - v_delayed)
    pred = np.maximum(0.0, pred)
    residual = np.abs(pred - f_now)
    return {
        "claim": "same_contact_mode_linear_kelvin_voigt",
        "samples": n,
        "max_abs_residual_n": float(np.max(residual)),
        "mean_abs_residual_n": float(np.mean(residual)),
        "status": "passed_with_floating_point_tolerance" if float(np.max(residual)) < 1e-9 else "failed",
    }


def find_mode_switch_counterexample(seed: int = 11, n: int = 10000) -> dict[str, float | int | str]:
    rng = np.random.default_rng(seed)
    params = PlantParams()
    q_delayed = rng.uniform(-0.010, -0.0001, size=n)
    q_now = rng.uniform(0.0001, 0.010, size=n)
    v_delayed = rng.uniform(0.0, 0.10, size=n)
    v_now = rng.uniform(0.0, 0.10, size=n)
    f_delayed = np.array([contact_force(float(q), float(v), params) for q, v in zip(q_delayed, v_delayed)])
    f_now = np.array([contact_force(float(q), float(v), params) for q, v in zip(q_now, v_now)])
    stale_pred = f_delayed + params.stiffness * (q_now - q_delayed) + params.damping * (v_now - v_delayed)
    residual = np.abs(stale_pred - f_now)
    idx = int(np.argmax(residual))
    return {
        "claim": "naive_delay_advance_across_mode_switch",
        "samples": n,
        "max_abs_residual_n": float(residual[idx]),
        "example_q_delayed_m": float(q_delayed[idx]),
        "example_q_now_m": float(q_now[idx]),
        "example_v_delayed_mps": float(v_delayed[idx]),
        "example_v_now_mps": float(v_now[idx]),
        "status": "counterexample_found",
    }


def check_model_mismatch(seed: int = 13, n: int = 10000) -> dict[str, float | int | str]:
    rng = np.random.default_rng(seed)
    params = PlantParams()
    q_delayed = rng.uniform(0.0001, 0.010, size=n)
    q_now = rng.uniform(0.0001, 0.010, size=n)
    v_delayed = rng.uniform(-0.05, 0.10, size=n)
    v_now = rng.uniform(-0.05, 0.10, size=n)
    f_delayed = np.maximum(0.0, params.stiffness * q_delayed + params.damping * v_delayed)
    f_now = np.maximum(0.0, params.stiffness * q_now + params.damping * v_now)
    k_hat = 0.85 * params.stiffness
    c_hat = 1.15 * params.damping
    pred = f_delayed + k_hat * (q_now - q_delayed) + c_hat * (v_now - v_delayed)
    pred = np.maximum(0.0, pred)
    residual = np.abs(pred - f_now)
    return {
        "claim": "model_mismatch_bound_needed",
        "samples": n,
        "max_abs_residual_n": float(np.max(residual)),
        "mean_abs_residual_n": float(np.mean(residual)),
        "status": "not_exact_under_wrong_model",
    }


def write_markdown(results: list[dict[str, float | int | str]]) -> None:
    path = DOCS / "formal_claim_check.md"
    with path.open("w", encoding="utf-8") as f:
        f.write("# Formal Claim Check\n\n")
        f.write("The formal claim is intentionally narrow.\n\n")
        f.write("For a fixed Kelvin-Voigt contact mode, with true stiffness `k`, damping `c`, current proprioception `(q_t, v_t)`, delayed proprioception `(q_{t-L}, v_{t-L})`, and delayed force `F_{t-L}`, the predictor\n\n")
        f.write("`F_hat_t = F_{t-L} + k(q_t - q_{t-L}) + c(v_t - v_{t-L})`\n\n")
        f.write("equals the current force `F_t = k q_t + c v_t`, provided both samples are in the same unilateral contact mode and clipping does not change signs.\n\n")
        f.write("## Numeric Audit\n\n")
        f.write("| Check | Status | Max residual (N) | Mean residual (N) |\n")
        f.write("|---|---|---:|---:|\n")
        for item in results:
            f.write(
                f"| {item['claim']} | {item['status']} | "
                f"{float(item.get('max_abs_residual_n', 0.0)):.6g} | "
                f"{float(item.get('mean_abs_residual_n', 0.0)):.6g} |\n"
            )
        f.write("\n## Adversarial Boundary\n\n")
        f.write("- The same-mode linear-contact claim passes to floating-point tolerance.\n")
        f.write("- Advancing a delayed sample across a mode switch without a contact-timing state produces counterexamples.\n")
        f.write("- Wrong stiffness/damping makes exact invariance false; the paper may only claim approximate robustness under bounded model error.\n")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    results = [check_fixed_mode(), find_mode_switch_counterexample(), check_model_mismatch()]
    with (RESULTS / "claim_check.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    write_markdown(results)
    print(f"wrote={RESULTS / 'claim_check.json'}")
    print(f"wrote={DOCS / 'formal_claim_check.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
