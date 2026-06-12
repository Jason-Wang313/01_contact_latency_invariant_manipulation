# Reviewer Attacks

1. **Attack:** This is just a Smith predictor.
   **Response:** Concede the lineage. The new ablation shows force advancement alone is already nearly latency invariant in the toy simulator, so the paper must not oversell the distinction. The defensible boundary is event-time validity: the controller tracks when local prediction is semantically valid and where it crosses a hybrid contact boundary.
2. **Attack:** Toy 1D contact is too simple.
   **Response:** Agree as limitation. The toy is meant to isolate the broken assumption; claims stop at local linear-contact regimes.
3. **Attack:** No hardware experiments.
   **Response:** Mark as revise/workshop readiness, not submit-ready for a top robotics venue.
4. **Attack:** OpenAlex abstracts are not a real 250-paper deep read.
   **Response:** Be honest: it is an abstract/metadata deep classification. Closest canonical works are discussed directly; full manual reading remains future work.
5. **Attack:** Delay-robust and passivity controllers already handle latency.
   **Response:** Show they handle stability/energy but not necessarily first-contact impulse or semantic mode mismatch.
6. **Attack:** If the model is known, prediction is obvious.
   **Response:** The novelty is not prediction alone; it is choosing contact timing mismatch as the state and writing the controller in contact-age coordinates.
7. **Attack:** If the model is wrong, invariance disappears.
   **Response:** Yes. Include stiffness mismatch and jitter sensitivity; claim approximate invariance under bounded local model error.
8. **Attack:** The method needs current position, so sensing is not really delayed.
   **Response:** Scope the claim: force/tactile contact evidence is delayed, proprioception is assumed faster and timestamped.
9. **Attack:** Contact detection from position requires known wall geometry.
   **Response:** Use this as a hidden assumption and limitation; delayed force edge can calibrate the event-time state across repeated or slowly varying contacts.
10. **Attack:** The paper belongs in control, not ICLR.
   **Response:** Frame it as embodied intelligence/control with runnable evidence; readiness judgment can be workshop/revise if venue fit is weak.
11. **Attack:** Latency invariance is too strong a phrase.
   **Response:** Use 'approximately invariant in local linear-contact regimes' and report the measured latency slope.
12. **Attack:** No learning means not ICLR enough.
   **Response:** Do not bolt on learning. The contribution is a mechanism for embodied agents; submit-readiness can be conservative.
13. **Attack:** Recent visual-tactile and force-aware policies already use fast force/tactile feedback.
   **Response:** Cite recent work explicitly. The paper cannot claim novelty for force/tactile feedback, reactive tactile policies, or predictive tactile world models. Its narrower target is the event-age mismatch created when delayed evidence crosses first contact.
14. **Attack:** Contact-age phasing is not the reason the main curve is flat.
   **Response:** Agree. `force_advance_only` has 9.04 N max peak and zero latency slope in the ideal sweep, while the full method has 8.48 N. The paper should say phasing reduces overshoot after force advancement, not that phasing alone creates invariance.
15. **Attack:** Stress tests are still synthetic.
   **Response:** Agree. The 30-seed stress test perturbs stiffness, damping, servo time constant, initial gap, model estimates, and effective latency, but it is still a local 1D simulator. Decision remains workshop-only / strong-revise for main conference.
