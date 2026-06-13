#!/usr/bin/env python3
"""Full-scale, RAM-light experiment suite for Paper 01.

This script deliberately streams compact per-run metrics to disk. Full
trajectories are retained only for a small set of named examples used in figures.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.contact_latency import ControlParams, PlantParams, contact_force  # noqa: E402


RESULTS = ROOT / "results" / "full_scale"
FIGURES = RESULTS / "figures"
PAPER_FIGURES = ROOT / "paper" / "figures"
PAPER_TABLES = ROOT / "paper" / "tables"


@dataclass(frozen=True)
class RunConfig:
    suite: str
    controller: str
    latency_s: float
    profile: str = "nominal"
    seed: int = 0
    estimator: str = "perfect_guard"
    k_hat_scale: float = 1.0
    c_hat_scale: float = 1.0
    stiffness_scale: float = 1.0
    damping_scale: float = 1.0
    servo_scale: float = 1.0
    gap_scale: float = 1.0
    force_gain_scale: float = 1.0
    ramp_rate_scale: float = 1.0
    event_bias_s: float = 0.0
    event_jitter_s: float = 0.0
    event_drop_prob: float = 0.0
    false_early_m: float = 0.0
    tune: str = ""
    save_trajectory: bool = False


class OnlineController:
    name = "controller"

    def reset(self, cfg: RunConfig, plant: PlantParams, control: ControlParams) -> None:
        self.cfg = cfg
        self.plant = plant
        self.control = control
        self.contact_time: float | None = None
        self.filtered_force = 0.0
        self.k_hat = plant.stiffness * cfg.k_hat_scale
        self.c_hat = plant.damping * cfg.c_hat_scale
        self.rng = np.random.default_rng(cfg.seed + 1009)
        self.dropped_event = bool(self.rng.random() < cfg.event_drop_prob)

    def maybe_contact_time(
        self,
        t: float,
        q: float,
        delayed_force: float,
        latency: float,
    ) -> float | None:
        if self.contact_time is not None:
            return self.contact_time
        mode = self.cfg.estimator
        if mode == "perfect_guard" and q > 0.0:
            self.contact_time = t
        elif mode == "delayed_force_edge" and delayed_force > 0.05:
            self.contact_time = max(0.0, t - latency)
        elif mode == "noisy_guard" and q > 0.0 and not self.dropped_event:
            self.contact_time = t + self.cfg.event_bias_s + float(self.rng.normal(0.0, self.cfg.event_jitter_s))
        elif mode == "geometry_prior" and q > self.cfg.false_early_m:
            self.contact_time = t
        elif mode == "wrong_early" and q > -0.006:
            self.contact_time = t
        return self.contact_time

    def command(
        self,
        t: float,
        q: float,
        v: float,
        delayed_q: float,
        delayed_v: float,
        delayed_force: float,
        latency: float,
    ) -> tuple[float, float, float, float]:
        raise NotImplementedError

    def estimate_force(self, q: float, v: float, delayed_q: float, delayed_v: float, delayed_force: float) -> float:
        if q <= 0.0:
            return 0.0
        if delayed_q > 0.0:
            pred = delayed_force + self.k_hat * (q - delayed_q) + self.c_hat * (v - delayed_v)
        else:
            pred = self.k_hat * q + self.c_hat * v
        return max(0.0, float(pred))

    def clip(self, u: float) -> float:
        return float(np.clip(u, -self.control.max_velocity, self.control.max_velocity))


class DelayedFeedback(OnlineController):
    name = "delayed_force"

    def command(self, t, q, v, delayed_q, delayed_v, delayed_force, latency):
        target = self.control.desired_force
        u = self.control.force_gain * self.cfg.force_gain_scale * (target - delayed_force)
        if delayed_force < 0.05 and q < 0.002:
            u = max(u, self.control.approach_velocity)
        return self.clip(u), delayed_force, target, 0.0


class CautiousFeedback(OnlineController):
    name = "tuned_cautious"

    def command(self, t, q, v, delayed_q, delayed_v, delayed_force, latency):
        gain = float(self.cfg.tune or 18.0)
        safe_approach = self.control.approach_velocity / (1.0 + gain * latency)
        target = self.control.desired_force
        u = self.control.force_gain * self.cfg.force_gain_scale * (target - delayed_force)
        if delayed_force < 0.05:
            u = safe_approach
        return self.clip(u), delayed_force, target, 0.0


class LowPassDelayed(OnlineController):
    name = "low_pass_delayed"

    def command(self, t, q, v, delayed_q, delayed_v, delayed_force, latency):
        alpha = float(self.cfg.tune or 0.35)
        self.filtered_force = alpha * delayed_force + (1.0 - alpha) * self.filtered_force
        target = self.control.desired_force
        u = self.control.force_gain * self.cfg.force_gain_scale * (target - self.filtered_force)
        if self.filtered_force < 0.05 and q < 0.002:
            u = max(u, self.control.approach_velocity / (1.0 + 8.0 * latency))
        return self.clip(u), self.filtered_force, target, 0.0


class GainScheduledDelayed(OnlineController):
    name = "latency_gain_schedule"

    def command(self, t, q, v, delayed_q, delayed_v, delayed_force, latency):
        gamma = float(self.cfg.tune or 9.0)
        target = self.control.desired_force
        gain = self.control.force_gain / (1.0 + gamma * latency)
        approach = self.control.approach_velocity / math.sqrt(1.0 + gamma * latency)
        u = gain * (target - delayed_force)
        if delayed_force < 0.05:
            u = approach
        return self.clip(u), delayed_force, target, 0.0


class SmithPredictor(OnlineController):
    name = "smith_predictor"

    def command(self, t, q, v, delayed_q, delayed_v, delayed_force, latency):
        self.maybe_contact_time(t, q, delayed_force, latency)
        if self.contact_time is None:
            return self.control.approach_velocity, 0.0, 0.0, 0.0
        pred = self.estimate_force(q, v, delayed_q, delayed_v, delayed_force)
        target = self.control.desired_force
        u = self.control.force_gain * self.cfg.force_gain_scale * (target - pred)
        return self.clip(u), pred, target, max(0.0, t - self.contact_time)


class ContactAgeInvariant(OnlineController):
    name = "contact_age_invariant"

    def command(self, t, q, v, delayed_q, delayed_v, delayed_force, latency):
        self.maybe_contact_time(t, q, delayed_force, latency)
        if self.contact_time is None:
            return self.control.approach_velocity, 0.0, 0.0, 0.0
        pred = self.estimate_force(q, v, delayed_q, delayed_v, delayed_force)
        age = max(0.0, t - self.contact_time)
        target = min(self.control.desired_force, self.control.ramp_rate * self.cfg.ramp_rate_scale * age)
        u = self.control.force_gain * self.cfg.force_gain_scale * (target - pred)
        return self.clip(u), pred, target, age


class WrongEventContactAge(ContactAgeInvariant):
    name = "wrong_event_control"

    def reset(self, cfg: RunConfig, plant: PlantParams, control: ControlParams) -> None:
        cfg = RunConfig(**{**cfg.__dict__, "estimator": "wrong_early"})
        super().reset(cfg, plant, control)


class OneStepMPC(OnlineController):
    name = "one_step_mpc"

    def command(self, t, q, v, delayed_q, delayed_v, delayed_force, latency):
        self.maybe_contact_time(t, q, delayed_force, latency)
        if self.contact_time is None:
            return self.control.approach_velocity, 0.0, 0.0, 0.0
        pred = self.estimate_force(q, v, delayed_q, delayed_v, delayed_force)
        target = self.control.desired_force
        best_u = 0.0
        best_cost = float("inf")
        for u in np.linspace(-self.control.max_velocity, self.control.max_velocity, 17):
            v_next = v + (float(u) - v) / self.plant.servo_tau * self.plant.dt
            q_next = q + v_next * self.plant.dt
            f_next = max(0.0, self.k_hat * q_next + self.c_hat * v_next)
            cost = (f_next - target) ** 2 + 0.015 * float(u) ** 2
            if cost < best_cost:
                best_cost = cost
                best_u = float(u)
        return self.clip(best_u), pred, target, max(0.0, t - self.contact_time)


class AdaptiveWindowedAdvance(ContactAgeInvariant):
    name = "adaptive_windowed_advance"

    def command(self, t, q, v, delayed_q, delayed_v, delayed_force, latency):
        if delayed_q > 1e-4 and delayed_force > 0.05:
            implied_k = max(100.0, (delayed_force - self.c_hat * delayed_v) / delayed_q)
            self.k_hat = 0.98 * self.k_hat + 0.02 * float(np.clip(implied_k, 200.0, 9000.0))
        return super().command(t, q, v, delayed_q, delayed_v, delayed_force, latency)


CONTROLLERS: dict[str, type[OnlineController]] = {
    cls.name: cls
    for cls in [
        DelayedFeedback,
        CautiousFeedback,
        LowPassDelayed,
        GainScheduledDelayed,
        SmithPredictor,
        ContactAgeInvariant,
        WrongEventContactAge,
        OneStepMPC,
        AdaptiveWindowedAdvance,
    ]
}


def profile_force(q: float, v: float, plant: PlantParams, profile: str) -> float:
    if q <= 0.0:
        return 0.0
    k = plant.stiffness
    c = plant.damping
    if profile == "nominal":
        return contact_force(q, v, plant)
    if profile == "soft_to_hard":
        threshold = 0.0035
        k1, k2 = 0.45 * k, 1.75 * k
        elastic = k1 * min(q, threshold) + k2 * max(0.0, q - threshold)
        return max(0.0, elastic + c * v)
    if profile == "hard_to_soft":
        threshold = 0.0035
        k1, k2 = 1.55 * k, 0.50 * k
        elastic = k1 * min(q, threshold) + k2 * max(0.0, q - threshold)
        return max(0.0, elastic + c * v)
    if profile == "deadband":
        deadband = 0.0018
        return max(0.0, k * max(0.0, q - deadband) + c * v)
    if profile == "force_cap":
        return min(11.0, contact_force(q, v, plant))
    raise ValueError(f"unknown profile: {profile}")


def make_plant(cfg: RunConfig) -> PlantParams:
    base = PlantParams()
    return PlantParams(
        dt=base.dt,
        horizon=base.horizon,
        servo_tau=base.servo_tau * cfg.servo_scale,
        stiffness=base.stiffness * cfg.stiffness_scale,
        damping=base.damping * cfg.damping_scale,
        initial_gap=base.initial_gap * cfg.gap_scale,
        max_velocity=base.max_velocity,
    )


def simulate_metrics(cfg: RunConfig) -> dict[str, float | int | str]:
    plant = make_plant(cfg)
    control = ControlParams(
        force_gain=ControlParams().force_gain * cfg.force_gain_scale,
        ramp_rate=ControlParams().ramp_rate * cfg.ramp_rate_scale,
        k_hat_scale=cfg.k_hat_scale,
        c_hat_scale=cfg.c_hat_scale,
    )
    controller = CONTROLLERS[cfg.controller]()
    controller.reset(cfg, plant, control)

    n = int(plant.horizon / plant.dt) + 1
    delay_steps = max(0, int(round(cfg.latency_s / plant.dt)))
    q_hist = np.zeros(n, dtype=np.float64)
    v_hist = np.zeros(n, dtype=np.float64)
    f_hist = np.zeros(n, dtype=np.float64)
    pred_hist = np.zeros(n, dtype=np.float64) if cfg.save_trajectory else np.zeros(1)
    target_hist = np.zeros(n, dtype=np.float64) if cfg.save_trajectory else np.zeros(1)
    command_hist = np.zeros(n, dtype=np.float64) if cfg.save_trajectory else np.zeros(1)

    q_hist[0] = -plant.initial_gap
    peak = 0.0
    impulse_250 = 0.0
    high_dwell = 0.0
    contact_idx: int | None = None
    settle_idx: int | None = None
    target = control.desired_force

    for i in range(1, n):
        t_prev = (i - 1) * plant.dt
        j = max(0, i - delay_steps - 1)
        q = float(q_hist[i - 1])
        v = float(v_hist[i - 1])
        delayed_q = float(q_hist[j])
        delayed_v = float(v_hist[j])
        delayed_force = float(f_hist[j])
        u, pred, tgt, _age = controller.command(t_prev, q, v, delayed_q, delayed_v, delayed_force, cfg.latency_s)
        v_new = v + (u - v) / plant.servo_tau * plant.dt
        v_new = float(np.clip(v_new, -plant.max_velocity, plant.max_velocity))
        q_new = q + v_new * plant.dt
        f_new = profile_force(q_new, v_new, plant, cfg.profile)
        q_hist[i] = q_new
        v_hist[i] = v_new
        f_hist[i] = f_new
        if cfg.save_trajectory:
            pred_hist[i] = pred
            target_hist[i] = tgt
            command_hist[i] = u
        if f_new > 0.05 and contact_idx is None:
            contact_idx = i
        if contact_idx is not None:
            peak = max(peak, f_new)
            if i - contact_idx < int(0.25 / plant.dt):
                impulse_250 += f_new * plant.dt
            if f_new > 12.0:
                high_dwell += plant.dt
            if settle_idx is None and abs(f_new - target) <= 0.5:
                window = f_hist[max(contact_idx, i - int(0.015 / plant.dt)) : i + 1]
                if len(window) and float(np.max(np.abs(window - target))) <= 0.75:
                    settle_idx = i

    final_force = float(f_hist[-1])
    row: dict[str, float | int | str] = {
        **cfg.__dict__,
        "peak_force_n": float(peak),
        "overshoot_n": float(max(0.0, peak - target)),
        "impulse_250ms_ns": float(impulse_250),
        "high_force_dwell_s": float(high_dwell),
        "final_force_error_n": float(abs(final_force - target)),
        "settling_time_s": float((settle_idx - contact_idx) * plant.dt) if settle_idx is not None and contact_idx is not None else -1.0,
        "contact_made": int(contact_idx is not None),
    }
    if cfg.save_trajectory:
        traj_path = RESULTS / f"trajectory_{cfg.suite}_{cfg.controller}_{cfg.profile}_{int(cfg.latency_s * 1000):03d}ms.csv"
        with traj_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time_s", "q_m", "v_mps", "force_n", "predicted_force_n", "target_force_n", "command_mps"])
            for i in range(n):
                writer.writerow([i * plant.dt, q_hist[i], v_hist[i], f_hist[i], pred_hist[i], target_hist[i], command_hist[i]])
        row["trajectory_csv"] = str(traj_path.relative_to(ROOT))
    return row


def ensure_dirs() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)
    PAPER_TABLES.mkdir(parents=True, exist_ok=True)


class StreamingCsv:
    def __init__(self, path: Path, fieldnames: list[str]) -> None:
        self.path = path
        self.fieldnames = fieldnames
        self.f = path.open("w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.f, fieldnames=fieldnames, extrasaction="ignore")
        self.writer.writeheader()
        self.count = 0

    def write(self, row: dict[str, float | int | str]) -> None:
        self.writer.writerow(row)
        self.count += 1
        if self.count % 500 == 0:
            self.f.flush()

    def close(self) -> None:
        self.f.flush()
        self.f.close()


FIELDS = list(RunConfig.__dataclass_fields__.keys()) + [
    "peak_force_n",
    "overshoot_n",
    "impulse_250ms_ns",
    "high_force_dwell_s",
    "final_force_error_n",
    "settling_time_s",
    "contact_made",
    "trajectory_csv",
]


def run_suite(path: Path, configs: Iterable[RunConfig]) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    writer = StreamingCsv(path, FIELDS)
    try:
        for cfg in configs:
            row = simulate_metrics(cfg)
            writer.write(row)
            rows.append(row)
    finally:
        writer.close()
    return rows


def tune_baselines() -> dict[str, str]:
    candidates: dict[str, list[str]] = {
        "tuned_cautious": ["4", "8", "12", "18", "28", "40"],
        "low_pass_delayed": ["0.15", "0.25", "0.35", "0.50", "0.70"],
        "latency_gain_schedule": ["4", "8", "12", "18", "28"],
    }
    rows: list[dict[str, float | int | str]] = []
    train_latencies = [0.0, 0.03, 0.06, 0.10, 0.15, 0.20]
    train_profiles = ["nominal", "soft_to_hard", "deadband"]
    for controller, values in candidates.items():
        for value in values:
            for latency in train_latencies:
                for profile in train_profiles:
                    cfg = RunConfig(
                        suite="tuning",
                        controller=controller,
                        latency_s=latency,
                        profile=profile,
                        tune=value,
                    )
                    row = simulate_metrics(cfg)
                    rows.append(row)
    path = RESULTS / "tuning_grid.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    best: dict[str, str] = {}
    for controller, values in candidates.items():
        scores: list[tuple[float, str]] = []
        for value in values:
            subset = [r for r in rows if r["controller"] == controller and r["tune"] == value]
            score = float(np.mean([float(r["peak_force_n"]) + 0.25 * float(r["final_force_error_n"]) for r in subset]))
            scores.append((score, value))
        best[controller] = min(scores)[1]
    return best


def make_nominal_configs(best: dict[str, str]) -> list[RunConfig]:
    configs: list[RunConfig] = []
    controllers = [
        "delayed_force",
        "tuned_cautious",
        "low_pass_delayed",
        "latency_gain_schedule",
        "smith_predictor",
        "one_step_mpc",
        "adaptive_windowed_advance",
        "contact_age_invariant",
    ]
    for latency in np.linspace(0.0, 0.25, 14):
        for controller in controllers:
            configs.append(
                RunConfig(
                    suite="nominal_latency",
                    controller=controller,
                    latency_s=float(latency),
                    tune=best.get(controller, ""),
                    save_trajectory=controller in {"delayed_force", "tuned_cautious", "smith_predictor", "contact_age_invariant"}
                    and abs(float(latency) - 0.12) < 1e-9,
                )
            )
    return configs


def make_event_configs(best: dict[str, str]) -> list[RunConfig]:
    configs: list[RunConfig] = []
    estimators = [
        ("perfect_guard", 0.0, 0.0, 0.0, 0.0),
        ("delayed_force_edge", 0.0, 0.0, 0.0, 0.0),
        ("noisy_guard", 0.0, 0.002, 0.0, 0.0),
        ("noisy_guard", 0.008, 0.004, 0.0, 0.0),
        ("noisy_guard", -0.006, 0.004, 0.0, 0.0),
        ("noisy_guard", 0.0, 0.004, 0.20, 0.0),
        ("geometry_prior", 0.0, 0.0, 0.0, -0.002),
        ("geometry_prior", 0.0, 0.0, 0.0, 0.002),
    ]
    for seed in range(60):
        for latency in [0.04, 0.08, 0.12, 0.18]:
            for estimator, bias, jitter, drop, false_early in estimators:
                configs.append(
                    RunConfig(
                        suite="event_estimation",
                        controller="contact_age_invariant",
                        latency_s=latency,
                        seed=seed,
                        estimator=estimator,
                        event_bias_s=bias,
                        event_jitter_s=jitter,
                        event_drop_prob=drop,
                        false_early_m=false_early,
                    )
                )
    return configs


def make_mismatch_configs() -> list[RunConfig]:
    configs: list[RunConfig] = []
    for latency in [0.04, 0.08, 0.12, 0.18, 0.25]:
        for k_hat in [0.55, 0.70, 0.85, 1.0, 1.15, 1.35, 1.60]:
            for c_hat in [0.50, 0.75, 1.0, 1.40]:
                for controller in ["smith_predictor", "adaptive_windowed_advance", "contact_age_invariant"]:
                    configs.append(
                        RunConfig(
                            suite="model_mismatch",
                            controller=controller,
                            latency_s=latency,
                            k_hat_scale=k_hat,
                            c_hat_scale=c_hat,
                        )
                    )
    return configs


def make_mode_configs(best: dict[str, str]) -> list[RunConfig]:
    configs: list[RunConfig] = []
    profiles = ["nominal", "soft_to_hard", "hard_to_soft", "deadband", "force_cap"]
    controllers = ["delayed_force", "tuned_cautious", "smith_predictor", "adaptive_windowed_advance", "contact_age_invariant", "wrong_event_control"]
    for seed in range(30):
        for profile in profiles:
            for latency in [0.04, 0.08, 0.12, 0.18]:
                for controller in controllers:
                    rng = np.random.default_rng(seed)
                    configs.append(
                        RunConfig(
                            suite="mode_switch",
                            controller=controller,
                            latency_s=latency,
                            profile=profile,
                            seed=seed,
                            tune=best.get(controller, ""),
                            stiffness_scale=float(np.clip(rng.normal(1.0, 0.10), 0.75, 1.30)),
                            damping_scale=float(np.clip(rng.normal(1.0, 0.20), 0.55, 1.60)),
                            servo_scale=float(np.clip(rng.normal(1.0, 0.15), 0.65, 1.45)),
                        )
                    )
    return configs


def make_large_stress_configs(best: dict[str, str]) -> list[RunConfig]:
    configs: list[RunConfig] = []
    controllers = ["delayed_force", "tuned_cautious", "smith_predictor", "one_step_mpc", "adaptive_windowed_advance", "contact_age_invariant"]
    profiles = ["nominal", "soft_to_hard", "deadband"]
    for seed in range(180):
        rng = np.random.default_rng(seed + 2026)
        profile = profiles[seed % len(profiles)]
        stiffness_scale = float(np.clip(rng.lognormal(mean=0.0, sigma=0.22), 0.55, 1.75))
        damping_scale = float(np.clip(rng.lognormal(mean=0.0, sigma=0.30), 0.40, 2.00))
        servo_scale = float(np.clip(rng.lognormal(mean=0.0, sigma=0.22), 0.55, 1.65))
        gap_scale = float(np.clip(rng.lognormal(mean=0.0, sigma=0.18), 0.60, 1.60))
        k_hat_scale = float(np.clip(rng.normal(1.0, 0.18), 0.55, 1.60))
        c_hat_scale = float(np.clip(rng.normal(1.0, 0.25), 0.45, 1.85))
        for latency in [0.0, 0.04, 0.08, 0.12, 0.18, 0.25]:
            effective_latency = max(0.0, float(latency + rng.normal(0.0, 0.004)))
            for controller in controllers:
                configs.append(
                    RunConfig(
                        suite="large_seed_stress",
                        controller=controller,
                        latency_s=effective_latency,
                        profile=profile,
                        seed=seed,
                        tune=best.get(controller, ""),
                        k_hat_scale=k_hat_scale,
                        c_hat_scale=c_hat_scale,
                        stiffness_scale=stiffness_scale,
                        damping_scale=damping_scale,
                        servo_scale=servo_scale,
                        gap_scale=gap_scale,
                        event_jitter_s=0.002,
                    )
                )
    return configs


def make_negative_control_configs() -> list[RunConfig]:
    configs: list[RunConfig] = []
    for latency in [0.0, 0.08, 0.18]:
        for controller in ["delayed_force", "smith_predictor", "contact_age_invariant", "wrong_event_control"]:
            configs.append(RunConfig(suite="negative_controls", controller=controller, latency_s=latency))
    return configs


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_leaderboard(paths: list[Path]) -> list[dict[str, float | str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        rows.extend(load_csv(path))
    out: list[dict[str, float | str]] = []
    for suite in sorted({r["suite"] for r in rows}):
        for controller in sorted({r["controller"] for r in rows if r["suite"] == suite}):
            subset = [r for r in rows if r["suite"] == suite and r["controller"] == controller]
            peaks = np.array([float(r["peak_force_n"]) for r in subset])
            impulses = np.array([float(r["impulse_250ms_ns"]) for r in subset])
            final = np.array([float(r["final_force_error_n"]) for r in subset])
            contact = np.array([int(float(r["contact_made"])) for r in subset])
            unsafe = peaks > 12.0
            missed = contact < 1
            out.append(
                {
                    "suite": suite,
                    "controller": controller,
                    "n": float(len(subset)),
                    "mean_peak_force_n": float(np.mean(peaks)),
                    "p90_peak_force_n": float(np.percentile(peaks, 90)),
                    "p95_peak_force_n": float(np.percentile(peaks, 95)),
                    "max_peak_force_n": float(np.max(peaks)),
                    "failure_rate_peak_gt_12n": float(np.mean(unsafe)),
                    "no_contact_rate": float(np.mean(missed)),
                    "unsafe_or_no_contact_rate": float(np.mean(np.logical_or(unsafe, missed))),
                    "mean_impulse_250ms_ns": float(np.mean(impulses)),
                    "mean_final_error_n": float(np.mean(final)),
                }
            )
    path = RESULTS / "leaderboard.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        writer.writeheader()
        writer.writerows(out)
    return out


def plot_nominal(rows: list[dict[str, str]]) -> Path:
    path = FIGURES / "full_scale_latency_baselines.png"
    plt.figure(figsize=(7.0, 4.4))
    order = ["delayed_force", "tuned_cautious", "latency_gain_schedule", "smith_predictor", "one_step_mpc", "adaptive_windowed_advance", "contact_age_invariant"]
    for controller in order:
        subset = [r for r in rows if r["controller"] == controller]
        if not subset:
            continue
        subset = sorted(subset, key=lambda r: float(r["latency_s"]))
        xs = [1000.0 * float(r["latency_s"]) for r in subset]
        ys = [float(r["peak_force_n"]) if int(float(r["contact_made"])) else np.nan for r in subset]
        plt.plot(xs, ys, marker="o", linewidth=1.8, label=controller.replace("_", " "))
        miss_x = [1000.0 * float(r["latency_s"]) for r in subset if not int(float(r["contact_made"]))]
        if miss_x:
            plt.scatter(miss_x, [0.0] * len(miss_x), marker="x", color="black", s=35, zorder=4)
    plt.axhline(8.0, color="black", linestyle="--", linewidth=1, label="target")
    plt.axhline(12.0, color="firebrick", linestyle=":", linewidth=1, label="12 N stress threshold")
    plt.xlabel("configured sensing latency (ms)")
    plt.ylabel("peak contact force (N)")
    plt.title("Held-out latency grid with tuned and predictive baselines")
    plt.grid(True, alpha=0.25)
    plt.legend(frameon=False, fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def plot_event(rows: list[dict[str, str]]) -> Path:
    path = FIGURES / "event_estimator_sensitivity.png"
    labels = sorted({(r["estimator"], r["event_bias_s"], r["event_jitter_s"], r["event_drop_prob"], r["false_early_m"]) for r in rows})
    names: list[str] = []
    means: list[float] = []
    fails: list[float] = []
    for label in labels:
        subset = [
            r
            for r in rows
            if (r["estimator"], r["event_bias_s"], r["event_jitter_s"], r["event_drop_prob"], r["false_early_m"]) == label
        ]
        name = label[0]
        if float(label[1]) != 0:
            name += f" bias={float(label[1])*1000:.0f}ms"
        if float(label[2]) != 0:
            name += f" jitter={float(label[2])*1000:.0f}ms"
        if float(label[3]) != 0:
            name += f" drop={float(label[3]):.1f}"
        if float(label[4]) != 0:
            name += f" q0={float(label[4])*1000:.1f}mm"
        names.append(name)
        peaks = np.array([float(r["peak_force_n"]) for r in subset])
        means.append(float(np.mean(peaks)))
        fails.append(float(np.mean(peaks > 12.0)))
    x = np.arange(len(names))
    fig, ax1 = plt.subplots(figsize=(8.6, 4.5))
    ax1.bar(x - 0.2, means, width=0.4, label="mean peak force")
    ax1.axhline(12.0, color="firebrick", linestyle=":", linewidth=1)
    ax1.set_ylabel("mean peak force (N)")
    ax2 = ax1.twinx()
    ax2.bar(x + 0.2, fails, width=0.4, color="tab:orange", label="failure rate")
    ax2.set_ylabel("failure rate peak > 12 N")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax1.set_title("Contact-event timing is the main non-ideal bottleneck")
    ax1.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path


def plot_mode(rows: list[dict[str, str]]) -> Path:
    path = FIGURES / "mode_switch_failure_map.png"
    profiles = sorted({r["profile"] for r in rows})
    controllers = ["delayed_force", "tuned_cautious", "smith_predictor", "adaptive_windowed_advance", "contact_age_invariant", "wrong_event_control"]
    mat = np.zeros((len(controllers), len(profiles)))
    for i, controller in enumerate(controllers):
        for j, profile in enumerate(profiles):
            subset = [r for r in rows if r["controller"] == controller and r["profile"] == profile]
            mat[i, j] = np.mean([float(r["peak_force_n"]) > 12.0 for r in subset]) if subset else np.nan
    plt.figure(figsize=(7.2, 3.8))
    im = plt.imshow(mat, cmap="magma", vmin=0.0, vmax=1.0, aspect="auto")
    plt.colorbar(im, label="failure rate peak > 12 N")
    plt.yticks(np.arange(len(controllers)), [c.replace("_", " ") for c in controllers], fontsize=8)
    plt.xticks(np.arange(len(profiles)), [p.replace("_", " ") for p in profiles], rotation=20, ha="right")
    plt.title("Mode and contact-profile shifts expose the boundary")
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def plot_stress(rows: list[dict[str, str]]) -> Path:
    path = FIGURES / "large_seed_stress_distribution.png"
    controllers = ["delayed_force", "tuned_cautious", "smith_predictor", "one_step_mpc", "adaptive_windowed_advance", "contact_age_invariant"]
    data = [[float(r["peak_force_n"]) for r in rows if r["controller"] == c] for c in controllers]
    plt.figure(figsize=(7.2, 4.2))
    plt.boxplot(data, tick_labels=[c.replace("_", "\n") for c in controllers], showfliers=False)
    plt.axhline(8.0, color="black", linestyle="--", linewidth=1)
    plt.axhline(12.0, color="firebrick", linestyle=":", linewidth=1)
    plt.ylabel("peak contact force (N)")
    plt.title("Large sequential stress suite: distribution over seeds and profiles")
    plt.grid(True, axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def plot_mismatch(rows: list[dict[str, str]]) -> Path:
    path = FIGURES / "model_mismatch_surface.png"
    subset = [r for r in rows if r["controller"] == "contact_age_invariant" and abs(float(r["latency_s"]) - 0.18) < 1e-9]
    k_vals = sorted({float(r["k_hat_scale"]) for r in subset})
    c_vals = sorted({float(r["c_hat_scale"]) for r in subset})
    mat = np.zeros((len(c_vals), len(k_vals)))
    for i, c in enumerate(c_vals):
        for j, k in enumerate(k_vals):
            cell = [r for r in subset if abs(float(r["k_hat_scale"]) - k) < 1e-9 and abs(float(r["c_hat_scale"]) - c) < 1e-9]
            mat[i, j] = float(cell[0]["peak_force_n"]) if cell else np.nan
    plt.figure(figsize=(6.4, 3.9))
    im = plt.imshow(mat, cmap="viridis", aspect="auto", origin="lower")
    plt.colorbar(im, label="peak force (N)")
    plt.xticks(np.arange(len(k_vals)), [f"{k:.2f}" for k in k_vals])
    plt.yticks(np.arange(len(c_vals)), [f"{c:.2f}" for c in c_vals])
    plt.xlabel("stiffness estimate scale")
    plt.ylabel("damping estimate scale")
    plt.title("Model-estimate sensitivity at 180 ms latency")
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def latex_escape(value: str) -> str:
    return value.replace("_", " ")


def event_condition_label(label: tuple[str, str, str, str, str]) -> str:
    name = latex_escape(label[0])
    bias = float(label[1])
    jitter = float(label[2])
    drop = float(label[3])
    false_early = float(label[4])
    parts = [name]
    if bias:
        parts.append(f"bias {bias * 1000:.0f} ms")
    if jitter:
        parts.append(f"jitter {jitter * 1000:.0f} ms")
    if drop:
        parts.append(f"drop {drop:.1f}")
    if false_early:
        direction = "early" if false_early < 0.0 else "late"
        parts.append(f"{direction} {abs(false_early) * 1000:.1f} mm")
    return ", ".join(parts)


def metrics(rows: list[dict[str, str]]) -> dict[str, float]:
    peaks = np.array([float(r["peak_force_n"]) for r in rows])
    final = np.array([float(r["final_force_error_n"]) for r in rows])
    contact = np.array([int(float(r["contact_made"])) for r in rows])
    unsafe = peaks > 12.0
    missed = contact < 1
    return {
        "n": float(len(rows)),
        "mean": float(np.mean(peaks)),
        "p50": float(np.percentile(peaks, 50)),
        "p90": float(np.percentile(peaks, 90)),
        "p95": float(np.percentile(peaks, 95)),
        "max": float(np.max(peaks)),
        "unsafe": float(np.mean(unsafe)),
        "unsafe_miss": float(np.mean(np.logical_or(unsafe, missed))),
        "final": float(np.mean(final)),
    }


def write_secondary_tables(
    stress_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
    mode_rows: list[dict[str, str]],
    mismatch_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
) -> None:
    controllers = [
        "delayed_force",
        "tuned_cautious",
        "smith_predictor",
        "one_step_mpc",
        "adaptive_windowed_advance",
        "contact_age_invariant",
    ]
    with (PAPER_TABLES / "stress_quantiles.tex").open("w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{lrrrrrr}\\toprule\n")
        f.write("Controller & P50 & P90 & P95 & Max & Unsafe/miss & Final err.\\\\\n")
        f.write("\\midrule\n")
        for controller in controllers:
            row_metrics = metrics([r for r in stress_rows if r["controller"] == controller])
            f.write(
                f"{latex_escape(controller)} & {row_metrics['p50']:.2f} & {row_metrics['p90']:.2f} & "
                f"{row_metrics['p95']:.2f} & {row_metrics['max']:.2f} & "
                f"{100.0 * row_metrics['unsafe_miss']:.1f}\\% & {row_metrics['final']:.2f}\\\\\n"
            )
        f.write("\\bottomrule\\end{tabular}\n")

    labels = sorted({(r["estimator"], r["event_bias_s"], r["event_jitter_s"], r["event_drop_prob"], r["false_early_m"]) for r in event_rows})
    with (PAPER_TABLES / "event_boundary_table.tex").open("w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{lrrrrr}\\toprule\n")
        f.write("Event model & $n$ & Mean & P95 & Max & Unsafe\\\\\n")
        f.write("\\midrule\n")
        for label in labels:
            subset = [
                r
                for r in event_rows
                if (r["estimator"], r["event_bias_s"], r["event_jitter_s"], r["event_drop_prob"], r["false_early_m"]) == label
            ]
            row_metrics = metrics(subset)
            f.write(
                f"{event_condition_label(label)} & {int(row_metrics['n'])} & {row_metrics['mean']:.2f} & "
                f"{row_metrics['p95']:.2f} & {row_metrics['max']:.2f} & {100.0 * row_metrics['unsafe']:.1f}\\%\\\\\n"
            )
        f.write("\\bottomrule\\end{tabular}\n")

    profiles = sorted({r["profile"] for r in mode_rows})
    with (PAPER_TABLES / "mode_profile_table.tex").open("w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{lrrrrr}\\toprule\n")
        f.write("Profile & Delayed unsafe & Smith unsafe & CAIC unsafe & CAIC P95 & CAIC max\\\\\n")
        f.write("\\midrule\n")
        for profile in profiles:
            delayed = metrics([r for r in mode_rows if r["profile"] == profile and r["controller"] == "delayed_force"])
            smith = metrics([r for r in mode_rows if r["profile"] == profile and r["controller"] == "smith_predictor"])
            caic = metrics([r for r in mode_rows if r["profile"] == profile and r["controller"] == "contact_age_invariant"])
            f.write(
                f"{latex_escape(profile)} & {100.0 * delayed['unsafe']:.1f}\\% & {100.0 * smith['unsafe']:.1f}\\% & "
                f"{100.0 * caic['unsafe']:.1f}\\% & {caic['p95']:.2f} & {caic['max']:.2f}\\\\\n"
            )
        f.write("\\bottomrule\\end{tabular}\n")

    latencies = sorted({float(r["latency_s"]) for r in mismatch_rows})
    with (PAPER_TABLES / "mismatch_latency_table.tex").open("w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{rrrrrr}\\toprule\n")
        f.write("Latency & CAIC P95 & CAIC unsafe & Smith P95 & Smith unsafe & AWA unsafe\\\\\n")
        f.write("\\midrule\n")
        for latency in latencies:
            caic = metrics([r for r in mismatch_rows if abs(float(r["latency_s"]) - latency) < 1e-9 and r["controller"] == "contact_age_invariant"])
            smith = metrics([r for r in mismatch_rows if abs(float(r["latency_s"]) - latency) < 1e-9 and r["controller"] == "smith_predictor"])
            adaptive = metrics([r for r in mismatch_rows if abs(float(r["latency_s"]) - latency) < 1e-9 and r["controller"] == "adaptive_windowed_advance"])
            f.write(
                f"{1000.0 * latency:.0f} ms & {caic['p95']:.2f} & {100.0 * caic['unsafe']:.1f}\\% & "
                f"{smith['p95']:.2f} & {100.0 * smith['unsafe']:.1f}\\% & {100.0 * adaptive['unsafe']:.1f}\\%\\\\\n"
            )
        f.write("\\bottomrule\\end{tabular}\n")

    with (PAPER_TABLES / "negative_controls_table.tex").open("w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{rrrrr}\\toprule\n")
        f.write("Latency & Delayed & Smith & CAIC & Wrong event\\\\\n")
        f.write("\\midrule\n")
        for latency in sorted({float(r["latency_s"]) for r in negative_rows}):
            values: dict[str, float] = {}
            for controller in ["delayed_force", "smith_predictor", "contact_age_invariant", "wrong_event_control"]:
                subset = [r for r in negative_rows if abs(float(r["latency_s"]) - latency) < 1e-9 and r["controller"] == controller]
                values[controller] = float(subset[0]["peak_force_n"]) if subset else math.nan
            f.write(
                f"{1000.0 * latency:.0f} ms & {values['delayed_force']:.2f} & {values['smith_predictor']:.2f} & "
                f"{values['contact_age_invariant']:.2f} & {values['wrong_event_control']:.2f}\\\\\n"
            )
        f.write("\\bottomrule\\end{tabular}\n")


def write_tuning_table(tuning_rows: list[dict[str, str]], best: dict[str, str]) -> None:
    with (PAPER_TABLES / "tuning_selection_table.tex").open("w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{llrrrr}\\toprule\n")
        f.write("Baseline & Candidate & Score & Mean peak & Unsafe/miss & Selected\\\\\n")
        f.write("\\midrule\n")
        for controller in ["tuned_cautious", "low_pass_delayed", "latency_gain_schedule"]:
            values = sorted({r["tune"] for r in tuning_rows if r["controller"] == controller}, key=float)
            for value in values:
                subset = [r for r in tuning_rows if r["controller"] == controller and r["tune"] == value]
                row_metrics = metrics(subset)
                score = float(np.mean([float(r["peak_force_n"]) + 0.25 * float(r["final_force_error_n"]) for r in subset]))
                selected = "yes" if best.get(controller) == value else ""
                f.write(
                    f"{latex_escape(controller)} & {value} & {score:.2f} & {row_metrics['mean']:.2f} & "
                    f"{100.0 * row_metrics['unsafe_miss']:.1f}\\% & {selected}\\\\\n"
                )
        f.write("\\bottomrule\\end{tabular}\n")


def plot_stress_pareto(rows: list[dict[str, str]]) -> Path:
    path = FIGURES / "stress_pareto_tradeoff.png"
    controllers = ["delayed_force", "tuned_cautious", "smith_predictor", "one_step_mpc", "adaptive_windowed_advance", "contact_age_invariant"]
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    for controller in controllers:
        row_metrics = metrics([r for r in rows if r["controller"] == controller])
        size = 55.0 + 260.0 * row_metrics["unsafe_miss"]
        ax.scatter(row_metrics["final"], row_metrics["p95"], s=size, alpha=0.75)
        ax.annotate(latex_escape(controller), (row_metrics["final"], row_metrics["p95"]), xytext=(5, 4), textcoords="offset points", fontsize=8)
    ax.axhline(12.0, color="firebrick", linestyle=":", linewidth=1)
    ax.set_xlabel("mean final force error (N)")
    ax.set_ylabel("P95 peak force (N)")
    ax.set_title("Stress-suite safety versus final-force tracking")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path


def plot_event_latency_heatmap(rows: list[dict[str, str]]) -> Path:
    path = FIGURES / "event_latency_failure_heatmap.png"
    labels = sorted({(r["estimator"], r["event_bias_s"], r["event_jitter_s"], r["event_drop_prob"], r["false_early_m"]) for r in rows})
    latencies = sorted({float(r["latency_s"]) for r in rows})
    mat = np.zeros((len(labels), len(latencies)))
    for i, label in enumerate(labels):
        for j, latency in enumerate(latencies):
            subset = [
                r
                for r in rows
                if (r["estimator"], r["event_bias_s"], r["event_jitter_s"], r["event_drop_prob"], r["false_early_m"]) == label
                and abs(float(r["latency_s"]) - latency) < 1e-9
            ]
            mat[i, j] = np.mean([float(r["peak_force_n"]) > 12.0 for r in subset]) if subset else np.nan
    fig, ax = plt.subplots(figsize=(6.7, 4.5))
    im = ax.imshow(mat, cmap="magma", vmin=0.0, vmax=1.0, aspect="auto")
    fig.colorbar(im, ax=ax, label="failure rate peak > 12 N")
    ax.set_xticks(np.arange(len(latencies)))
    ax.set_xticklabels([f"{1000.0 * latency:.0f}" for latency in latencies])
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels([event_condition_label(label) for label in labels], fontsize=7)
    ax.set_xlabel("latency (ms)")
    ax.set_title("Event-estimator failure rate by latency")
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path


def write_tables(leaderboard: list[dict[str, float | str]], best: dict[str, str]) -> None:
    key_suites = ["nominal_latency", "event_estimation", "mode_switch", "large_seed_stress", "model_mismatch"]
    rows = [r for r in leaderboard if r["suite"] in key_suites and r["controller"] in {"delayed_force", "tuned_cautious", "smith_predictor", "one_step_mpc", "adaptive_windowed_advance", "contact_age_invariant"}]
    with (PAPER_TABLES / "full_scale_leaderboard.tex").open("w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{llrrrrr}\\toprule\n")
        f.write("Suite & Controller & $n$ & Mean peak & P95 peak & Unsafe & Unsafe/miss\\\\\n")
        f.write("\\midrule\n")
        for r in rows:
            f.write(
                f"{str(r['suite']).replace('_', ' ')} & {str(r['controller']).replace('_', ' ')} & "
                f"{int(float(r['n']))} & {float(r['mean_peak_force_n']):.2f} & "
                f"{float(r['p95_peak_force_n']):.2f} & {100.0 * float(r['failure_rate_peak_gt_12n']):.1f}\\% & "
                f"{100.0 * float(r['unsafe_or_no_contact_rate']):.1f}\\%\\\\\n"
            )
        f.write("\\bottomrule\\end{tabular}\n")
    with (PAPER_TABLES / "tuned_baselines.tex").open("w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{ll}\\toprule\n")
        f.write("Baseline & Selected hyperparameter\\\\\n")
        f.write("\\midrule\n")
        for name, value in best.items():
            f.write(f"{name.replace('_', ' ')} & {value}\\\\\n")
        f.write("\\bottomrule\\end{tabular}\n")


def copy_figures(paths: Iterable[Path]) -> None:
    for path in paths:
        shutil.copy2(path, PAPER_FIGURES / path.name)


def main() -> int:
    start = time.perf_counter()
    ensure_dirs()
    if "--summarize-only" in sys.argv:
        summary_path = RESULTS / "full_scale_summary.json"
        best = json.loads(summary_path.read_text(encoding="utf-8"))["best_tuned_hyperparameters"]
        csv_paths = [
            RESULTS / "nominal_latency_grid.csv",
            RESULTS / "event_estimation.csv",
            RESULTS / "model_mismatch_grid.csv",
            RESULTS / "mode_switch_grid.csv",
            RESULTS / "large_seed_stress.csv",
            RESULTS / "negative_controls.csv",
        ]
        leaderboard = write_leaderboard(csv_paths)
        figure_paths = [
            plot_nominal(load_csv(RESULTS / "nominal_latency_grid.csv")),
            plot_event(load_csv(RESULTS / "event_estimation.csv")),
            plot_mismatch(load_csv(RESULTS / "model_mismatch_grid.csv")),
            plot_mode(load_csv(RESULTS / "mode_switch_grid.csv")),
            plot_stress(load_csv(RESULTS / "large_seed_stress.csv")),
            plot_stress_pareto(load_csv(RESULTS / "large_seed_stress.csv")),
            plot_event_latency_heatmap(load_csv(RESULTS / "event_estimation.csv")),
        ]
        copy_figures(figure_paths)
        write_tables(leaderboard, best)
        write_secondary_tables(
            load_csv(RESULTS / "large_seed_stress.csv"),
            load_csv(RESULTS / "event_estimation.csv"),
            load_csv(RESULTS / "mode_switch_grid.csv"),
            load_csv(RESULTS / "model_mismatch_grid.csv"),
            load_csv(RESULTS / "negative_controls.csv"),
        )
        write_tuning_table(load_csv(RESULTS / "tuning_grid.csv"), best)
        print("summarized existing full-scale CSV outputs", flush=True)
        return 0
    best = tune_baselines()
    suite_specs: list[tuple[str, list[RunConfig]]] = [
        ("nominal_latency_grid.csv", make_nominal_configs(best)),
        ("event_estimation.csv", make_event_configs(best)),
        ("model_mismatch_grid.csv", make_mismatch_configs()),
        ("mode_switch_grid.csv", make_mode_configs(best)),
        ("large_seed_stress.csv", make_large_stress_configs(best)),
        ("negative_controls.csv", make_negative_control_configs()),
    ]
    csv_paths: list[Path] = []
    for filename, configs in suite_specs:
        path = RESULTS / filename
        print(f"running {filename}: {len(configs)} runs", flush=True)
        run_suite(path, configs)
        csv_paths.append(path)
    leaderboard = write_leaderboard(csv_paths)
    nominal_rows = load_csv(RESULTS / "nominal_latency_grid.csv")
    event_rows = load_csv(RESULTS / "event_estimation.csv")
    mismatch_rows = load_csv(RESULTS / "model_mismatch_grid.csv")
    mode_rows = load_csv(RESULTS / "mode_switch_grid.csv")
    stress_rows = load_csv(RESULTS / "large_seed_stress.csv")
    figure_paths = [
        plot_nominal(nominal_rows),
        plot_event(event_rows),
        plot_mismatch(mismatch_rows),
        plot_mode(mode_rows),
        plot_stress(stress_rows),
        plot_stress_pareto(stress_rows),
        plot_event_latency_heatmap(event_rows),
    ]
    copy_figures(figure_paths)
    write_tables(leaderboard, best)
    write_secondary_tables(stress_rows, event_rows, mode_rows, mismatch_rows, load_csv(RESULTS / "negative_controls.csv"))
    write_tuning_table(load_csv(RESULTS / "tuning_grid.csv"), best)
    elapsed = time.perf_counter() - start
    summary = {
        "best_tuned_hyperparameters": best,
        "elapsed_seconds": elapsed,
        "suites": {filename: len(configs) for filename, configs in suite_specs},
        "total_runs": int(sum(len(configs) for _, configs in suite_specs)),
        "streaming": True,
        "full_trajectories_saved_only_for_selected_examples": True,
    }
    (RESULTS / "full_scale_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
