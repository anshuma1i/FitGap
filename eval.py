"""Offline eval for FitGap.

Measures:
  1. Precision@3 per candidate, mean over all 10 candidates.
  2. REVIEW flag correlation with wrong matches (2×2 contingency table).
  3. REVIEW recall / precision on the "wrong" class.

50 hand-labeled (candidate_idx, assignment_id, should_match) pairs —
5 per candidate, ~35% True, ~65% False. Balance reflects real-world:
a recruiter shortlists only a fraction of roles for any given candidate.

Run with: python eval.py
"""

from __future__ import annotations

from collections import Counter

from data import ASSIGNMENTS, CANDIDATES
from matcher import DEFAULT_ALPHA, MatchResult, rank_assignments


# (candidate_index, assignment_id, should_match)
# 50 labeled pairs across 10 candidates, 5 each.
# True  = recruiter would shortlist this candidate for this assignment.
# False = recruiter would not (domain mismatch, missing skills, wrong level).
#
# Label philosophy (documented for interview defence):
#   - Direct title match or adjacent role with core skill overlap -> True
#   - Different domain altogether -> False
#   - Same domain but wrong seniority/specialization -> False (this is where
#     REVIEW flags should ideally fire — hard case for semantic-only ranking)
LABELS: list[tuple[int, str, bool]] = [
    # =====================================================================
    # Candidate 0: Interim Finance Controller
    # =====================================================================
    (0, "ASG-001", True),     # Interim Finance Controller — direct hit
    (0, "ASG-002", True),     # Interim CFO — adjacent, IFRS + stakeholder
    (0, "ASG-003", False),    # SAP FICO — SAP overlap but no ABAP, wrong role
    (0, "ASG-005", False),    # External Auditor — IFRS overlap, audit domain not match
    (0, "ASG-011", False),    # Senior Data Engineer — wrong domain

    # =====================================================================
    # Candidate 1: Financial Planning Analyst
    # =====================================================================
    (1, "ASG-004", True),     # Financial Planning Analyst — direct hit
    (1, "ASG-007", True),     # FP&A Manager — same domain, senior version
    (1, "ASG-002", False),    # Interim CFO — too senior, missing M&A
    (1, "ASG-017", False),    # BI Developer — tool overlap (Power BI) but wrong role
    (1, "ASG-042", False),    # Salesforce Admin — wrong domain

    # =====================================================================
    # Candidate 2: Senior Data Engineer
    # =====================================================================
    (2, "ASG-011", True),     # Senior Data Engineer — direct hit
    (2, "ASG-015", True),     # MLOps Engineer — adjacent infra + data overlap
    (2, "ASG-018", False),    # Data Architect — Snowflake + SQL but missing data modeling focus
    (2, "ASG-017", False),    # BI Developer — SQL overlap, not pipeline engineering
    (2, "ASG-001", False),    # Interim Finance Controller — wrong domain

    # =====================================================================
    # Candidate 3: Machine Learning Engineer
    # =====================================================================
    (3, "ASG-012", True),     # Machine Learning Engineer — direct hit
    (3, "ASG-014", True),     # AI Engineer — adjacent, LLM + Python
    (3, "ASG-020", False),    # NLP Engineer — ML overlap but specialized NLP, no NLP in blurb
    (3, "ASG-013", False),    # Data Scientist — stats + ML overlap but no stats in blurb
    (3, "ASG-031", False),    # DevOps Engineer — wrong domain despite kubernetes

    # =====================================================================
    # Candidate 4: Backend Developer (Java)
    # =====================================================================
    (4, "ASG-022", True),     # Backend Developer (Java/Spring) — direct hit
    (4, "ASG-027", False),    # API Developer (Go) — REST + PG overlap, wrong language
    (4, "ASG-033", False),    # SRE — Kubernetes + CI/CD but wrong primary role
    (4, "ASG-025", False),    # .NET Developer — backend but wrong stack
    (4, "ASG-003", False),    # SAP FICO — wrong domain

    # =====================================================================
    # Candidate 5: Frontend Developer (React)
    # =====================================================================
    (5, "ASG-021", True),     # Frontend Developer (React) — direct hit
    (5, "ASG-023", True),     # Full-Stack (Next.js/Node) — TypeScript + Node overlap
    (5, "ASG-024", False),    # Mobile (React Native) — React overlap, different platform
    (5, "ASG-026", False),    # QA Automation — Cypress overlap but testing role
    (5, "ASG-047", False),    # UX Designer — Figma overlap, wrong primary role

    # =====================================================================
    # Candidate 6: Cloud Architect
    # =====================================================================
    (6, "ASG-032", True),     # Cloud Architect — direct hit
    (6, "ASG-040", True),     # Infrastructure Manager — adjacent leadership, AWS + stakeholder
    (6, "ASG-034", False),    # Platform Engineer — adjacent infra, strong overlap but IC role
    (6, "ASG-006", False),    # Tax Specialist — wrong domain
    (6, "ASG-016", False),    # Data Analyst — wrong domain

    # =====================================================================
    # Candidate 7: DevOps Engineer
    # =====================================================================
    (7, "ASG-031", True),     # DevOps Engineer — direct hit
    (7, "ASG-033", True),     # SRE — adjacent, Kubernetes + Prometheus + CI/CD
    (7, "ASG-037", False),    # Kubernetes Admin — K8s overlap, different role scope
    (7, "ASG-028", False),    # Embedded C++ — wrong domain despite Linux
    (7, "ASG-009", False),    # Payroll Specialist — wrong domain

    # =====================================================================
    # Candidate 8: Technical Product Manager
    # =====================================================================
    (8, "ASG-043", True),     # Product Manager — direct hit (user research + stakeholder)
    (8, "ASG-045", True),     # Technical Program Manager — adjacent TPM
    (8, "ASG-046", False),    # Business Analyst — stakeholder overlap, different role
    (8, "ASG-041", False),    # Agile PM — Jira + stakeholder overlap, not product
    (8, "ASG-005", False),    # External Auditor — wrong domain

    # =====================================================================
    # Candidate 9: Business Analyst
    # =====================================================================
    (9, "ASG-046", True),     # Business Analyst — direct hit
    (9, "ASG-049", True),     # Change Manager — business process + stakeholder overlap
    (9, "ASG-048", False),    # Delivery Lead — stakeholder overlap, more senior delivery role
    (9, "ASG-044", False),    # Scrum Master — Jira overlap, wrong specialty
    (9, "ASG-014", False),    # AI Engineer — wrong domain
]


def _find(results: list[MatchResult], asg_id: str) -> MatchResult:
    for r in results:
        if r.assignment["id"] == asg_id:
            return r
    raise KeyError(asg_id)


def _rank_all(alpha: float) -> dict[int, list[MatchResult]]:
    """Full ranking of every assignment for every candidate at one alpha."""
    return {
        i: rank_assignments(c["blurb"], ASSIGNMENTS, alpha=alpha)
        for i, c in enumerate(CANDIDATES)
    }


def _labeled_candidates() -> list[int]:
    """Candidate indices that have at least one True label in LABELS.

    Skips demo-only candidates added for the UI but not labeled (e.g. the
    AI Strategy Consultant). Otherwise their P@3 would be 0 by construction
    and drag the mean down.
    """
    return sorted({i for i, _, ok in LABELS if ok})


def _truth(i: int) -> set[str]:
    return {asg_id for cand_i, asg_id, ok in LABELS if cand_i == i and ok}


def _reciprocal_rank(ranking: list[MatchResult], truth: set[str]) -> float:
    """Reciprocal rank of the first True-labeled assignment, 0 if none in list."""
    for pos, r in enumerate(ranking, start=1):
        if r.assignment["id"] in truth:
            return 1.0 / pos
    return 0.0


def compute_metrics(rankings: dict[int, list[MatchResult]]) -> dict:
    """All headline numbers for one alpha. Used by the default run and sweep."""
    labeled = _labeled_candidates()

    # Ranking quality -- P@3 has a hard ceiling when |truth| < 3, so MRR
    # is reported alongside it as the cleaner "top hit goodness" metric.
    p3_per_candidate: list[tuple[int, float]] = []
    mrr_per_candidate: list[tuple[int, float]] = []
    for i in labeled:
        truth = _truth(i)
        top3 = [r.assignment["id"] for r in rankings[i][:3]]
        hits = sum(1 for a in top3 if a in truth)
        p3_per_candidate.append((i, hits / 3))
        mrr_per_candidate.append((i, _reciprocal_rank(rankings[i], truth)))

    # REVIEW 2x2 over labeled pairs
    tp = fp = tn = fn = 0
    reason_counts: Counter[str] = Counter()
    pair_rows: list[tuple[int, str, bool, bool, list[str]]] = []
    for cand_i, asg_id, should_match in LABELS:
        r = _find(rankings[cand_i], asg_id)
        flagged = r.review_flag
        pair_rows.append((cand_i, asg_id, should_match, flagged, r.review_reasons))
        for reason in r.review_reasons:
            reason_counts[reason] += 1
        if flagged and not should_match:
            tp += 1
        elif flagged and should_match:
            fp += 1
        elif not flagged and should_match:
            tn += 1
        else:
            fn += 1

    return {
        "p3_per_candidate": p3_per_candidate,
        "mrr_per_candidate": mrr_per_candidate,
        "mean_p3": sum(p for _, p in p3_per_candidate) / len(p3_per_candidate) if p3_per_candidate else 0.0,
        "mean_mrr": sum(m for _, m in mrr_per_candidate) / len(mrr_per_candidate) if mrr_per_candidate else 0.0,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "recall": tp / (tp + fn) if tp + fn else None,
        "precision": tp / (tp + fp) if tp + fp else None,
        "reason_counts": reason_counts,
        "pair_rows": pair_rows,
    }


def main() -> None:
    n_true = sum(1 for _, _, ok in LABELS if ok)
    n_false = sum(1 for _, _, ok in LABELS if not ok)
    n_labeled = len(_labeled_candidates())
    print(f"Eval with alpha={DEFAULT_ALPHA}, {len(LABELS)} labeled pairs "
          f"({n_true} True / {n_false} False) across {n_labeled} candidates\n")

    rankings = _rank_all(DEFAULT_ALPHA)
    m = compute_metrics(rankings)

    # ---- Per-candidate ranking quality ------------------------------------
    print("Per-candidate ranking quality")
    print("-" * 70)
    for (i, p3), (_, mrr) in zip(m["p3_per_candidate"], m["mrr_per_candidate"]):
        truth = _truth(i)
        top3 = [r.assignment["id"] for r in rankings[i][:3]]
        ceiling = min(len(truth), 3) / 3
        print(f"  [{i}] {CANDIDATES[i]['name']:<32s} top3={top3}")
        print(f"       truth={truth}  P@3={p3:.2f} (ceiling {ceiling:.2f})  RR={mrr:.2f}")
    print(f"\nMean P@3:  {m['mean_p3']:.2f}   "
          f"Mean MRR:  {m['mean_mrr']:.2f}")
    print("MRR is the cleaner headline since P@3 is capped at min(|truth|,3)/3.\n")

    # ---- REVIEW 2x2 -------------------------------------------------------
    print("REVIEW flag vs label")
    print("-" * 70)
    print(f"  {'candidate':<32s} {'asg':<10s} {'label':<7s} {'REVIEW':<7s} reasons")
    for cand_i, asg_id, ok, flagged, reasons in m["pair_rows"]:
        reason_str = "; ".join(reasons) if reasons else "-"
        print(f"  {CANDIDATES[cand_i]['name']:<32s} {asg_id:<10s} "
              f"{str(ok):<7s} {str(flagged):<7s} {reason_str}")

    print()
    print(f"  REVIEW caught wrong   (TP): {m['tp']}")
    print(f"  Wrong slipped through (FN): {m['fn']}")
    print(f"  REVIEW on good match  (FP): {m['fp']}")
    print(f"  Good match clean      (TN): {m['tn']}")

    if m["recall"] is not None:
        print(f"\n  Recall on wrong matches    (REVIEW fires when it should): {m['recall']:.2f}")
    else:
        print("\n  Recall on wrong matches: undefined (no wrong matches)")
    if m["precision"] is not None:
        print(f"  Precision of REVIEW        (when it fires, it's right):  {m['precision']:.2f}")
    elif (m["tp"] + m["fn"]) == 0:
        print("  Precision of REVIEW: n/a (all matches correct, no flags)")
    else:
        print("  Precision of REVIEW: n/a (REVIEW never fired despite wrong matches)")

    # ---- REVIEW reason breakdown -----------------------------------------
    # Shows that the three rules each do distinct work, not just one over-firing.
    print("\nREVIEW reason breakdown (independent rule fire counts)")
    print("-" * 70)
    if m["reason_counts"]:
        for reason, count in m["reason_counts"].most_common():
            print(f"  {count:3d}x  {reason}")
    else:
        print("  (no rules fired)")

    # ---- Alpha sweep ------------------------------------------------------
    # Is the blend actually doing work? Compare skill-only / combined / sem-only
    # on the same labels. Reuse the default-alpha numbers we already computed.
    print("\nAlpha sweep: does the blend actually help?")
    print("-" * 70)
    print(f"  {'alpha':<7s} {'label':<22s} {'P@3':<7s} {'MRR':<7s} "
          f"{'REV recall':<12s} {'REV precision':<14s}")
    # Fixed comparison points; default alpha is shown separately at the top.
    sweep = [
        (0.0, "skill-only"),
        (0.5, "mid-blend"),
        (1.0, "semantic-only"),
    ]
    for alpha, label in sweep:
        m_a = m if alpha == DEFAULT_ALPHA else compute_metrics(_rank_all(alpha))
        rec = f"{m_a['recall']:.2f}" if m_a["recall"] is not None else "n/a"
        prec = f"{m_a['precision']:.2f}" if m_a["precision"] is not None else "n/a"
        print(f"  {alpha:<7.2f} {label:<22s} {m_a['mean_p3']:<7.2f} "
              f"{m_a['mean_mrr']:<7.2f} {rec:<12s} {prec:<14s}")


if __name__ == "__main__":
    main()