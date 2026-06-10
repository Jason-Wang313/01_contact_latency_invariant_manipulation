# Novelty Boundary Map

## Hidden Assumptions That May Be False

1. Contact event time is available to the controller when it matters.
2. A delayed force sample still describes the current contact mode.
3. Continuous-time delay robustness is enough for hybrid contact transitions.
4. Sensor latency is fixed, known, or independent of contact events.
5. Controller clocks, sensor clocks, and actuator clocks are aligned.
6. The first damaging impulse is small enough to wait for feedback.
7. Compliance can absorb timing mismatch without changing the task objective.
8. Contact mode switches are sparse relative to sensing delay.
9. Contact geometry is known well enough for pre-contact prediction.
10. Environment stiffness and damping remain stationary across trials.
11. Friction changes forces but not the timing logic of contact onset.
12. Tactile processing latency is negligible compared with mechanical transients.
13. Hybrid guards are evaluated on current state rather than delayed observations.
14. Passivity margins imply useful force transients, not merely stability.
15. Learning policies trained with one timing distribution generalize to another.
16. The safety variable is instantaneous force error rather than impulse accumulated during the blind interval.
17. The robot can always slow down enough before contact without task loss.
18. Delayed visual and tactile estimates share the same effective timestamp.
19. Actuator saturation does not couple with late contact correction.
20. Thresholded force onset is an unambiguous contact-time estimator.
21. Contact-rich planning errors are mostly geometric rather than temporal.
22. A single latency scalar describes a multi-stage sensing pipeline.
23. Mode estimators can be judged by accuracy without judging phase error.
24. The controller's state should be indexed by wall-clock time rather than contact age.

## Directions That Break Assumptions

- **Contact-age invariant control**: Make contact timing mismatch a state variable and command interaction in inferred contact-age coordinates. Strongest fit: changes the central mechanism from delayed feedback stabilization to hybrid-event time alignment.
- **Impulse-before-feedback safety filters**: Constrain the pre-feedback impulse budget using velocity, compliance, and worst-case delay. Strong safety angle, but close to passivity/energy tanks unless the event-time state is central.
- **Latency-calibrating tactile servoing**: Estimate the timestamp of tactile frames online and servo on timestamp-corrected contact patches. Useful, but risks being perceived as a perception timestamping paper rather than a manipulation mechanism.
- **Hybrid guard predictors for contact planners**: Predict guard crossing times and re-index contact plans by guard residual. Good planning contribution, but heavier formal burden and less runnable in this repository.
- **Contact-mode delay adversarial benchmark**: Benchmark policies under mode-correlated sensing delay. Forbidden as benchmark-only unless paired with a new mechanism.
- **Delay-aware impedance adaptation**: Adapt impedance based on estimated contact event mismatch and blind-interval impulse. Promising but too close to adding adaptation unless the age coordinate is the real contribution.

## Boundary Against Prior Work

| Prior cluster | What is already covered | What remains open |
|---|---|---|
| Time-delay control | Stability and tracking with delayed measurements or inputs | Hybrid event-time semantics when the delayed sample belongs to a previous contact mode |
| Smith predictors | Prediction through known continuous plant dynamics | Contact onset changes the plant model exactly when the delayed force edge arrives |
| Passivity/teleoperation | Energy safety under delayed force/motion channels | Stable behavior can still accumulate unacceptable impulse before contact feedback |
| Impedance/admittance | Compliant force-motion behavior | Virtual compliance is usually time-indexed, not contact-age-indexed |
| Hybrid force/position control | Subspace switching at contact | Switch timing is treated as observable or exogenous |
| Tactile contact estimation | Recognize contact state, slip, geometry, and outcome | Tactile frames may be semantically stale during fast contact transitions |
| Contact-rich planning/MPC | Optimize through contact models and constraints | Delay-corrupted contact evidence is usually folded into robustness rather than represented as a state |

## Mechanism That Survives The Boundary

The surviving mechanism is a contact-timing mismatch state: maintain an estimate of the difference between physical contact age and observation age, advance delayed contact evidence through a local contact model when the mode is known, and phase the force objective by inferred contact age. This is narrower than generic delay compensation and more specific than adding uncertainty.
