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
```

Primary generated outputs:

- `results/latency_sweep.csv` and `results/summary.json`: deterministic latency sweep with five controllers.
- `results/seeded_stress.csv` and `results/stress_summary.json`: 30-seed randomized stress test.
- `results/claim_check.json`: formal same-mode, mode-switch, and mismatch checks.
- `paper/figures/*.png`: paper-ready copies of all regenerated figures.

Compile the paper from `paper/`:

```powershell
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The final batch output PDF is saved to `C:/Users/wangz/Downloads/01.pdf` by the child run.
