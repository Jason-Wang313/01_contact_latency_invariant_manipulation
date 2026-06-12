#!/usr/bin/env python3
"""Run latency sweep experiments for contact-age invariant control."""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.contact_latency import (  # noqa: E402
    CautiousDelayedController,
    ContactAgeTargetOnlyController,
    ContactAgeInvariantController,
    ControlParams,
    DelayedForceController,
    ForceAdvanceOnlyController,
    PlantParams,
    latency_slope,
    simulate,
)


RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
PAPER_FIGURES = ROOT / "paper" / "figures"


def ensure_dirs() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)


def make_controllers(nominal_latency: float) -> list:
    return [
        DelayedForceController(),
        CautiousDelayedController(float(nominal_latency)),
        ForceAdvanceOnlyController(),
        ContactAgeTargetOnlyController(),
        ContactAgeInvariantController(),
    ]


def summarize_rows(rows: list[dict[str, float | str]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, float | str]]] = {}
    for row in rows:
        grouped.setdefault(str(row["controller"]), []).append(row)

    summary: dict[str, dict[str, float]] = {}
    for name, items in grouped.items():
        xs = np.array([float(item.get("configured_latency_s", item["latency_s"])) for item in items])
        peak = np.array([float(item["peak_force_n"]) for item in items])
        over = np.array([float(item["overshoot_n"]) for item in items])
        impulse = np.array([float(item["impulse_250ms_ns"]) for item in items])
        summary[name] = {
            "peak_force_latency_slope_n_per_s": latency_slope(xs, peak),
            "overshoot_latency_slope_n_per_s": latency_slope(xs, over),
            "impulse_latency_slope_ns_per_s": latency_slope(xs, impulse),
            "mean_peak_force_n": float(np.mean(peak)),
            "max_peak_force_n": float(np.max(peak)),
            "mean_overshoot_n": float(np.mean(over)),
        }
    return summary


def run_main_sweep() -> tuple[list[dict[str, float | str]], dict[str, dict[str, float]]]:
    latencies = np.array([0.0, 0.005, 0.010, 0.020, 0.040, 0.060, 0.080, 0.100, 0.125, 0.150])
    rows: list[dict[str, float | str]] = []
    for latency in latencies:
        for controller in make_controllers(float(latency)):
            result = simulate(controller, float(latency), PlantParams(), ControlParams())
            metrics = result.metrics()
            rows.append(metrics)
    return rows, summarize_rows(rows)


def run_mismatch_ablation() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    latencies = [0.0, 0.04, 0.08, 0.12]
    for k_scale in [0.75, 0.90, 1.0, 1.10, 1.25]:
        for latency in latencies:
            control = ControlParams(k_hat_scale=k_scale)
            result = simulate(ContactAgeInvariantController(), latency, PlantParams(), control)
            metrics = result.metrics()
            metrics["k_hat_scale"] = k_scale
            rows.append(metrics)
    return rows


def run_seeded_stress(n_seeds: int = 30) -> tuple[list[dict[str, float | str]], dict[str, dict[str, float]]]:
    rows: list[dict[str, float | str]] = []
    latencies = [0.0, 0.04, 0.08, 0.12, 0.15]
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        stiffness_scale = float(np.clip(rng.normal(1.0, 0.15), 0.65, 1.35))
        damping_scale = float(np.clip(rng.normal(1.0, 0.25), 0.45, 1.75))
        servo_scale = float(np.clip(rng.normal(1.0, 0.20), 0.55, 1.55))
        gap_scale = float(np.clip(rng.normal(1.0, 0.20), 0.55, 1.55))
        k_hat_scale = float(np.clip(rng.normal(1.0, 0.15), 0.65, 1.35))
        c_hat_scale = float(np.clip(rng.normal(1.0, 0.25), 0.45, 1.75))
        base = PlantParams()
        plant = PlantParams(
            servo_tau=base.servo_tau * servo_scale,
            stiffness=base.stiffness * stiffness_scale,
            damping=base.damping * damping_scale,
            initial_gap=base.initial_gap * gap_scale,
        )
        control = ControlParams(k_hat_scale=k_hat_scale, c_hat_scale=c_hat_scale)
        for configured_latency in latencies:
            effective_latency = float(max(0.0, configured_latency + rng.normal(0.0, 0.005)))
            for controller in make_controllers(configured_latency):
                result = simulate(controller, effective_latency, plant, control)
                metrics = result.metrics()
                metrics["seed"] = seed
                metrics["configured_latency_s"] = configured_latency
                metrics["effective_latency_s"] = effective_latency
                metrics["stiffness_scale"] = stiffness_scale
                metrics["damping_scale"] = damping_scale
                metrics["servo_scale"] = servo_scale
                metrics["gap_scale"] = gap_scale
                metrics["k_hat_scale"] = k_hat_scale
                metrics["c_hat_scale"] = c_hat_scale
                rows.append(metrics)

    summary: dict[str, dict[str, float]] = {}
    for name in sorted({str(row["controller"]) for row in rows}):
        items = [row for row in rows if row["controller"] == name]
        peaks = np.array([float(row["peak_force_n"]) for row in items])
        overs = np.array([float(row["overshoot_n"]) for row in items])
        high = np.array(
            [
                float(row["peak_force_n"])
                for row in items
                if abs(float(row["configured_latency_s"]) - 0.15) < 1e-9
            ]
        )
        high_ci = 1.96 * float(np.std(high, ddof=1)) / float(np.sqrt(len(high))) if len(high) > 1 else 0.0
        summary[name] = {
            "n_runs": float(len(items)),
            "mean_peak_force_n": float(np.mean(peaks)),
            "p95_peak_force_n": float(np.percentile(peaks, 95)),
            "max_peak_force_n": float(np.max(peaks)),
            "mean_overshoot_n": float(np.mean(overs)),
            "failure_rate_peak_gt_12n": float(np.mean(peaks > 12.0)),
            "high_latency_150ms_mean_peak_n": float(np.mean(high)),
            "high_latency_150ms_ci95_peak_n": high_ci,
        }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    keys: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def plot_peak(rows: list[dict[str, float | str]]) -> Path:
    path = FIGURES / "peak_force_vs_latency.png"
    plt.figure(figsize=(6.4, 3.8))
    names = ["delayed_force", "delay_scaled_cautious", "contact_age_invariant"]
    labels = {
        "delayed_force": "Delayed force feedback",
        "delay_scaled_cautious": "Delay-scaled cautious",
        "contact_age_invariant": "Contact-age invariant",
    }
    for name in names:
        items = [row for row in rows if row["controller"] == name]
        xs = [1000.0 * float(row["latency_s"]) for row in items]
        ys = [float(row["peak_force_n"]) for row in items]
        plt.plot(xs, ys, marker="o", linewidth=2, label=labels[name])
    plt.axhline(8.0, color="black", linestyle="--", linewidth=1, label="Target force")
    plt.xlabel("Force/tactile sensing latency (ms)")
    plt.ylabel("Peak contact force (N)")
    plt.title("First-contact peak force under delayed contact evidence")
    plt.grid(True, alpha=0.25)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def plot_ablation(rows: list[dict[str, float | str]]) -> Path:
    path = FIGURES / "mechanism_ablation.png"
    plt.figure(figsize=(6.6, 4.0))
    names = [
        "delayed_force",
        "force_advance_only",
        "contact_age_target_only",
        "contact_age_invariant",
    ]
    labels = {
        "delayed_force": "Delayed force",
        "force_advance_only": "Advance only",
        "contact_age_target_only": "Age target only",
        "contact_age_invariant": "Full method",
    }
    for name in names:
        items = [row for row in rows if row["controller"] == name]
        xs = [1000.0 * float(row["latency_s"]) for row in items]
        ys = [float(row["peak_force_n"]) for row in items]
        plt.plot(xs, ys, marker="o", linewidth=2, label=labels[name])
    plt.axhline(8.0, color="black", linestyle="--", linewidth=1, label="Target force")
    plt.xlabel("Force/tactile sensing latency (ms)")
    plt.ylabel("Peak contact force (N)")
    plt.title("Ablation of force advancement and contact-age phasing")
    plt.grid(True, alpha=0.25)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def plot_stress(rows: list[dict[str, float | str]]) -> Path:
    path = FIGURES / "seeded_stress_peak_force.png"
    plt.figure(figsize=(6.6, 4.0))
    names = ["delayed_force", "delay_scaled_cautious", "contact_age_invariant"]
    labels = {
        "delayed_force": "Delayed force feedback",
        "delay_scaled_cautious": "Delay-scaled cautious",
        "contact_age_invariant": "Contact-age invariant",
    }
    for name in names:
        xs: list[float] = []
        means: list[float] = []
        cis: list[float] = []
        latencies = sorted(
            {
                float(row["configured_latency_s"])
                for row in rows
                if row["controller"] == name
            }
        )
        for latency in latencies:
            vals = np.array(
                [
                    float(row["peak_force_n"])
                    for row in rows
                    if row["controller"] == name
                    and abs(float(row["configured_latency_s"]) - latency) < 1e-9
                ]
            )
            xs.append(1000.0 * latency)
            means.append(float(np.mean(vals)))
            ci = 1.96 * float(np.std(vals, ddof=1)) / float(np.sqrt(len(vals))) if len(vals) > 1 else 0.0
            cis.append(ci)
        plt.errorbar(xs, means, yerr=cis, marker="o", linewidth=2, capsize=3, label=labels[name])
    plt.axhline(8.0, color="black", linestyle="--", linewidth=1, label="Target force")
    plt.xlabel("Configured sensing latency (ms)")
    plt.ylabel("Mean peak force over 30 seeds (N)")
    plt.title("Seeded stress test with model and latency perturbations")
    plt.grid(True, alpha=0.25)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def plot_trajectories() -> Path:
    path = FIGURES / "force_trajectories_80ms.png"
    latency = 0.08
    controllers = [
        DelayedForceController(),
        CautiousDelayedController(latency),
        ContactAgeInvariantController(),
    ]
    labels = {
        "delayed_force": "Delayed force feedback",
        "delay_scaled_cautious": "Delay-scaled cautious",
        "contact_age_invariant": "Contact-age invariant",
    }
    plt.figure(figsize=(6.4, 3.8))
    for controller in controllers:
        result = simulate(controller, latency, PlantParams(), ControlParams())
        plt.plot(1000.0 * result.time, result.force, linewidth=2, label=labels[controller.name])
    plt.axhline(8.0, color="black", linestyle="--", linewidth=1, label="Target force")
    plt.xlim(120, 520)
    plt.xlabel("Time (ms)")
    plt.ylabel("Contact force (N)")
    plt.title("Force transient with 80 ms contact sensing latency")
    plt.grid(True, alpha=0.25)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def plot_mismatch(rows: list[dict[str, float | str]]) -> Path:
    path = FIGURES / "stiffness_mismatch_ablation.png"
    plt.figure(figsize=(6.4, 3.8))
    for k_scale in sorted({float(row["k_hat_scale"]) for row in rows}):
        items = [row for row in rows if abs(float(row["k_hat_scale"]) - k_scale) < 1e-9]
        xs = [1000.0 * float(row["latency_s"]) for row in items]
        ys = [float(row["peak_force_n"]) for row in items]
        plt.plot(xs, ys, marker="o", linewidth=1.8, label=f"k_hat/k={k_scale:.2f}")
    plt.axhline(8.0, color="black", linestyle="--", linewidth=1)
    plt.xlabel("Force/tactile sensing latency (ms)")
    plt.ylabel("Peak force (N)")
    plt.title("Model mismatch weakens but does not erase timing benefit")
    plt.grid(True, alpha=0.25)
    plt.legend(frameon=False, ncol=2)
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def copy_for_paper(paths: list[Path]) -> None:
    for path in paths:
        shutil.copy2(path, PAPER_FIGURES / path.name)


def main() -> int:
    ensure_dirs()
    rows, summary = run_main_sweep()
    mismatch = run_mismatch_ablation()
    stress_rows, stress_summary = run_seeded_stress()
    write_csv(RESULTS / "latency_sweep.csv", rows)
    write_csv(RESULTS / "stiffness_mismatch.csv", mismatch)
    write_csv(RESULTS / "seeded_stress.csv", stress_rows)
    with (RESULTS / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    with (RESULTS / "stress_summary.json").open("w", encoding="utf-8") as f:
        json.dump(stress_summary, f, indent=2, sort_keys=True)
    fig_paths = [
        plot_peak(rows),
        plot_ablation(rows),
        plot_stress(stress_rows),
        plot_trajectories(),
        plot_mismatch(mismatch),
    ]
    copy_for_paper(fig_paths)
    print(f"wrote={RESULTS / 'latency_sweep.csv'}")
    print(f"wrote={RESULTS / 'summary.json'}")
    print(f"wrote={RESULTS / 'seeded_stress.csv'}")
    print(f"wrote={RESULTS / 'stress_summary.json'}")
    for fig in fig_paths:
        print(f"figure={fig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
