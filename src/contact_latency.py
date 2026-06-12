"""Minimal contact-latency manipulation simulator.

The simulator is intentionally small: a one-dimensional robot endpoint moves
toward a rigid contact and regulates force through velocity commands. The goal
is not realism; it is to isolate the timing assumption that delayed force
feedback is semantically stale at first contact.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class PlantParams:
    dt: float = 5e-4
    horizon: float = 1.2
    servo_tau: float = 0.018
    stiffness: float = 2600.0
    damping: float = 7.0
    initial_gap: float = 0.018
    max_velocity: float = 0.18


@dataclass(frozen=True)
class ControlParams:
    desired_force: float = 8.0
    approach_velocity: float = 0.10
    max_velocity: float = 0.18
    force_gain: float = 0.020
    ramp_rate: float = 260.0
    k_hat_scale: float = 1.0
    c_hat_scale: float = 1.0


@dataclass
class SimResult:
    time: np.ndarray
    q: np.ndarray
    v: np.ndarray
    force: np.ndarray
    command: np.ndarray
    delayed_force: np.ndarray
    predicted_force: np.ndarray
    target_force: np.ndarray
    contact_age: np.ndarray
    latency: float
    controller: str

    def metrics(self) -> dict[str, float | str]:
        dt = float(self.time[1] - self.time[0])
        force = self.force
        desired = 8.0
        contact = force > 0.05
        if np.any(contact):
            first_idx = int(np.argmax(contact))
            post = force[first_idx:]
            peak_post = float(np.max(post))
            impulse_250ms = float(np.sum(post[: int(0.25 / dt)]) * dt)
        else:
            peak_post = 0.0
            impulse_250ms = 0.0
        final_err = float(abs(force[-1] - desired))
        return {
            "controller": self.controller,
            "latency_s": self.latency,
            "peak_force_n": peak_post,
            "overshoot_n": max(0.0, peak_post - desired),
            "impulse_250ms_ns": impulse_250ms,
            "final_force_error_n": final_err,
        }


class Controller(Protocol):
    name: str

    def reset(self) -> None:
        ...

    def command(
        self,
        t: float,
        q: float,
        v: float,
        delayed_q: float,
        delayed_v: float,
        delayed_force: float,
        params: PlantParams,
        control: ControlParams,
    ) -> tuple[float, float, float, float]:
        """Return velocity command, predicted force, target force, contact age."""


def contact_force(q: float, v: float, params: PlantParams) -> float:
    if q <= 0.0:
        return 0.0
    return max(0.0, params.stiffness * q + params.damping * v)


def clip_velocity(u: float, control: ControlParams) -> float:
    return float(np.clip(u, -control.max_velocity, control.max_velocity))


class DelayedForceController:
    name = "delayed_force"

    def reset(self) -> None:
        pass

    def command(
        self,
        t: float,
        q: float,
        v: float,
        delayed_q: float,
        delayed_v: float,
        delayed_force: float,
        params: PlantParams,
        control: ControlParams,
    ) -> tuple[float, float, float, float]:
        target = control.desired_force
        u = control.force_gain * (target - delayed_force)
        if delayed_force < 0.05 and q < 0.002:
            u = max(u, control.approach_velocity)
        return clip_velocity(u, control), delayed_force, target, 0.0


class CautiousDelayedController:
    name = "delay_scaled_cautious"

    def __init__(self, latency: float) -> None:
        self.latency = latency

    def reset(self) -> None:
        pass

    def command(
        self,
        t: float,
        q: float,
        v: float,
        delayed_q: float,
        delayed_v: float,
        delayed_force: float,
        params: PlantParams,
        control: ControlParams,
    ) -> tuple[float, float, float, float]:
        # A conservative baseline: slow approach as the blind interval grows.
        safe_approach = control.approach_velocity / (1.0 + 18.0 * self.latency)
        target = control.desired_force
        u = control.force_gain * (target - delayed_force)
        if delayed_force < 0.05:
            u = safe_approach
        return clip_velocity(u, control), delayed_force, target, 0.0


class ForceAdvanceOnlyController:
    name = "force_advance_only"

    def __init__(self) -> None:
        self.contact_time_hat: float | None = None

    def reset(self) -> None:
        self.contact_time_hat = None

    def command(
        self,
        t: float,
        q: float,
        v: float,
        delayed_q: float,
        delayed_v: float,
        delayed_force: float,
        params: PlantParams,
        control: ControlParams,
    ) -> tuple[float, float, float, float]:
        k_hat = params.stiffness * control.k_hat_scale
        c_hat = params.damping * control.c_hat_scale
        if q > 0.0 and self.contact_time_hat is None:
            self.contact_time_hat = t
        if self.contact_time_hat is None:
            return control.approach_velocity, 0.0, 0.0, 0.0

        contact_age = max(0.0, t - self.contact_time_hat)
        if q <= 0.0:
            predicted = 0.0
        elif delayed_q > 0.0:
            predicted = delayed_force + k_hat * (q - delayed_q) + c_hat * (v - delayed_v)
            predicted = max(0.0, predicted)
        else:
            predicted = max(0.0, k_hat * q + c_hat * v)

        target = control.desired_force
        u = control.force_gain * (target - predicted)
        return clip_velocity(u, control), predicted, target, contact_age


class ContactAgeTargetOnlyController:
    name = "contact_age_target_only"

    def __init__(self) -> None:
        self.contact_time_hat: float | None = None

    def reset(self) -> None:
        self.contact_time_hat = None

    def command(
        self,
        t: float,
        q: float,
        v: float,
        delayed_q: float,
        delayed_v: float,
        delayed_force: float,
        params: PlantParams,
        control: ControlParams,
    ) -> tuple[float, float, float, float]:
        if q > 0.0 and self.contact_time_hat is None:
            self.contact_time_hat = t
        if self.contact_time_hat is None:
            return control.approach_velocity, 0.0, 0.0, 0.0

        contact_age = max(0.0, t - self.contact_time_hat)
        target = min(control.desired_force, control.ramp_rate * contact_age)
        u = control.force_gain * (target - delayed_force)
        return clip_velocity(u, control), delayed_force, target, contact_age


class ContactAgeInvariantController:
    name = "contact_age_invariant"

    def __init__(self) -> None:
        self.contact_time_hat: float | None = None

    def reset(self) -> None:
        self.contact_time_hat = None

    def command(
        self,
        t: float,
        q: float,
        v: float,
        delayed_q: float,
        delayed_v: float,
        delayed_force: float,
        params: PlantParams,
        control: ControlParams,
    ) -> tuple[float, float, float, float]:
        k_hat = params.stiffness * control.k_hat_scale
        c_hat = params.damping * control.c_hat_scale
        if q > 0.0 and self.contact_time_hat is None:
            # In a real system this guard may come from kinematics, expected
            # geometry, or a delayed force edge corrected by the timing state.
            self.contact_time_hat = t
        if self.contact_time_hat is None:
            predicted = 0.0
            target = 0.0
            return control.approach_velocity, predicted, target, 0.0

        contact_age = max(0.0, t - self.contact_time_hat)
        if q <= 0.0:
            predicted = 0.0
        elif delayed_q > 0.0:
            predicted = delayed_force + k_hat * (q - delayed_q) + c_hat * (v - delayed_v)
            predicted = max(0.0, predicted)
        else:
            # The delayed sample is pre-contact, so advance from the inferred
            # physical contact state rather than waiting for the stale edge.
            predicted = max(0.0, k_hat * q + c_hat * v)

        target = min(control.desired_force, control.ramp_rate * contact_age)
        u = control.force_gain * (target - predicted)
        return clip_velocity(u, control), predicted, target, contact_age


def simulate(
    controller: Controller,
    latency: float,
    plant: PlantParams | None = None,
    control: ControlParams | None = None,
) -> SimResult:
    plant = plant or PlantParams()
    control = control or ControlParams()
    controller.reset()
    n = int(plant.horizon / plant.dt) + 1
    time = np.arange(n) * plant.dt
    q = np.zeros(n)
    v = np.zeros(n)
    force = np.zeros(n)
    command = np.zeros(n)
    delayed_force = np.zeros(n)
    predicted_force = np.zeros(n)
    target_force = np.zeros(n)
    contact_age = np.zeros(n)
    q[0] = -plant.initial_gap
    delay_steps = max(0, int(round(latency / plant.dt)))

    for i in range(1, n):
        # The controller computes command i from samples available before the
        # current plant update. Even zero configured latency therefore uses the
        # previous integration sample rather than the not-yet-written force[i].
        j = max(0, i - delay_steps - 1)
        delayed_force[i] = force[j]
        u, pred, target, age = controller.command(
            float(time[i - 1]),
            float(q[i - 1]),
            float(v[i - 1]),
            float(q[j]),
            float(v[j]),
            float(force[j]),
            plant,
            control,
        )
        command[i] = u
        predicted_force[i] = pred
        target_force[i] = target
        contact_age[i] = age
        v[i] = v[i - 1] + (u - v[i - 1]) / plant.servo_tau * plant.dt
        v[i] = float(np.clip(v[i], -plant.max_velocity, plant.max_velocity))
        q[i] = q[i - 1] + v[i] * plant.dt
        force[i] = contact_force(float(q[i]), float(v[i]), plant)

    return SimResult(
        time=time,
        q=q,
        v=v,
        force=force,
        command=command,
        delayed_force=delayed_force,
        predicted_force=predicted_force,
        target_force=target_force,
        contact_age=contact_age,
        latency=latency,
        controller=controller.name,
    )


def latency_slope(latencies: np.ndarray, values: np.ndarray) -> float:
    if len(latencies) < 2:
        return 0.0
    centered = latencies - np.mean(latencies)
    denom = float(np.sum(centered**2))
    if denom <= 0.0:
        return 0.0
    return float(np.sum(centered * (values - np.mean(values))) / denom)
