# Plan: Contact Latency Invariant Manipulation

## Objective
Produce a complete, honest robotics/embodied-intelligence paper package for paper 01, including literature artifacts, runnable evidence, an anonymous ICLR-style LaTeX paper, compiled PDF at `C:/Users/wangz/Downloads/01.pdf`, final audit, and a public GitHub push for `01_contact_latency_invariant_manipulation`.

## Operating Rules
- Stay inside the assigned repository except for required output PDF at `C:/Users/wangz/Downloads/01.pdf`.
- Treat all shell probes as fallible; avoid uncaught nonzero exits.
- Keep `child_status.md` compactly updated with stage, exact commands, failures, and recoveries.
- Do not overclaim novelty or evidence; mark unsupported claims explicitly.
- Prefer reproducible scripts over manual artifacts when generating large literature and experiment outputs.

## Execution Stages
1. Initialize status log and inspect repository/tooling safely.
2. Create a reproducible project skeleton: `docs/`, `scripts/`, `src/`, `paper/`, `results/`.
3. Perform the landscape sweep using scholarly APIs/search:
   - collect at least 1000 candidate prior-work entries into `docs/related_work_matrix.csv`;
   - serious-skim 300 entries and deep-read/classify 200-250 entries where metadata/abstracts are available;
   - construct a 100-paper hostile prior-work set.
4. Build synthesis artifacts:
   - `docs/literature_map.md`
   - `docs/hostile_prior_work.md`
   - `docs/novelty_boundary_map.md`
   - `docs/novelty_decision.md`
   - `docs/claims.md`
   - `docs/reviewer_attacks.md`
5. Choose the strongest thesis only after the above synthesis, replacing the seed if warranted.
6. Implement runnable evidence:
   - a minimal contact-rich manipulation timing-mismatch simulator;
   - baseline delayed-contact controller(s);
   - latency-state/invariant controller mechanism;
   - reproducible experiments and plots.
7. Adversarially check formal claims with a small verification script or symbolic/numeric counterexample search where feasible.
8. Fetch/use the latest official ICLR LaTeX template available at runtime, then write a complete anonymous ICLR-style paper.
9. Compile the paper; copy/save final PDF exactly to `C:/Users/wangz/Downloads/01.pdf`.
10. Create/update public GitHub repo `01_contact_latency_invariant_manipulation`, commit complete package, push, and document any failure.
11. Write `docs/final_audit.md` answering all required audit questions, including Desktop-copy status as `pending orchestrator copy` unless an orchestrator result is present.

## Recovery Strategy
- If a scholarly API is unavailable, fall back to arXiv/OpenAlex/Crossref export and document coverage limits.
- If LaTeX tooling is missing, still create complete source and document compile failure with exact command/output.
- If GitHub authentication or repo creation fails, document exact command and failure, leaving the repo locally complete and ready to push.
