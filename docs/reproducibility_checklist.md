# Reproducibility Checklist

## Environment

- Python dependencies: `numpy>=1.26`, `matplotlib>=3.8`.
- LaTeX build: `pdflatex`, `bibtex`, `pdflatex`, `pdflatex` from `paper/`.
- Tested locally on Windows from `C:\Users\wangz\robotics_60_paper_batch\01_contact_latency_invariant_manipulation`.

## Commands

```powershell
python -m pip install -r requirements.txt
python scripts/run_experiments.py
python scripts/verify_claims.py
python scripts/run_full_scale_experiments.py
# Fast artifact regeneration from existing CSVs:
python scripts/run_full_scale_experiments.py --summarize-only
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Expected Outputs

- `results/latency_sweep.csv`
- `results/summary.json`
- `results/seeded_stress.csv`
- `results/stress_summary.json`
- `results/claim_check.json`
- `results/full_scale/nominal_latency_grid.csv`
- `results/full_scale/event_estimation.csv`
- `results/full_scale/model_mismatch_grid.csv`
- `results/full_scale/mode_switch_grid.csv`
- `results/full_scale/large_seed_stress.csv`
- `results/full_scale/negative_controls.csv`
- `results/full_scale/tuning_grid.csv`
- `results/full_scale/leaderboard.csv`
- `results/full_scale/full_scale_summary.json`
- `paper/figures/peak_force_vs_latency.png`
- `paper/figures/mechanism_ablation.png`
- `paper/figures/seeded_stress_peak_force.png`
- `paper/figures/full_scale_latency_baselines.png`
- `paper/figures/stress_pareto_tradeoff.png`
- `paper/figures/event_latency_failure_heatmap.png`
- `paper/tables/full_scale_leaderboard.tex`
- `paper/tables/tuning_selection_table.tex`
- `paper/main.pdf`
- `C:/Users/wangz/Downloads/01.pdf`

## Known Non-Reproducible Pieces

- The OpenAlex literature sweep depends on external API state if rerun.
- No hardware data exists.
- No pinned Python lockfile exists.

## Final Gate

- Final local build: 26 pages.
- Downloads copy allowed only after the final build is verified as the actual paper and at least 25 pages.
- Full-scale suite uses streaming CSV writes and saves full trajectories only for selected examples.
