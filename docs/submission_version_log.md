# Submission Version Log

| Version | Date | Changes | PDF |
|---|---|---|---|
| v1 | 2026-06-10 | Generated batch paper with literature sweep, toy simulator, formal claim checker, and initial PDF. | `C:/Users/wangz/Downloads/01.pdf` |
| v2 | 2026-06-12 | Added mechanism ablations, 30-seed stress tests, recent hostile prior-work citations, narrowed claims, visible hardening note, and submission-readiness docs. | `C:/Users/wangz/Downloads/01.pdf` |

## v2 Evidence Delta

- `results/latency_sweep.csv`: now includes five controllers.
- `results/seeded_stress.csv`: 30 seeds x 5 latencies x 5 controllers.
- `results/stress_summary.json`: reports p95, max, failure rate, and 150 ms confidence intervals.
- `paper/figures/mechanism_ablation.png`: shows force advancement dominates latency invariance.
- `paper/figures/seeded_stress_peak_force.png`: reports stress-test uncertainty.
