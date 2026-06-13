# Full-Scale Execution Plan: Paper 01

## Current Claim

Paper 01 claims that first-contact latency is not only a delayed-feedback problem; it is a hybrid-event semantics problem. The current mechanism, contact-age invariant control, advances delayed force evidence through a local contact model and indexes force targets by inferred contact age. Existing evidence is a one-dimensional Kelvin-Voigt point-contact simulator with a latency sweep, five controller variants, a 30-seed stress test, and a formal same-mode force-advance check.

## Current Gaps

- The manuscript is only 7 pages and reads like a mechanism note, not a full-scale submission.
- Evidence is mostly one-dimensional, single-contact, and idealized.
- Existing stress is useful but too small: 30 seeds, limited parameter families, no heavy-tail or mode-shift conditions.
- Baselines are not strong enough. The current cautious baseline is hand-coded, and there is no tuned predictor/controller family.
- Contact timing estimation is assumed from a perfect guard; the paper needs delayed edge, noisy event, and estimator-error studies.
- The current ablation shows force advancement alone explains most of the benefit, so the final paper must either add evidence where contact-age phasing matters or explicitly narrow the claim.
- No multi-axis/multi-contact proxy, no actuator saturation study, no timestamp jitter study, no sensor-dropout study, and no computational overhead study.
- Related work and limitations are present but short; they need a broader, better organized paper-scale treatment.

## Target Experiments

1. **Expanded deterministic latency grid.**
   Sweep latency from 0 to 250 ms, control rate, servo time constant, force gain, ramp rate, and approach velocity. Report peak force, impulse, settling time, steady-state error, time-to-safe-contact, and high-force dwell time.

2. **Tuned baseline family.**
   Add grid-tuned cautious, grid-tuned Smith-style predictor, low-pass filtered delayed feedback, latency-aware gain scheduling, and model-predictive one-step force control. Tune baselines on a train grid and report held-out results.

3. **Contact-event estimation study.**
   Replace perfect contact guard with delayed force-edge detection, noisy proprioceptive residual detection, and geometry-prior detection. Sweep timestamp noise, missed edge probability, false early contact, and delayed edge bias.

4. **Model mismatch and system identification.**
   Sweep stiffness, damping, mass/servo lag, friction-like deadband, actuator saturation, and wrong local stiffness/damping estimates. Add an online windowed stiffness estimator baseline and compare fixed-model versus adaptive variants.

5. **Mode-switch and multi-contact proxy.**
   Add piecewise contact modes: soft-to-hard transition, contact loss/recontact, dual surface/fixture contact, and hidden compliance jump. These tests should identify where contact-age control fails, not hide failures.

6. **Large seed stress.**
   Scale from 30 seeds to at least 300-1000 lightweight seeds, run sequentially and stream CSV rows to disk. Use compact result summaries and avoid storing full trajectories except for selected exemplars.

7. **Negative controls.**
   Include cases with zero latency, perfectly current force, deliberately wrong contact-age estimate, and irrelevant target phasing. These controls should show when the mechanism should not help.

8. **Ablation matrix.**
   Cross advancement, contact-age phasing, event-estimator type, model-estimator type, gain schedule, and saturation rule. Report both performance and failure-mode shifts.

9. **Representative trajectories.**
   Save only selected full trajectories for figure panels: nominal, delayed failure, cautious failure, tuned predictor success/failure, estimator-lag failure, and mode-switch failure.

10. **Runtime and memory audit.**
    Measure total run time, peak approximate memory footprint, rows written, and artifact sizes. Show that experiments are reproducible on a modest machine.

## Baselines

- Delayed force feedback.
- Delay-scaled cautious feedback.
- Grid-tuned cautious feedback.
- Force-advance-only.
- Contact-age target-only.
- Full contact-age invariant controller.
- Smith-style local force predictor with no contact-age target phasing.
- Latency-aware gain schedule.
- Low-pass filtered delayed force controller.
- One-step model-predictive force controller.
- Windowed system-identification predictor.
- Oracle current-force controller as an upper bound, clearly marked as nondeployable.
- Wrong-event negative-control controller.

## Figures And Tables

- Main latency scaling curve with train/held-out split.
- Baseline leaderboard table across nominal, stress, event-noise, and mode-switch suites.
- Ablation heat map for advancement/phasing/estimator components.
- Contact-event estimation error plot.
- Model mismatch sensitivity plot.
- Mode-switch failure taxonomy figure.
- Large-seed distribution plot: p50/p90/p95/max peak force and impulse.
- Representative trajectory panel.
- Compute/reproducibility table.
- Claim boundary table mapping each supported claim to the experiment that supports or falsifies it.

## Writing Expansion

- Expand introduction with a stronger motivating example and precise claim boundary.
- Split related work into force/impedance control, delay compensation/passivity, tactile event timing, predictive control, and contact-rich learning.
- Add a formal setup section that distinguishes signal delay, event delay, and semantic contact-age mismatch.
- Add a methods section for each controller/baseline family.
- Add a full experimental protocol section with train/held-out grids, metrics, and RAM-light execution.
- Add results subsections for nominal sweep, tuned baselines, event estimation, mismatch, mode switches, large stress, and negative controls.
- Add a detailed limitations/failure taxonomy section.
- Add an artifact/reproducibility section.

## Page-Count Strategy

The target is at least 20 pages of real manuscript content. The expected composition is:

- Abstract and introduction: 2 pages.
- Related work: 3 pages.
- Problem setup and formal claim: 2 pages.
- Controllers and baselines: 3 pages.
- Experimental protocol: 2 pages.
- Results: 6-8 pages with figures/tables.
- Failure analysis, limitations, and reproducibility: 3 pages.
- References: as needed.

No padding is allowed. If the paper does not naturally reach 20 pages after the expanded evidence, it is not final.

## RAM-Light Execution Strategy

- Run experiments sequentially by suite.
- Stream row-level results to CSV instead of retaining all runs in memory.
- Store full trajectories only for a small named exemplar set.
- Use numpy arrays only inside one rollout at a time.
- Keep seed sweeps compact: aggregate metrics per run and write immediately.
- Use JSON summaries for tables and regenerate figures from CSV.
- Avoid multiprocessing unless needed; quality comes from experimental scope, not parallel RAM usage.

## Final Acceptance Checklist

- At least 20 pages in the compiled manuscript PDF.
- Downloads `01.pdf` is not replaced until the above threshold passes.
- The final PDF is the actual paper, not an audit/status document.
- All new experiments are reproducible from scripts.
- Strong baselines include tuned and oracle/nondeployable upper-bound variants.
- Stress tests include event-estimation, model-mismatch, mode-switch, and large-seed suites.
- Failure cases are reported honestly and visible in the paper.
- Claims are updated to match evidence.
- Docs/logs/reproducibility files are updated.
- Repo is clean after final commit and push.
