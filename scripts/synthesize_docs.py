#!/usr/bin/env python3
"""Synthesize literature and novelty artifacts from related_work_matrix.csv."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CSV_PATH = DOCS / "related_work_matrix.csv"


HIDDEN_ASSUMPTIONS = [
    "Contact event time is available to the controller when it matters.",
    "A delayed force sample still describes the current contact mode.",
    "Continuous-time delay robustness is enough for hybrid contact transitions.",
    "Sensor latency is fixed, known, or independent of contact events.",
    "Controller clocks, sensor clocks, and actuator clocks are aligned.",
    "The first damaging impulse is small enough to wait for feedback.",
    "Compliance can absorb timing mismatch without changing the task objective.",
    "Contact mode switches are sparse relative to sensing delay.",
    "Contact geometry is known well enough for pre-contact prediction.",
    "Environment stiffness and damping remain stationary across trials.",
    "Friction changes forces but not the timing logic of contact onset.",
    "Tactile processing latency is negligible compared with mechanical transients.",
    "Hybrid guards are evaluated on current state rather than delayed observations.",
    "Passivity margins imply useful force transients, not merely stability.",
    "Learning policies trained with one timing distribution generalize to another.",
    "The safety variable is instantaneous force error rather than impulse accumulated during the blind interval.",
    "The robot can always slow down enough before contact without task loss.",
    "Delayed visual and tactile estimates share the same effective timestamp.",
    "Actuator saturation does not couple with late contact correction.",
    "Thresholded force onset is an unambiguous contact-time estimator.",
    "Contact-rich planning errors are mostly geometric rather than temporal.",
    "A single latency scalar describes a multi-stage sensing pipeline.",
    "Mode estimators can be judged by accuracy without judging phase error.",
    "The controller's state should be indexed by wall-clock time rather than contact age.",
]


PAPER_DIRECTIONS = [
    (
        "Contact-age invariant control",
        "Make contact timing mismatch a state variable and command interaction in inferred contact-age coordinates.",
        "Strongest fit: changes the central mechanism from delayed feedback stabilization to hybrid-event time alignment.",
    ),
    (
        "Impulse-before-feedback safety filters",
        "Constrain the pre-feedback impulse budget using velocity, compliance, and worst-case delay.",
        "Strong safety angle, but close to passivity/energy tanks unless the event-time state is central.",
    ),
    (
        "Latency-calibrating tactile servoing",
        "Estimate the timestamp of tactile frames online and servo on timestamp-corrected contact patches.",
        "Useful, but risks being perceived as a perception timestamping paper rather than a manipulation mechanism.",
    ),
    (
        "Hybrid guard predictors for contact planners",
        "Predict guard crossing times and re-index contact plans by guard residual.",
        "Good planning contribution, but heavier formal burden and less runnable in this repository.",
    ),
    (
        "Contact-mode delay adversarial benchmark",
        "Benchmark policies under mode-correlated sensing delay.",
        "Forbidden as benchmark-only unless paired with a new mechanism.",
    ),
    (
        "Delay-aware impedance adaptation",
        "Adapt impedance based on estimated contact event mismatch and blind-interval impulse.",
        "Promising but too close to adding adaptation unless the age coordinate is the real contribution.",
    ),
]


def load_rows() -> list[dict[str, str]]:
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def safe(value: str, limit: int = 120) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def write_literature_map(rows: list[dict[str, str]]) -> None:
    tiers = Counter(row["skim_tier"] for row in rows)
    buckets = Counter(row["source_query"] for row in rows[:1000])
    years = Counter((row["year"] or "unknown") for row in rows[:1000])
    mechanism_counts: Counter[str] = Counter()
    open_counts: Counter[str] = Counter()
    for row in rows[:1000]:
        for part in row["actual_mechanism_introduced"].split(";"):
            if part.strip():
                mechanism_counts[part.strip()] += 1
        for part in row["what_it_leaves_open"].split("|"):
            if part.strip():
                open_counts[part.strip()] += 1

    path = DOCS / "literature_map.md"
    with path.open("w", encoding="utf-8") as f:
        f.write("# Literature Map\n\n")
        f.write("## Field Box\n\n")
        f.write(
            "This paper sits in contact-rich manipulation and control: force/impedance/admittance control, "
            "hybrid contact dynamics, tactile manipulation, contact-mode estimation, time-delay control, "
            "and passivity/teleoperation. The narrow field box is not generic robot learning; it is the "
            "controller-level question of what a robot should do when the semantic timestamp of contact "
            "evidence is wrong during a physical interaction.\n\n"
        )
        f.write("## Sweep Coverage\n\n")
        f.write(f"- Total rows in matrix: {len(rows)}\n")
        for tier, count in tiers.most_common():
            f.write(f"- {tier}: {count}\n")
        f.write("- Important limitation: rows are extracted from OpenAlex metadata and abstracts. The paper text separately cites and reasons about the closest mechanisms.\n\n")
        f.write("## Query Buckets In The Counted 1000\n\n")
        for bucket, count in buckets.most_common():
            f.write(f"- {bucket}: {count}\n")
        f.write("\n## Year Distribution Snapshot\n\n")
        for year, count in sorted(years.items(), key=lambda kv: kv[0], reverse=True)[:25]:
            f.write(f"- {year}: {count}\n")
        f.write("\n## Mechanism Clusters\n\n")
        for mechanism, count in mechanism_counts.most_common(15):
            f.write(f"- {mechanism}: {count}\n")
        f.write("\n## Repeated Open Gaps\n\n")
        for item, count in open_counts.most_common(12):
            f.write(f"- {item}: {count}\n")
        f.write("\n## Top 50 Deep-Read Candidates\n\n")
        f.write("| Rank | Year | Title | Mechanism | Leaves Open |\n")
        f.write("|---:|---:|---|---|---|\n")
        for row in rows[:50]:
            f.write(
                f"| {row['rank']} | {row['year']} | {safe(row['title'], 90)} | "
                f"{safe(row['actual_mechanism_introduced'], 80)} | {safe(row['what_it_leaves_open'], 90)} |\n"
            )


def write_hostile(rows: list[dict[str, str]]) -> None:
    hostile = [row for row in rows if row["hostile_prior"] == "yes"][:100]
    path = DOCS / "hostile_prior_work.md"
    with path.open("w", encoding="utf-8") as f:
        f.write("# Hostile Prior Work Set\n\n")
        f.write(
            "These are the 100 papers most likely to make the proposed idea look incremental, "
            "because they already address delay, prediction, passivity, impedance/admittance, "
            "force control, tactile contact state, or hybrid contact modes.\n\n"
        )
        f.write("| # | Matrix Rank | Year | Title | Why Hostile | Boundary Left Open |\n")
        f.write("|---:|---:|---:|---|---|---|\n")
        for idx, row in enumerate(hostile, start=1):
            f.write(
                f"| {idx} | {row['rank']} | {row['year']} | {safe(row['title'], 75)} | "
                f"{safe(row['what_it_makes_less_novel'], 90)} | {safe(row['what_it_leaves_open'], 100)} |\n"
            )
        f.write("\n## Hostile Reading Summary\n\n")
        f.write("- Delay-control and Smith-predictor work make generic delay compensation non-novel.\n")
        f.write("- Passivity and wave-variable work make stable delayed force/motion channels non-novel.\n")
        f.write("- Impedance, admittance, and hybrid force/position control make compliant force regulation non-novel.\n")
        f.write("- Tactile manipulation makes contact-state estimation from tactile evidence non-novel.\n")
        f.write("- The remaining boundary is narrower: contact evidence can be delayed across a hybrid event, so the controller should explicitly estimate the mismatch between physical contact age and observation age.\n")


def write_novelty_boundary(rows: list[dict[str, str]]) -> None:
    path = DOCS / "novelty_boundary_map.md"
    with path.open("w", encoding="utf-8") as f:
        f.write("# Novelty Boundary Map\n\n")
        f.write("## Hidden Assumptions That May Be False\n\n")
        for idx, assumption in enumerate(HIDDEN_ASSUMPTIONS, start=1):
            f.write(f"{idx}. {assumption}\n")
        f.write("\n## Directions That Break Assumptions\n\n")
        for name, mechanism, note in PAPER_DIRECTIONS:
            f.write(f"- **{name}**: {mechanism} {note}\n")
        f.write("\n## Boundary Against Prior Work\n\n")
        f.write("| Prior cluster | What is already covered | What remains open |\n")
        f.write("|---|---|---|\n")
        f.write("| Time-delay control | Stability and tracking with delayed measurements or inputs | Hybrid event-time semantics when the delayed sample belongs to a previous contact mode |\n")
        f.write("| Smith predictors | Prediction through known continuous plant dynamics | Contact onset changes the plant model exactly when the delayed force edge arrives |\n")
        f.write("| Passivity/teleoperation | Energy safety under delayed force/motion channels | Stable behavior can still accumulate unacceptable impulse before contact feedback |\n")
        f.write("| Impedance/admittance | Compliant force-motion behavior | Virtual compliance is usually time-indexed, not contact-age-indexed |\n")
        f.write("| Hybrid force/position control | Subspace switching at contact | Switch timing is treated as observable or exogenous |\n")
        f.write("| Tactile contact estimation | Recognize contact state, slip, geometry, and outcome | Tactile frames may be semantically stale during fast contact transitions |\n")
        f.write("| Contact-rich planning/MPC | Optimize through contact models and constraints | Delay-corrupted contact evidence is usually folded into robustness rather than represented as a state |\n")
        f.write("\n## Mechanism That Survives The Boundary\n\n")
        f.write(
            "The surviving mechanism is a contact-timing mismatch state: maintain an estimate of the difference "
            "between physical contact age and observation age, advance delayed contact evidence through a local "
            "contact model when the mode is known, and phase the force objective by inferred contact age. "
            "This is narrower than generic delay compensation and more specific than adding uncertainty.\n"
        )


def write_decision(rows: list[dict[str, str]]) -> None:
    path = DOCS / "novelty_decision.md"
    with path.open("w", encoding="utf-8") as f:
        f.write("# Novelty Decision\n\n")
        f.write("## Chosen Thesis\n\n")
        f.write(
            "Contact-rich manipulation should treat contact timing mismatch as an explicit controller state. "
            "A controller that reconstructs current contact force by advancing delayed force evidence through "
            "the measured proprioceptive displacement and then indexes force ramps by inferred contact age can "
            "make first-contact transients approximately invariant to sensing latency in a local linear-contact regime.\n\n"
        )
        f.write("## Why This Direction Wins\n\n")
        f.write("- It changes the central mechanism from stronger feedback to semantic time alignment across a hybrid event.\n")
        f.write("- It gives a concrete formal claim under linear contact: delayed force can be exactly advanced when the contact mode and local stiffness/damping are correct.\n")
        f.write("- It produces a runnable falsifiable experiment: sweep sensing latency and compare peak force/impulse against delayed-force baselines.\n")
        f.write("- It avoids forbidden weak moves: no bigger model, no RL, no benchmark-only claim, no LLM planner, and no generic uncertainty wrapper.\n\n")
        f.write("## Rejected Alternatives\n\n")
        for name, mechanism, note in PAPER_DIRECTIONS[1:]:
            f.write(f"- **{name}**: rejected as primary thesis. {note}\n")
        f.write("\n## Exact Novelty Boundary\n\n")
        f.write(
            "The paper does not claim to invent force control, impedance control, delay compensation, passivity, "
            "Smith prediction, tactile perception, or contact-mode estimation. It claims a narrower mechanism: "
            "for contact-rich controllers, the variable that must be made explicit is the mismatch between "
            "when contact physically began and when the controller's evidence says it began. The controller is "
            "then written in contact-age coordinates and uses local contact dynamics to advance stale force samples.\n"
        )


def write_claims(rows: list[dict[str, str]]) -> None:
    path = DOCS / "claims.md"
    with path.open("w", encoding="utf-8") as f:
        f.write("# Claims Ledger\n\n")
        f.write("| ID | Claim | Status | Evidence plan | Main caveat |\n")
        f.write("|---|---|---|---|---|\n")
        f.write("| C1 | In a known linear Kelvin-Voigt contact mode, current force can be reconstructed from a delayed force sample plus current-minus-delayed proprioceptive displacement/velocity. | Formally checkable | `scripts/verify_claims.py` numeric and algebraic residual checks | Fails at mode switches, wrong stiffness/damping, or bad proprioception |\n")
        f.write("| C2 | A contact-age indexed controller reduces sensitivity of peak force and impulse to sensing latency compared with delayed-force feedback. | Empirical in toy simulator | `scripts/run_experiments.py` latency sweep plots and CSV | 1D local contact model only, not a hardware result |\n")
        f.write("| C3 | The relevant broken assumption in much contact-rich control is not just delayed measurement but delayed contact semantics. | Literature-supported argument | 1000-row matrix and 100-paper hostile set | Based on metadata/abstract sweep plus cited canonical works, not exhaustive full-PDF reading |\n")
        f.write("| C4 | The mechanism is distinct from generic Smith prediction because it estimates contact event mismatch and phases force objectives by contact age. | Conceptual/algorithmic | Novelty boundary map and ablations | Closest reviewers may still view it as a contact-specialized predictor |\n")
        f.write("| C5 | The method is ready for real robotic deployment. | Unsupported | None | Must not be claimed; paper should say simulation evidence only |\n")


def write_attacks(rows: list[dict[str, str]]) -> None:
    path = DOCS / "reviewer_attacks.md"
    with path.open("w", encoding="utf-8") as f:
        f.write("# Reviewer Attacks\n\n")
        attacks = [
            ("This is just a Smith predictor.", "Concede the lineage. Distinguish the event-time residual and contact-age objective phasing; add ablation showing predictor without age phasing is weaker."),
            ("Toy 1D contact is too simple.", "Agree as limitation. The toy is meant to isolate the broken assumption; claims stop at local linear-contact regimes."),
            ("No hardware experiments.", "Mark as revise/workshop readiness, not submit-ready for a top robotics venue."),
            ("OpenAlex abstracts are not a real 250-paper deep read.", "Be honest: it is an abstract/metadata deep classification. Closest canonical works are discussed directly; full manual reading remains future work."),
            ("Delay-robust and passivity controllers already handle latency.", "Show they handle stability/energy but not necessarily first-contact impulse or semantic mode mismatch."),
            ("If the model is known, prediction is obvious.", "The novelty is not prediction alone; it is choosing contact timing mismatch as the state and writing the controller in contact-age coordinates."),
            ("If the model is wrong, invariance disappears.", "Yes. Include stiffness mismatch and jitter sensitivity; claim approximate invariance under bounded local model error."),
            ("The method needs current position, so sensing is not really delayed.", "Scope the claim: force/tactile contact evidence is delayed, proprioception is assumed faster and timestamped."),
            ("Contact detection from position requires known wall geometry.", "Use this as a hidden assumption and limitation; delayed force edge can calibrate the event-time state across repeated or slowly varying contacts."),
            ("The paper belongs in control, not ICLR.", "Frame it as embodied intelligence/control with runnable evidence; readiness judgment can be workshop/revise if venue fit is weak."),
            ("Latency invariance is too strong a phrase.", "Use 'approximately invariant in local linear-contact regimes' and report the measured latency slope."),
            ("No learning means not ICLR enough.", "Do not bolt on learning. The contribution is a mechanism for embodied agents; submit-readiness can be conservative."),
        ]
        for idx, (attack, response) in enumerate(attacks, start=1):
            f.write(f"{idx}. **Attack:** {attack}\n")
            f.write(f"   **Response:** {response}\n")


def main() -> int:
    if not CSV_PATH.exists():
        print(f"missing {CSV_PATH}; run collect_literature.py first")
        return 0
    rows = load_rows()
    write_literature_map(rows)
    write_hostile(rows)
    write_novelty_boundary(rows)
    write_decision(rows)
    write_claims(rows)
    write_attacks(rows)
    print(f"synthesized_docs={DOCS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
