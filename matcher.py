"""Matching, scoring, and confidence logic for FitGap.

Pipeline (all in-memory; 15 assignments doesn't need a vector DB):

  candidate blurb ──► embed ─┐
                              ├─► cosine similarity ──► semantic_sim
  assignment desc ──► embed ─┘

  candidate blurb ──► keyword skill extraction ──┐
                                                  ├─► |intersect|/|required| ──► skill_overlap
  assignment.required_skills ─────────────────────┘

  combined   = alpha * semantic_sim + (1 - alpha) * skill_overlap
  confidence = min(semantic_sim, skill_overlap)         # conservative
  review     = any(reason fires)

In prod the embedding store maps to Databricks Vector Search; the scoring
and REVIEW logic stays exactly where it is.
"""

from __future__ import annotations

import hashlib
import pickle
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from data import Assignment, CANONICAL_SKILLS


# ---- Tunables -------------------------------------------------------------
# Surfaced at the top so they're easy to find and explain in an interview.

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_PATH = Path(__file__).parent / ".cache" / "embeddings.pkl"

DEFAULT_ALPHA = 1.0             # combined = alpha*sem + (1-alpha)*skill
                                # Set to 1.0 (semantic-only) because the
                                # alpha sweep in eval.py shows it ranks best
                                # on the labeled set. Skill overlap is still
                                # computed for confidence + REVIEW + UI.
LOW_COMBINED_THRESHOLD = 0.40   # below this -> REVIEW: low overall match
SEMANTIC_GAP_THRESHOLD = 0.30   # sem - skill above this -> REVIEW...
WEAK_SKILL_THRESHOLD = 0.50     # ...IF skill_overlap is also below this


# ---- Result container -----------------------------------------------------

@dataclass
class MatchResult:
    assignment: Assignment
    semantic_sim: float
    skill_overlap: float
    combined_score: float
    confidence: float
    matched_required: list[str]
    missing_required: list[str]
    matched_nice: list[str]
    review_flag: bool
    review_reasons: list[str] = field(default_factory=list)


# ---- Skill extraction -----------------------------------------------------

# Split on anything that isn't an ASCII alphanumeric. Keeps the tokenizer
# trivial and language-agnostic enough for the prototype.
_TOKEN_SPLIT = re.compile(r"[^a-z0-9]+")


def extract_skills(blurb: str, vocab: list[str] = CANONICAL_SKILLS) -> set[str]:
    """Extract canonical skills from a free-text blurb.

    Strategy (kept deliberately simple for the prototype):
      - Lowercase the blurb.
      - Single-word, purely-alphanumeric skills ("python", "sap"): tokenize
        the blurb on non-alphanumerics and require an exact token match.
        This avoids "sap" matching inside "saps" or "saphire".
      - Multi-word or punctuated skills ("month-end close", "ci/cd",
        "node.js"): substring check against the lowercased blurb.
    """
    text = blurb.lower()
    tokens = {t for t in _TOKEN_SPLIT.split(text) if t}
    found: set[str] = set()
    for skill in vocab:
        s = skill.lower()
        if s.isalnum():
            if s in tokens:
                found.add(skill)
        else:
            if s in text:
                found.add(skill)
    return found


# ---- Embedding + on-disk cache --------------------------------------------

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    # Lazy-loaded so importing matcher.py is cheap (eval.py / app.py both
    # import it before they need the model).
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _hash_text(text: str) -> str:
    # sha256 hex digest -- stable across processes, unlike Python's built-in
    # hash() (which is salted per interpreter run).
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_cache() -> dict[str, np.ndarray]:
    try:
        with open(CACHE_PATH, "rb") as f:
            cache = pickle.load(f)
        # Defensive: pickle deserialized to something we don't expect.
        if not isinstance(cache, dict):
            return {}
        return cache
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        # Missing or corrupted cache -> start fresh; it'll be rewritten.
        return {}


def _save_cache(cache: dict[str, np.ndarray]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(cache, f)


def embed_texts(texts: list[str], use_cache: bool = True) -> np.ndarray:
    """Embed a list of texts, reusing cached vectors where the text matches.

    The cache is keyed by sha256(text), so identical inputs produce a hit
    even across Streamlit reruns and `python eval.py` invocations.
    """
    cache = _load_cache() if use_cache else {}
    keys = [_hash_text(t) for t in texts]
    missing_idx = [i for i, k in enumerate(keys) if k not in cache]
    if missing_idx:
        model = _get_model()
        new_vecs = model.encode(
            [texts[i] for i in missing_idx],
            convert_to_numpy=True,
            normalize_embeddings=True,  # so cosine == dot product
        )
        for i, vec in zip(missing_idx, new_vecs):
            cache[keys[i]] = vec
        if use_cache:
            _save_cache(cache)
    return np.stack([cache[k] for k in keys])


# ---- Scoring --------------------------------------------------------------

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    # Both sides are L2-normalized at encode time, so dot == cosine.
    # Clip negatives so the score stays in [0, 1] and is safe to blend.
    return float(np.clip(np.dot(a, b), 0.0, 1.0))


def _review(
    combined: float,
    semantic_sim: float,
    skill_overlap: float,
    required: list[str],
) -> tuple[bool, list[str]]:
    """Decide whether this match should be flagged for recruiter review."""
    reasons: list[str] = []
    if combined < LOW_COMBINED_THRESHOLD:
        reasons.append("Low overall match")
    if (
        semantic_sim - skill_overlap > SEMANTIC_GAP_THRESHOLD
        and skill_overlap < WEAK_SKILL_THRESHOLD
    ):
        # The failure mode this whole flag exists for: the blurb *sounds*
        # right but the candidate doesn't actually have the required skills.
        reasons.append("Sounds relevant but missing required skills")
    if required and skill_overlap == 0.0:
        reasons.append("No required skills detected")
    return bool(reasons), reasons


def score_match(
    candidate_vec: np.ndarray,
    assignment: Assignment,
    assignment_vec: np.ndarray,
    candidate_skills: set[str],
    alpha: float = DEFAULT_ALPHA,
) -> MatchResult:
    """Score one candidate against one assignment.

    Embeddings and the candidate skill-set are passed in so we don't redo
    that work per pair -- matters for the eval script and snappy UI.
    """
    required = assignment["required_skills"]
    nice = assignment["nice_to_have"]
    matched_required = sorted(s for s in required if s in candidate_skills)
    missing_required = sorted(s for s in required if s not in candidate_skills)
    matched_nice = sorted(s for s in nice if s in candidate_skills)

    semantic_sim = _cosine(candidate_vec, assignment_vec)
    skill_overlap = (len(matched_required) / len(required)) if required else 0.0
    combined = alpha * semantic_sim + (1 - alpha) * skill_overlap
    confidence = min(semantic_sim, skill_overlap)
    review_flag, review_reasons = _review(
        combined, semantic_sim, skill_overlap, required
    )

    return MatchResult(
        assignment=assignment,
        semantic_sim=semantic_sim,
        skill_overlap=skill_overlap,
        combined_score=combined,
        confidence=confidence,
        matched_required=matched_required,
        missing_required=missing_required,
        matched_nice=matched_nice,
        review_flag=review_flag,
        review_reasons=review_reasons,
    )


def rank_assignments(
    candidate_blurb: str,
    assignments: list[Assignment],
    alpha: float = DEFAULT_ALPHA,
) -> list[MatchResult]:
    """Score every assignment for one candidate, ranked by combined score."""
    # Title + description gives the embedding a bit more signal than the
    # description alone, especially for short descriptions.
    assignment_texts = [f"{a['title']}. {a['description']}" for a in assignments]
    # One batched embed call; the cache makes the assignment side a no-op
    # after first run.
    vectors = embed_texts([candidate_blurb] + assignment_texts)
    cand_vec, asg_vecs = vectors[0], vectors[1:]
    cand_skills = extract_skills(candidate_blurb)

    results = [
        score_match(cand_vec, asg, asg_vec, cand_skills, alpha=alpha)
        for asg, asg_vec in zip(assignments, asg_vecs)
    ]
    results.sort(key=lambda r: r.combined_score, reverse=True)
    return results
