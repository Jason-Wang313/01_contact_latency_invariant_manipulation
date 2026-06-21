# Experiment Rigor Checklist

| Item | Status | Evidence |
|---|---|---|
| Stronger baseline than naive delay | Partial | Delay-scaled cautious baseline included. |
| Mechanism ablation | Done | `force_advance_only` and `contact_age_target_only` in `results/latency_sweep.csv`. |
| Multiple seeds | Done | 30-seed stress test in `results/seeded_stress.csv`. |
| Uncertainty estimates | Done | 95 percent CI in `results/stress_summary.json` and stress figure. |
| Model mismatch | Done | `results/stiffness_mismatch.csv` and `results/claim_check.json`. |
| Failure cases | Done | Mode-switch counterexample and model-mismatch residuals. |
| Full-scale streamed evaluation | Done | `results/full_scale/*.csv`, 12,544 streamed rollouts. |
| VLA boxed-link visual audit | Done | Final `C:/Users/wangz/Downloads/01.pdf`; 52 link annotations, green = 35, red = 17, cyan = 0; rendered pages 2, 3, 4, 5, 7, 8, 9, 13, 15, 19, 20, 21, 23, and 25. |
| Final artifact cleanup | Done | Canonical `01.pdf` only; no duplicate `1.pdf`; transient `paper/main.pdf` removed. |
| Hardware validation | Missing | Non-recoverable in this local repo. |
| Multi-DOF simulation | Missing | Non-recoverable without building a new simulator. |
| Claims narrowed to evidence | Done | Abstract, limitations, claims ledger, and final audit updated. |

## Rigor Decision

Empirical rigor is adequate for the current batch's final simulation/mechanism-paper standard. It is still not a hardware-ready robotics result because all evidence is local 1D simulation.

2026-06-21 delivery metadata: 26 pages, 1,254,294 bytes, SHA256 `92E7BE958E6A5761619853445346A31D3C281FD23EF73D200DB8A4CD16A1F013`.
