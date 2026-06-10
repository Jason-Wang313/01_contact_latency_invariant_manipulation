# Novelty Decision

## Chosen Thesis

Contact-rich manipulation should treat contact timing mismatch as an explicit controller state. A controller that reconstructs current contact force by advancing delayed force evidence through the measured proprioceptive displacement and then indexes force ramps by inferred contact age can make first-contact transients approximately invariant to sensing latency in a local linear-contact regime.

## Why This Direction Wins

- It changes the central mechanism from stronger feedback to semantic time alignment across a hybrid event.
- It gives a concrete formal claim under linear contact: delayed force can be exactly advanced when the contact mode and local stiffness/damping are correct.
- It produces a runnable falsifiable experiment: sweep sensing latency and compare peak force/impulse against delayed-force baselines.
- It avoids forbidden weak moves: no bigger model, no RL, no benchmark-only claim, no LLM planner, and no generic uncertainty wrapper.

## Rejected Alternatives

- **Impulse-before-feedback safety filters**: rejected as primary thesis. Strong safety angle, but close to passivity/energy tanks unless the event-time state is central.
- **Latency-calibrating tactile servoing**: rejected as primary thesis. Useful, but risks being perceived as a perception timestamping paper rather than a manipulation mechanism.
- **Hybrid guard predictors for contact planners**: rejected as primary thesis. Good planning contribution, but heavier formal burden and less runnable in this repository.
- **Contact-mode delay adversarial benchmark**: rejected as primary thesis. Forbidden as benchmark-only unless paired with a new mechanism.
- **Delay-aware impedance adaptation**: rejected as primary thesis. Promising but too close to adding adaptation unless the age coordinate is the real contribution.

## Exact Novelty Boundary

The paper does not claim to invent force control, impedance control, delay compensation, passivity, Smith prediction, tactile perception, or contact-mode estimation. It claims a narrower mechanism: for contact-rich controllers, the variable that must be made explicit is the mismatch between when contact physically began and when the controller's evidence says it began. The controller is then written in contact-age coordinates and uses local contact dynamics to advance stale force samples.
