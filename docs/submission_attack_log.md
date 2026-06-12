# Submission Attack Log

Paper: 01_contact_latency_invariant_manipulation

Hardening version: v2
Date: 2026-06-12 19:01:59 +01:00

## Attack Rounds

| Round | Attack | Action | Residual Risk |
|---:|---|---|---|
| 1 | This is just a Smith predictor. | Added force-advance-only ablation and narrowed claims. | High; still closest hostile framing. |
| 2 | Contact-age phasing may not be necessary. | Added contact-age-target-only and force-advance-only ablations. | Confirmed; phasing is secondary. |
| 3 | Toy 1D result has no uncertainty. | Added 30-seed randomized stress suite and confidence intervals. | Stress is still synthetic. |
| 4 | No strong baselines beyond delayed feedback. | Retained delay-scaled cautious baseline and added mechanism ablations. | No passivity/wave-variable implementation. |
| 5 | Model mismatch breaks exactness. | Kept stiffness mismatch ablation and formal mismatch counterexample. | No adaptive estimator. |
| 6 | Mode switches make force advancement invalid. | Kept formal mode-switch counterexample and emphasized semantic validity boundary. | No hybrid proof. |
| 7 | Recent tactile/force policies make novelty stale. | Added 2024-2026 hostile force/tactile policy citations and prior-work addendum. | Web search was targeted, not exhaustive. |
| 8 | Claims imply deployment readiness. | Revised abstract, limitations, final audit, and readiness decision. | Hardware evidence remains absent. |
| 9 | Reproducibility depends on undocumented outputs. | Updated README and added reproducibility checklist. | Dependency versions are ranges. |
| 10 | Figures may overstate full method. | Added mechanism ablation figure and text saying force advancement dominates. | Main title may still sound broad. |
| 11 | Stress test hides failures. | Recorded max, p95, failure rate over 12 N, and 150 ms CI in docs. | No per-seed appendix table in paper body. |
| 12 | ICLR fit is weak. | Marked terminal state workshop-only / strong-revise for main conference. | Venue fit remains weak. |

## Stop Condition

Stopped before 50 rounds because the remaining meaningful attacks converge on the same non-recoverable limits: no hardware, only 1D local simulation, no multi-DOF contact modes, and force advancement accounting for most of the empirical gain. Recoverable documentation, ablation, stress-test, and claim-scope issues were fixed.
