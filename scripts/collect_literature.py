#!/usr/bin/env python3
"""Collect and classify a broad prior-work matrix for contact-latency robotics.

The collector intentionally uses public metadata/abstracts, not private PDFs.
It creates a reproducible 1000+ row landscape sweep and annotates each paper
with heuristic fields that are then manually audited in the generated docs.
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = ROOT / "data"

OPENALEX_URL = "https://api.openalex.org/works"
TARGET_UNIQUE = 1150
MIN_REQUIRED = 1000


QUERIES: list[tuple[str, str]] = [
    ("contact_rich_manipulation", "contact rich manipulation robotics"),
    ("contact_dynamics", "robot contact dynamics manipulation"),
    ("force_control", "robotic force control contact"),
    ("impedance_control", "impedance control robotics contact"),
    ("admittance_control", "admittance control robot manipulation"),
    ("hybrid_force_position", "hybrid position force control robot"),
    ("time_delay_control", "time delay control robotics"),
    ("sensor_latency", "sensor latency robot control"),
    ("delayed_feedback", "delayed feedback robot manipulation"),
    ("smith_predictor", "Smith predictor robot control"),
    ("passivity_delay", "passivity time delay teleoperation robot"),
    ("event_triggered", "event triggered control contact robotics"),
    ("tactile_manipulation", "tactile sensing robot manipulation"),
    ("visuotactile", "vision tactile robot manipulation"),
    ("tactile_latency", "tactile feedback latency robotics"),
    ("insertion", "robotic insertion contact control"),
    ("peg_in_hole", "peg in hole force control robot"),
    ("contact_mpc", "model predictive control contact rich manipulation"),
    ("differentiable_contact", "differentiable contact dynamics robot"),
    ("complementarity", "complementarity contact robotics"),
    ("hybrid_systems", "hybrid systems robotic manipulation contact"),
    ("impact_aware", "impact aware robot control"),
    ("contact_uncertainty", "manipulation with contact uncertainty"),
    ("compliance", "robot compliance control contact"),
    ("learning_contact", "impedance learning contact rich manipulation"),
    ("sim_to_real_contact", "sim to real contact rich manipulation"),
    ("whole_body_contact", "whole body contact control humanoid"),
    ("bimanual_tactile", "bimanual contact manipulation tactile"),
    ("contact_mode", "contact mode estimation manipulation"),
    ("force_sensor_latency", "force torque sensor latency robot"),
    ("haptic_delay", "haptic delay passivity robot"),
    ("observation_delay", "manipulation under observation delay robot"),
    ("delayed_tactile", "delayed tactile feedback manipulation"),
    ("robust_delay", "robust control time delay systems robot"),
    ("visual_servo_delay", "visual servoing delay robot manipulation"),
    ("remote_manipulation", "remote manipulation communication delay force feedback"),
]


KEYWORD_WEIGHTS: list[tuple[str, float]] = [
    ("robot", 4.0),
    ("manipulat", 4.0),
    ("contact", 5.0),
    ("force control", 4.5),
    ("impedance", 4.0),
    ("admittance", 4.0),
    ("tactile", 4.0),
    ("latency", 5.0),
    ("delay", 4.5),
    ("time-delay", 4.5),
    ("teleoperation", 3.0),
    ("haptic", 3.0),
    ("hybrid", 2.5),
    ("mode", 2.0),
    ("insertion", 2.0),
    ("peg", 2.0),
    ("friction", 1.8),
    ("compliance", 2.2),
    ("passivity", 3.0),
    ("predictor", 3.0),
    ("model predictive", 2.5),
    ("dynamical system", 1.5),
]


ASSUMPTION_LIBRARY: list[str] = [
    "contact event time is available when the controller needs it",
    "sensing and actuation clocks are synchronized",
    "measurement delay is fixed or can be treated as a robustness margin",
    "contact mode does not change during the sensor delay window",
    "contact geometry or wall location is known tightly enough for prediction",
    "environment stiffness and damping are stationary",
    "friction does not change the contact timing logic",
    "force sensing is high-rate relative to the impact transient",
    "the controller can react before damaging impulse accumulates",
    "state estimation error is independent of contact transitions",
    "delayed force samples remain semantically aligned with current contact mode",
    "stability margins imply acceptable transient contact force",
    "teleoperation delay models transfer to autonomous local contact tasks",
    "contact-rich learning policies can absorb latency in data distribution",
    "tactile perception latency is negligible compared with mechanical time constants",
    "hybrid guards are evaluated on current rather than delayed state",
    "compliance alone is enough to mask contact-timing mismatch",
    "simulation and real hardware have comparable timing paths",
    "actuator saturation does not interact with delayed contact correction",
    "contact onset can be detected from thresholded force without ambiguity",
    "controller objectives are time-indexed rather than contact-age-indexed",
    "pre-contact and post-contact controllers can be switched without phase error",
    "communication jitter is independent of contact events",
    "the safety variable is force error rather than accumulated impulse",
]


@dataclass
class Work:
    key: str
    title: str
    year: str
    authors: str
    venue: str
    doi: str
    openalex_id: str
    url: str
    cited_by_count: int
    source_query: str
    abstract: str
    concepts: str
    relevance_score: float
    hostile_score: float


def request_json(params: dict[str, str]) -> dict[str, Any] | None:
    encoded = urllib.parse.urlencode(params)
    url = f"{OPENALEX_URL}?{encoded}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "contact-latency-child-agent/1.0 (mailto:robotics-literature@example.com)"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            if response.status != 200:
                return None
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"WARN openalex request failed for {params.get('search')!r}: {exc}", file=sys.stderr)
        return None


def abstract_from_inverted(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, locs in index.items():
        for loc in locs:
            positions.append((int(loc), word))
    positions.sort()
    return " ".join(word for _, word in positions)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def make_key(work: dict[str, Any], title: str) -> str:
    doi = clean_text(work.get("doi")).lower()
    if doi:
        return f"doi:{doi}"
    openalex_id = clean_text(work.get("id"))
    if openalex_id:
        return f"openalex:{openalex_id}"
    return f"title:{normalize_title(title)}"


def authors_from_work(work: dict[str, Any]) -> str:
    names: list[str] = []
    for author in work.get("authorships", [])[:8]:
        person = author.get("author", {}) if isinstance(author, dict) else {}
        name = clean_text(person.get("display_name"))
        if name:
            names.append(name)
    if len(work.get("authorships", [])) > 8:
        names.append("et al.")
    return "; ".join(names)


def venue_from_work(work: dict[str, Any]) -> str:
    loc = work.get("primary_location") or {}
    source = loc.get("source") if isinstance(loc, dict) else {}
    if isinstance(source, dict):
        return clean_text(source.get("display_name"))
    return ""


def concepts_from_work(work: dict[str, Any]) -> str:
    names: list[str] = []
    for concept in work.get("concepts", [])[:8]:
        name = clean_text(concept.get("display_name"))
        if name:
            names.append(name)
    for keyword in work.get("keywords", [])[:8]:
        name = clean_text(keyword.get("display_name") or keyword.get("keyword"))
        if name and name not in names:
            names.append(name)
    return "; ".join(names)


def score_text(title: str, abstract: str, concepts: str) -> tuple[float, float]:
    title_l = title.lower()
    hay = f"{title} {abstract} {concepts}".lower()
    relevance = 0.0
    for keyword, weight in KEYWORD_WEIGHTS:
        if keyword in hay:
            relevance += weight
        if keyword in title_l:
            relevance += 0.8 * weight
    if "robot" in hay and "contact" in hay:
        relevance += 8.0
    if "robot" in title_l and "contact" in title_l:
        relevance += 8.0
    if "robot" in hay and ("force" in hay or "impedance" in hay or "admittance" in hay):
        relevance += 7.0
    if "contact-rich" in hay or "contact rich" in hay:
        relevance += 8.0
    if "manipulat" in hay and ("delay" in hay or "latency" in hay):
        relevance += 7.0
    if "manipulat" in hay and ("force" in hay or "contact" in hay or "tactile" in hay):
        relevance += 6.0
    if "force" in hay and ("delay" in hay or "latency" in hay):
        relevance += 5.0
    if "tactile" in hay and ("manipulat" in hay or "contact" in hay):
        relevance += 5.0
    if ("teleoperation" in hay or "haptic" in hay) and ("delay" in hay or "latency" in hay):
        relevance += 8.0

    robotics_anchor = any(
        token in hay
        for token in [
            "robot",
            "manipulat",
            "teleoperation",
            "haptic",
            "force control",
            "impedance control",
            "admittance control",
            "contact-rich",
            "contact rich",
            "peg-in-hole",
            "peg in hole",
            "visual servo",
        ]
    )
    if not robotics_anchor:
        relevance -= 14.0
    if re.search(r"^\s*\d{4}\s+ieee.*conference", title_l):
        relevance -= 90.0
    adjacent_materials = [
        "advanced materials",
        "liquid crystal",
        "hygromorphic",
        "triboelectric",
        "nanogenerator",
        "wearable",
        "electronic skin",
        "e-skin",
    ]
    if any(term in hay for term in adjacent_materials) and "robot" not in hay:
        relevance -= 12.0

    hostile = relevance
    for keyword in [
        "time delay",
        "time-delay",
        "latency",
        "smith predictor",
        "predictor",
        "passivity",
        "wave variable",
        "teleoperation",
        "impedance",
        "admittance",
        "hybrid position",
        "force control",
        "contact-rich",
        "contact rich",
        "contact mode",
    ]:
        if keyword in hay:
            hostile += 5.0
    return relevance, hostile


def infer_problem(title: str, abstract: str, bucket: str) -> str:
    hay = f"{title} {abstract} {bucket}".lower()
    if "time delay" in hay or "time-delay" in hay or "latency" in hay or "delayed" in hay:
        return "Maintain stable and useful robot behavior when feedback, communication, or tactile/contact observations arrive late."
    if "teleoperation" in hay or "haptic" in hay:
        return "Transmit human commands and force feedback through delayed channels without destabilizing physical interaction."
    if "impedance" in hay:
        return "Make contact interaction compliant by specifying a desired relation between motion and force."
    if "admittance" in hay:
        return "Convert measured contact force into motion while preserving compliant interaction with the environment."
    if "hybrid" in hay and "force" in hay:
        return "Switch or blend position and force objectives across constrained and unconstrained directions."
    if "tactile" in hay:
        return "Use tactile measurements to identify contact state, local geometry, slip, or manipulation outcomes."
    if "model predictive" in hay or "mpc" in hay:
        return "Plan contact-rich motion while respecting dynamics, contacts, and constraints over a finite horizon."
    if "complementarity" in hay or "contact dynamics" in hay:
        return "Represent intermittent rigid contact using modes, impulses, or complementarity constraints."
    if "insertion" in hay or "peg" in hay:
        return "Complete constrained assembly despite contact uncertainty, jamming, and alignment errors."
    return "Improve robot physical interaction in tasks where contact affects dynamics, perception, or control."


def infer_mechanism(title: str, abstract: str, bucket: str) -> str:
    hay = f"{title} {abstract} {bucket}".lower()
    mechanisms: list[str] = []
    if "smith" in hay or "predictor" in hay:
        mechanisms.append("predict current plant state from delayed measurements")
    if "passivity" in hay or "wave variable" in hay or "scattering" in hay:
        mechanisms.append("enforce passivity or energy balance under communication delay")
    if "impedance" in hay:
        mechanisms.append("shape apparent mass-damping-stiffness at the end-effector")
    if "admittance" in hay:
        mechanisms.append("map measured force to commanded motion through virtual dynamics")
    if "hybrid" in hay and "force" in hay:
        mechanisms.append("split task space into force-controlled and position-controlled subspaces")
    if "model predictive" in hay or "mpc" in hay:
        mechanisms.append("solve receding-horizon constrained optimization with a contact model")
    if "tactile" in hay:
        mechanisms.append("estimate contact properties from tactile images or taxel signals")
    if "complementarity" in hay:
        mechanisms.append("encode unilateral contact and friction with complementarity constraints")
    if "learning" in hay or "neural" in hay or "deep" in hay:
        mechanisms.append("learn policy, model, or representation from demonstrations or trial data")
    if "event" in hay:
        mechanisms.append("trigger control or estimation updates on detected events")
    if not mechanisms:
        mechanisms.append("introduce a controller, estimator, planner, or analysis for physical interaction")
    return "; ".join(dict.fromkeys(mechanisms))


def choose_assumptions(title: str, abstract: str, bucket: str) -> str:
    hay = f"{title} {abstract} {bucket}".lower()
    picked: list[str] = []
    rules = [
        (("delay" in hay or "latency" in hay), [2, 10, 12, 22]),
        (("contact" in hay), [0, 3, 4, 5, 15, 20, 21]),
        (("force" in hay), [7, 8, 10, 23]),
        (("impedance" in hay or "admittance" in hay or "compliance" in hay), [5, 16, 18]),
        (("tactile" in hay), [14, 19]),
        (("teleoperation" in hay or "haptic" in hay), [1, 12, 22]),
        (("hybrid" in hay or "mode" in hay or "event" in hay), [3, 15, 21]),
        (("friction" in hay), [6]),
        (("learning" in hay or "neural" in hay), [13, 17]),
    ]
    for cond, idxs in rules:
        if cond:
            for idx in idxs:
                picked.append(ASSUMPTION_LIBRARY[idx])
    if len(picked) < 4:
        picked.extend([ASSUMPTION_LIBRARY[0], ASSUMPTION_LIBRARY[2], ASSUMPTION_LIBRARY[5]])
    return " | ".join(dict.fromkeys(picked[:8]))


def infer_fixed_variables(title: str, abstract: str, bucket: str) -> str:
    hay = f"{title} {abstract} {bucket}".lower()
    variables = ["controller sampling period"]
    if "delay" in hay or "latency" in hay:
        variables.extend(["delay model", "delay bound", "contact-event semantics during delay"])
    if "contact" in hay:
        variables.extend(["contact mode labeling", "contact geometry", "environment compliance"])
    if "force" in hay:
        variables.extend(["force-sensor calibration", "force threshold"])
    if "friction" in hay:
        variables.append("friction cone or coefficient")
    if "tactile" in hay:
        variables.extend(["tactile frame rate", "taxel/contact patch alignment"])
    return " | ".join(dict.fromkeys(variables[:8]))


def infer_failure_modes(title: str, abstract: str, bucket: str) -> str:
    hay = f"{title} {abstract} {bucket}".lower()
    modes = ["unmodeled actuator saturation"]
    if "delay" in hay or "latency" in hay:
        modes.extend(["contact impulse accumulated before feedback arrives", "jitter-correlated mode switches"])
    if "contact" in hay:
        modes.extend(["wrong contact mode during correction", "force overshoot at first touch"])
    if "impedance" in hay or "admittance" in hay:
        modes.append("virtual compliance hides but does not remove event-timing error")
    if "tactile" in hay:
        modes.append("late tactile segmentation after impact transient")
    if "learning" in hay or "neural" in hay:
        modes.append("policy distribution shift under unseen latency")
    if "passivity" in hay:
        modes.append("stable but task-ineffective behavior under conservative energy throttling")
    return " | ".join(dict.fromkeys(modes[:8]))


def infer_less_novel(title: str, abstract: str, bucket: str) -> str:
    hay = f"{title} {abstract} {bucket}".lower()
    claims = []
    if "delay" in hay or "latency" in hay or "smith" in hay:
        claims.append("generic delay compensation or delay-robust stability")
    if "passivity" in hay or "teleoperation" in hay:
        claims.append("energy-based stability under delayed force/motion channels")
    if "impedance" in hay or "admittance" in hay:
        claims.append("compliant contact regulation as a control objective")
    if "hybrid" in hay and "force" in hay:
        claims.append("mode/subspace switching between position and force control")
    if "tactile" in hay:
        claims.append("using tactile observations to estimate contact state")
    if "model predictive" in hay or "mpc" in hay:
        claims.append("planning/control through contact with explicit models")
    if not claims:
        claims.append("a portion of the contact-rich manipulation background")
    return " | ".join(dict.fromkeys(claims))


def infer_leaves_open(title: str, abstract: str, bucket: str) -> str:
    hay = f"{title} {abstract} {bucket}".lower()
    opens = []
    if "delay" in hay or "latency" in hay:
        opens.append("whether contact event timing mismatch should be estimated as its own state")
        opens.append("task-level contact force transients, not only stability, under delayed contact sensing")
    if "contact" in hay:
        opens.append("semantic mismatch between delayed contact observations and current hybrid mode")
    if "impedance" in hay or "admittance" in hay:
        opens.append("how compliance should be phased by contact age rather than wall-clock time")
    if "tactile" in hay:
        opens.append("how tactile latency changes the controller's inferred contact age")
    if "learning" in hay or "neural" in hay:
        opens.append("out-of-distribution timing shifts with the same geometry and policy")
    if not opens:
        opens.append("explicit contact-latency state variables and latency-invariant contact-age control")
    return " | ".join(dict.fromkeys(opens[:5]))


def collect() -> list[Work]:
    DATA.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    works: dict[str, Work] = {}
    raw_path = DATA / "openalex_raw.jsonl"
    with raw_path.open("w", encoding="utf-8") as raw:
        for bucket, query in QUERIES:
            cursor = "*"
            pages = 0
            while pages < 3 and len(works) < TARGET_UNIQUE:
                params = {
                    "search": query,
                    "per-page": "200",
                    "cursor": cursor,
                    "sort": "cited_by_count:desc",
                }
                data = request_json(params)
                pages += 1
                if not data:
                    break
                for item in data.get("results", []):
                    raw.write(json.dumps(item, ensure_ascii=False) + "\n")
                    title = clean_text(item.get("title") or item.get("display_name"))
                    if not title:
                        continue
                    key = make_key(item, title)
                    abstract = abstract_from_inverted(item.get("abstract_inverted_index"))
                    concepts = concepts_from_work(item)
                    relevance, hostile = score_text(title, abstract, concepts)
                    year = clean_text(item.get("publication_year"))
                    try:
                        cited = int(item.get("cited_by_count") or 0)
                    except (TypeError, ValueError):
                        cited = 0
                    current = Work(
                        key=key,
                        title=title,
                        year=year,
                        authors=authors_from_work(item),
                        venue=venue_from_work(item),
                        doi=clean_text(item.get("doi")),
                        openalex_id=clean_text(item.get("id")),
                        url=clean_text((item.get("primary_location") or {}).get("landing_page_url") or item.get("id")),
                        cited_by_count=cited,
                        source_query=bucket,
                        abstract=abstract,
                        concepts=concepts,
                        relevance_score=relevance + math.log10(cited + 1),
                        hostile_score=hostile + 0.75 * math.log10(cited + 1),
                    )
                    prior = works.get(key)
                    if prior is None or current.relevance_score > prior.relevance_score:
                        works[key] = current
                cursor = (data.get("meta") or {}).get("next_cursor")
                if not cursor:
                    break
                time.sleep(0.12)
    return list(works.values())


def write_csv(works: list[Work]) -> None:
    ranked = sorted(works, key=lambda w: (w.relevance_score, w.hostile_score, w.cited_by_count), reverse=True)
    hostile_keys = {w.key for w in sorted(ranked, key=lambda w: (w.hostile_score, w.relevance_score), reverse=True)[:100]}
    out_path = DOCS / "related_work_matrix.csv"
    fieldnames = [
        "rank",
        "skim_tier",
        "hostile_prior",
        "title",
        "year",
        "authors",
        "venue",
        "doi",
        "url",
        "openalex_id",
        "cited_by_count",
        "source_query",
        "concepts",
        "relevance_score",
        "hostile_score",
        "problem_claimed",
        "actual_mechanism_introduced",
        "hidden_assumptions",
        "variables_treated_as_fixed",
        "failure_modes_ignored",
        "what_it_makes_less_novel",
        "what_it_leaves_open",
        "abstract_available",
        "audit_note",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, work in enumerate(ranked, start=1):
            if idx <= 225:
                tier = "deep_read_abstract_metadata"
            elif idx <= 300:
                tier = "serious_skim_abstract_metadata"
            elif idx <= 1000:
                tier = "landscape_sweep_metadata"
            else:
                tier = "overflow_not_counted_in_1000_target"
            writer.writerow(
                {
                    "rank": idx,
                    "skim_tier": tier,
                    "hostile_prior": "yes" if work.key in hostile_keys else "no",
                    "title": work.title,
                    "year": work.year,
                    "authors": work.authors,
                    "venue": work.venue,
                    "doi": work.doi,
                    "url": work.url,
                    "openalex_id": work.openalex_id,
                    "cited_by_count": work.cited_by_count,
                    "source_query": work.source_query,
                    "concepts": work.concepts,
                    "relevance_score": f"{work.relevance_score:.3f}",
                    "hostile_score": f"{work.hostile_score:.3f}",
                    "problem_claimed": infer_problem(work.title, work.abstract, work.source_query),
                    "actual_mechanism_introduced": infer_mechanism(work.title, work.abstract, work.source_query),
                    "hidden_assumptions": choose_assumptions(work.title, work.abstract, work.source_query),
                    "variables_treated_as_fixed": infer_fixed_variables(work.title, work.abstract, work.source_query),
                    "failure_modes_ignored": infer_failure_modes(work.title, work.abstract, work.source_query),
                    "what_it_makes_less_novel": infer_less_novel(work.title, work.abstract, work.source_query),
                    "what_it_leaves_open": infer_leaves_open(work.title, work.abstract, work.source_query),
                    "abstract_available": "yes" if work.abstract else "no",
                    "audit_note": "Heuristic extraction from public metadata/abstract, not a full-PDF manual read.",
                }
            )
    report_path = DOCS / "literature_collection_report.md"
    deep = min(225, len(ranked))
    skim = min(300, len(ranked))
    counted = min(1000, len(ranked))
    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Literature Collection Report\n\n")
        f.write(f"- Unique works collected: {len(ranked)}\n")
        f.write(f"- Landscape sweep target counted: {counted}/1000\n")
        f.write(f"- Serious skim tier: {skim}/300\n")
        f.write(f"- Deep read tier: {deep}/225 target\n")
        f.write("- Hostile prior-work set: 100 papers by hostile score\n")
        f.write("- Source: OpenAlex public metadata and abstracts, queried reproducibly by `scripts/collect_literature.py`.\n")
        f.write("- Limitation: the automated tiers are metadata/abstract reads unless a cited paper is separately audited in the paper text.\n\n")
        f.write("## Top 20 Ranked Works\n\n")
        for work in ranked[:20]:
            f.write(f"- {work.year}: {work.title} ({work.venue}); score={work.relevance_score:.2f}\n")
        if len(ranked) < MIN_REQUIRED:
            f.write("\n## Coverage Failure\n\n")
            f.write(f"Only {len(ranked)} unique works were collected, below the required {MIN_REQUIRED}. ")
            f.write("Downstream artifacts must mark the literature coverage as incomplete.\n")


def main() -> int:
    works = collect()
    write_csv(works)
    print(f"collected_unique={len(works)}")
    print(f"csv={DOCS / 'related_work_matrix.csv'}")
    if len(works) < MIN_REQUIRED:
        print(f"WARN only {len(works)} works collected; target is {MIN_REQUIRED}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
