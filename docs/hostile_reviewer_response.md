# Hostile Reviewer Response

## Likely Decision

Workshop accept / main-conference reject unless expanded with multi-DOF or hardware evidence.

## Core Responses

| Reviewer Objection | Response in v2 |
|---|---|
| This is a Smith predictor in contact-control clothing. | Conceded as closest prior. The paper now claims only contact-event timing semantics and validity boundaries for local advancement. |
| Contact-age phasing is not the key mechanism. | Conceded. Ablation shows force advancement alone has 9.04 N max peak and zero latency slope; full method improves to 8.48 N. |
| There is no hardware. | Conceded. The v3 final status is batch-final simulation/mechanism paper, not hardware-ready. |
| The result is a toy simulation. | Conceded. Added stress seeds and uncertainty, but claims remain local. |
| Recent force/tactile policies already solve contact-rich feedback. | Added 2024-2026 citations and narrowed away from broad force/tactile novelty. |
| Exact invariance is brittle. | Formal checker shows same-mode exactness, mode-switch failure, and model-mismatch residuals. |
| Reproducibility is unclear. | README and checklist now identify commands and generated outputs. |

## Claims We Should Not Make

- Do not claim deployment readiness.
- Do not claim novelty for force control, impedance control, Smith prediction, tactile feedback, or contact-rich policy learning.
- Do not claim contact-age phasing alone creates latency invariance.
- Do not claim robustness outside a local contact mode.
