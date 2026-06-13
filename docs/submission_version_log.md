# Submission Version Log

| Version | Date | Changes | PDF |
|---|---|---|---|
| v1 | 2026-06-10 | Generated batch paper with literature sweep, toy simulator, formal claim checker, and initial PDF. | `C:/Users/wangz/Downloads/01.pdf` |
| v2 | 2026-06-12 | Added mechanism ablations, 30-seed stress tests, recent hostile prior-work citations, narrowed claims, visible hardening note, and submission-readiness docs. | `C:/Users/wangz/Downloads/01.pdf` |
| v3 | 2026-06-13 | Expanded to a 26-page full-scale simulation manuscript with 12,544 streamed rollouts, stronger baselines, tuning audit, event-estimator boundaries, model mismatch, mode/profile shifts, stress quantiles, negative controls, and reproducibility artifacts. | `C:/Users/wangz/Downloads/01.pdf` |

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
