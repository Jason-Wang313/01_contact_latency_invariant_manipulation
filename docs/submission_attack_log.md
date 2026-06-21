# Submission Attack Log

Paper: 01_contact_latency_invariant_manipulation

Hardening version: v3.1
Date: 2026-06-21

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
| 12 | ICLR fit is weak. | Marked the v2 terminal state as not main-conference ready. | Venue fit remains weak without hardware or multi-DOF evidence. |
| 13 | Short mechanism note is not enough. | Expanded v3 to a 26-page full-scale simulation/mechanism manuscript with 12,544 streamed rollouts, stronger baselines, event-estimator boundaries, mismatch grids, mode/profile shifts, and negative controls. | Still local simulation. |
| 14 | PDF link boxes must visually match the visible VLA-v4 role model. | Added explicit hyperref boxed-link policy, rebuilt, rendered all link-bearing pages, and verified green citation/URL boxes plus red internal-reference boxes. | Visual style is verified for this artifact; future source edits must preserve the policy. |

## Stop Condition

The v3 pass completed the recoverable local scope: full-scale streamed experiments, stronger baselines, ablations, stress tests, event-estimation failures, model/mode mismatch studies, generated figures/tables, a 26-page final manuscript, and explicit limitations. Remaining meaningful attacks converge on the same non-recoverable limits: no hardware, only 1D local simulation, no multi-DOF contact modes, and force advancement accounting for most of the empirical gain.

The 2026-06-21 VLA highlight-hardening pass completed visual delivery scope: `C:/Users/wangz/Downloads/01.pdf` is 26 pages, 1,254,294 bytes, SHA256 `92E7BE958E6A5761619853445346A31D3C281FD23EF73D200DB8A4CD16A1F013`, with 52 role-model-style link annotations and zero malformed page-edge rectangles.
