# Claims Ledger

| ID | Claim | Status | Evidence plan | Main caveat |
|---|---|---|---|---|
| C1 | In a known linear Kelvin-Voigt contact mode, current force can be reconstructed from a delayed force sample plus current-minus-delayed proprioceptive displacement/velocity. | Formally checkable | `scripts/verify_claims.py` numeric and algebraic residual checks | Fails at mode switches, wrong stiffness/damping, or bad proprioception |
| C2 | A controller that advances delayed force evidence reduces sensitivity of peak force and impulse to sensing latency compared with delayed-force feedback. | Empirical in toy simulator | `scripts/run_experiments.py` latency sweep, mechanism ablation, and 30-seed stress test | 1D local contact model only, not a hardware result |
| C3 | Contact-age target phasing alone is insufficient; in the current simulator it mainly reduces first-contact overshoot after force advancement has already handled latency. | Empirical in toy simulator | `results/summary.json` and `paper/figures/mechanism_ablation.png` | Weakens the original novelty story; must be stated honestly |
| C4 | The relevant broken assumption in much contact-rich control is not just delayed measurement but delayed contact semantics. | Literature-supported argument | 1000-row matrix, 100-paper hostile set, and added 2024-2026 force/tactile policy citations | Based on metadata/abstract sweep plus cited canonical works, not exhaustive full-PDF reading |
| C5 | The mechanism is distinct from generic Smith prediction because it exposes contact event mismatch and marks where local force prediction is valid or invalid. | Conceptual/algorithmic | Novelty boundary map, ablations, formal mode-switch counterexample | Closest reviewers may still view it as a contact-specialized predictor |
| C6 | The method is ready for real robotic deployment. | Unsupported | None | Must not be claimed; paper should say simulation evidence only |
