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
- `paper/figures/peak_force_vs_latency.png`
- `paper/figures/mechanism_ablation.png`
- `paper/figures/seeded_stress_peak_force.png`
- `paper/main.pdf`
- `C:/Users/wangz/Downloads/01.pdf`

## Known Non-Reproducible Pieces

- The OpenAlex literature sweep depends on external API state if rerun.
- No hardware data exists.
- No pinned Python lockfile exists.
