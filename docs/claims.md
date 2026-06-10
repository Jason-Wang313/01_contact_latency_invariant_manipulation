# Claims Ledger

| ID | Claim | Status | Evidence plan | Main caveat |
|---|---|---|---|---|
| C1 | In a known linear Kelvin-Voigt contact mode, current force can be reconstructed from a delayed force sample plus current-minus-delayed proprioceptive displacement/velocity. | Formally checkable | `scripts/verify_claims.py` numeric and algebraic residual checks | Fails at mode switches, wrong stiffness/damping, or bad proprioception |
| C2 | A contact-age indexed controller reduces sensitivity of peak force and impulse to sensing latency compared with delayed-force feedback. | Empirical in toy simulator | `scripts/run_experiments.py` latency sweep plots and CSV | 1D local contact model only, not a hardware result |
| C3 | The relevant broken assumption in much contact-rich control is not just delayed measurement but delayed contact semantics. | Literature-supported argument | 1000-row matrix and 100-paper hostile set | Based on metadata/abstract sweep plus cited canonical works, not exhaustive full-PDF reading |
| C4 | The mechanism is distinct from generic Smith prediction because it estimates contact event mismatch and phases force objectives by contact age. | Conceptual/algorithmic | Novelty boundary map and ablations | Closest reviewers may still view it as a contact-specialized predictor |
| C5 | The method is ready for real robotic deployment. | Unsupported | None | Must not be claimed; paper should say simulation evidence only |
