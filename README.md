# Contact-Age Invariant Control for Delayed Contact Evidence

This repository contains paper 01 in the robotics/embodied-intelligence batch.
It studies contact timing mismatch as a controller state for contact-rich manipulation with delayed force or tactile evidence.

## Main Artifacts

- `docs/related_work_matrix.csv`: 1242 OpenAlex metadata/abstract entries, with 1000 counted for the landscape sweep.
- `docs/literature_map.md`: field map, hidden assumptions, and mechanism clusters.
- `docs/hostile_prior_work.md`: 100-paper hostile prior-work set.
- `docs/novelty_decision.md`: chosen thesis and rejected alternatives.
- `src/contact_latency.py`: minimal contact-latency simulator.
- `scripts/run_experiments.py`: latency sweeps, mechanism ablations, seeded stress tests, and figures.
- `scripts/verify_claims.py`: formal claim audit and counterexamples.
- `scripts/run_full_scale_experiments.py`: RAM-light full-scale suite with 12,544 streamed rollouts, tuned baselines, stress tests, event-estimator studies, mismatch grids, and generated paper figures/tables.
- `paper/main.tex`: anonymous ICLR-style paper source.

## Reproduce

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Regenerate the literature artifacts:

```powershell
python scripts/collect_literature.py
python scripts/synthesize_docs.py
```

Run evidence:

```powershell
python scripts/run_experiments.py
python scripts/verify_claims.py
python scripts/run_full_scale_experiments.py
```

To regenerate paper tables and figures from existing full-scale CSV files without rerunning the 12,544 rollouts:

```powershell
python scripts/run_full_scale_experiments.py --summarize-only
```

Primary generated outputs:

- `results/latency_sweep.csv` and `results/summary.json`: deterministic latency sweep with five controllers.
- `results/seeded_stress.csv` and `results/stress_summary.json`: 30-seed randomized stress test.
- `results/claim_check.json`: formal same-mode, mode-switch, and mismatch checks.
- `results/full_scale/*.csv`: full-scale streamed metrics, including the 6,480-run large stress suite.
- `results/full_scale/full_scale_summary.json`: suite sizes, runtime, tuned hyperparameters, and streaming metadata.
- `paper/tables/*.tex`: generated leaderboard, boundary, quantile, tuning, and negative-control tables.
- `paper/figures/*.png`: paper-ready copies of all regenerated figures.

Compile the paper from `paper/`:

```powershell
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The final batch output PDF is saved to `C:/Users/wangz/Downloads/01.pdf` only after the manuscript clears the batch final gate. Current final build: 26 pages.

## Current Artifact

2026-06-21 VLA highlight hardening verified the canonical Downloads PDF against the visible VLA-v4 boxed-link role model.

- Canonical PDF: `C:/Users/wangz/Downloads/01.pdf`
- Pages: 26
- Size: 1,254,294 bytes
- SHA256: `92E7BE958E6A5761619853445346A31D3C281FD23EF73D200DB8A4CD16A1F013`
- Link annotations: 52 total on pages `[(2, 33), (3, 2), (4, 2), (5, 1), (7, 1), (8, 1), (9, 2), (13, 1), (15, 2), (19, 1), (20, 1), (21, 3), (23, 1), (25, 1)]`
- Link colors: green = 35, red = 17, cyan = 0
- Link borders: `(0, 0, 1)` for all annotations
- Oversized page-edge annotation audit: 0 malformed rectangles
- Visual audit: pages 2, 3, 4, 5, 7, 8, 9, 13, 15, 19, 20, 21, 23, and 25 rendered and inspected with crisp green citation/URL boxes and red internal-reference boxes.
- Cleanup: no duplicate `C:/Users/wangz/Downloads/1.pdf`; local `paper/main.pdf` removed after export.
