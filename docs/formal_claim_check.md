# Formal Claim Check

The formal claim is intentionally narrow.

For a fixed Kelvin-Voigt contact mode, with true stiffness `k`, damping `c`, current proprioception `(q_t, v_t)`, delayed proprioception `(q_{t-L}, v_{t-L})`, and delayed force `F_{t-L}`, the predictor

`F_hat_t = F_{t-L} + k(q_t - q_{t-L}) + c(v_t - v_{t-L})`

equals the current force `F_t = k q_t + c v_t`, provided both samples are in the same unilateral contact mode and clipping does not change signs.

## Numeric Audit

| Check | Status | Max residual (N) | Mean residual (N) |
|---|---|---:|---:|
| same_contact_mode_linear_kelvin_voigt | passed_with_floating_point_tolerance | 7.10543e-15 | 1.23288e-15 |
| naive_delay_advance_across_mode_switch | counterexample_found | 25.9342 | 0 |
| model_mismatch_bound_needed | not_exact_under_wrong_model | 3.85975 | 1.27686 |

## Adversarial Boundary

- The same-mode linear-contact claim passes to floating-point tolerance.
- Advancing a delayed sample across a mode switch without a contact-timing state produces counterexamples.
- Wrong stiffness/damping makes exact invariance false; the paper may only claim approximate robustness under bounded model error.
