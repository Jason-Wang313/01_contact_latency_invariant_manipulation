# Experiment Rigor Checklist

| Item | Status | Evidence |
|---|---|---|
| Stronger baseline than naive delay | Partial | Delay-scaled cautious baseline included. |
| Mechanism ablation | Done | `force_advance_only` and `contact_age_target_only` in `results/latency_sweep.csv`. |
| Multiple seeds | Done | 30-seed stress test in `results/seeded_stress.csv`. |
| Uncertainty estimates | Done | 95 percent CI in `results/stress_summary.json` and stress figure. |
| Model mismatch | Done | `results/stiffness_mismatch.csv` and `results/claim_check.json`. |
| Failure cases | Done | Mode-switch counterexample and model-mismatch residuals. |
| Hardware validation | Missing | Non-recoverable in this local repo. |
| Multi-DOF simulation | Missing | Non-recoverable without building a new simulator. |
| Claims narrowed to evidence | Done | Abstract, limitations, claims ledger, and final audit updated. |

## Rigor Decision

Empirical rigor is adequate for a workshop mechanism paper. It is not adequate for a main robotics or ICLR submission because all evidence is local 1D simulation.
