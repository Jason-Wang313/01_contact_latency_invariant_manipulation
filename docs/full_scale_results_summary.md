# Full-Scale Results Summary

## Final Gate

- Final manuscript target for this pass: at least 25 pages of real content.
- Verified local build before Downloads copy: 26 pages.
- No intermediate PDF was copied to Downloads before the final gate.

## Full-Scale Run

- Runner: `python scripts/run_full_scale_experiments.py`
- Fast regeneration path: `python scripts/run_full_scale_experiments.py --summarize-only`
- Total streamed rollouts: 12,544
- Runtime on the current machine: 3,194 seconds
- RAM discipline: compact per-run CSV rows streamed to disk; full trajectories saved only for selected examples.

## Suite Sizes

- `nominal_latency_grid.csv`: 112 runs
- `event_estimation.csv`: 1,920 runs
- `model_mismatch_grid.csv`: 420 runs
- `mode_switch_grid.csv`: 3,600 runs
- `large_seed_stress.csv`: 6,480 runs
- `negative_controls.csv`: 12 runs

## Headline Findings

- Nominal latency grid: delayed force feedback reaches 111.90 N at 250 ms; CAIC remains at 8.48 N.
- Large stress suite: CAIC has 9.22 N mean peak force and 3.1% unsafe peaks; delayed feedback has 66.79 N mean peak force and 85.4% unsafe peaks.
- One-step MPC is a strong baseline with lower mean peak force but higher mean final-force error.
- Event timing is the sharpest boundary: delayed force-edge event timing fails every event-estimation trial, and event dropout creates rare severe peaks up to 261.35 N.
- Mode validity is the second boundary: hard-to-soft profile shifts produce most CAIC mode-suite failures.

## Generated Paper Artifacts

- `paper/figures/full_scale_latency_baselines.png`
- `paper/figures/large_seed_stress_distribution.png`
- `paper/figures/stress_pareto_tradeoff.png`
- `paper/figures/event_estimator_sensitivity.png`
- `paper/figures/event_latency_failure_heatmap.png`
- `paper/figures/model_mismatch_surface.png`
- `paper/figures/mode_switch_failure_map.png`
- `paper/tables/full_scale_leaderboard.tex`
- `paper/tables/stress_quantiles.tex`
- `paper/tables/event_boundary_table.tex`
- `paper/tables/mode_profile_table.tex`
- `paper/tables/mismatch_latency_table.tex`
- `paper/tables/negative_controls_table.tex`
- `paper/tables/tuning_selection_table.tex`
