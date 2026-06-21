# Submission Version Log

| Version | Date | Changes | PDF |
|---|---|---|---|
| v1 | 2026-06-10 | Generated batch paper with literature sweep, toy simulator, formal claim checker, and initial PDF. | `C:/Users/wangz/Downloads/01.pdf` |
| v2 | 2026-06-12 | Added mechanism ablations, 30-seed stress tests, recent hostile prior-work citations, narrowed claims, visible hardening note, and submission-readiness docs. | `C:/Users/wangz/Downloads/01.pdf` |
| v3 | 2026-06-13 | Expanded to a 26-page full-scale simulation manuscript with 12,544 streamed rollouts, stronger baselines, tuning audit, event-estimator boundaries, model mismatch, mode/profile shifts, stress quantiles, negative controls, and reproducibility artifacts. | `C:/Users/wangz/Downloads/01.pdf` |
| v3.1 | 2026-06-21 | Matched the visible VLA-v4 boxed-link role model with explicit hyperref policy, rebuilt, exported, rendered all link-bearing pages, and verified green citation/URL boxes plus red internal-reference boxes. | `C:/Users/wangz/Downloads/01.pdf` |

## v2 Evidence Delta

- `results/latency_sweep.csv`: now includes five controllers.
- `results/seeded_stress.csv`: 30 seeds x 5 latencies x 5 controllers.
- `results/stress_summary.json`: reports p95, max, failure rate, and 150 ms confidence intervals.
- `paper/figures/mechanism_ablation.png`: shows force advancement dominates latency invariance.
- `paper/figures/seeded_stress_peak_force.png`: reports stress-test uncertainty.

## v3 Evidence Delta

- `scripts/run_full_scale_experiments.py`: RAM-light streamed full-scale runner plus summarize-only regeneration path.
- `results/full_scale/full_scale_summary.json`: 12,544 total rollouts, 3,194 second runtime, streaming enabled.
- `results/full_scale/large_seed_stress.csv`: 6,480-run stress suite over 180 seeds, latencies, profile families, and plant/model variation.
- `results/full_scale/event_estimation.csv`: 1,920-run event-timing study including perfect guard, delayed force edge, noisy guards, geometry priors, and event dropout.
- `paper/figures/stress_pareto_tradeoff.png`: safety versus final-force tracking tradeoff.
- `paper/figures/event_latency_failure_heatmap.png`: event-estimator failure rate by latency.
- `paper/tables/*.tex`: generated full-scale leaderboard, stress quantiles, profile/mismatch/event boundary tables, tuning table, and negative-control table.
- Final local PDF build verified at 26 pages before copying to Downloads.

## v3.1 Delivery Metadata

- Pages: 26
- Size: 1,254,294 bytes
- SHA256: `92E7BE958E6A5761619853445346A31D3C281FD23EF73D200DB8A4CD16A1F013`
- Link inventory: 52 annotations on pages `[(2, 33), (3, 2), (4, 2), (5, 1), (7, 1), (8, 1), (9, 2), (13, 1), (15, 2), (19, 1), (20, 1), (21, 3), (23, 1), (25, 1)]`
- Link colors: green = 35, red = 17, cyan = 0
- Link borders: `(0, 0, 1)` for all annotations
- Oversized annotation audit: 0 malformed page-edge rectangles
- Visual audit pages: 2, 3, 4, 5, 7, 8, 9, 13, 15, 19, 20, 21, 23, and 25
- Cleanup: no duplicate `C:/Users/wangz/Downloads/1.pdf`; no local `paper/main.pdf`
