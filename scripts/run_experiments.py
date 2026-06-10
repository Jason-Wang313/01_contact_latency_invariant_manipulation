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
    ContactAgeInvariantController,
    ControlParams,
    DelayedForceController,
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


def run_main_sweep() -> tuple[list[dict[str, float | str]], dict[str, dict[str, float]]]:
    latencies = np.array([0.0, 0.005, 0.010, 0.020, 0.040, 0.060, 0.080, 0.100, 0.125, 0.150])
    rows: list[dict[str, float | str]] = []
    grouped: dict[str, list[dict[str, float | str]]] = {}
    for latency in latencies:
        controllers = [
            DelayedForceController(),
            CautiousDelayedController(float(latency)),
            ContactAgeInvariantController(),
        ]
        for controller in controllers:
            result = simulate(controller, float(latency), PlantParams(), ControlParams())
            metrics = result.metrics()
            rows.append(metrics)
            grouped.setdefault(str(metrics["controller"]), []).append(metrics)

    summary: dict[str, dict[str, float]] = {}
    for name, items in grouped.items():
        xs = np.array([float(item["latency_s"]) for item in items])
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
    return rows, summary


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
    write_csv(RESULTS / "latency_sweep.csv", rows)
    write_csv(RESULTS / "stiffness_mismatch.csv", mismatch)
    with (RESULTS / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    fig_paths = [plot_peak(rows), plot_trajectories(), plot_mismatch(mismatch)]
    copy_for_paper(fig_paths)
    print(f"wrote={RESULTS / 'latency_sweep.csv'}")
    print(f"wrote={RESULTS / 'summary.json'}")
    for fig in fig_paths:
        print(f"figure={fig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
