# DECISIONS — FitGap

## What it does

A recruiter pastes a candidate blurb. The app ranks 50 open assignments and,
per match, shows: a semantic score, a required-skill overlap score, a
combined score, matched and missing required skills, a confidence number,
and a REVIEW flag with one or more reasons when the match looks off. The
same scoring code is used by the app and the eval script.

## Pipeline

Candidate text is embedded with sentence-transformers and compared by cosine
similarity to each assignment's title+description embedding. Required-skill
overlap is computed by keyword and phrase matching the blurb against an
80-skill canonical vocabulary. The two signals feed a combined score, a
confidence number, and the REVIEW flag.

## Decisions

**1. Embedding model: `sentence-transformers/all-MiniLM-L6-v2`.**
~80 MB, runs on CPU, sentence-level trained, competitive on STS benchmarks.
English-only. For production with Dutch and mixed-language data, replace
with a multilingual model (multilingual-e5 or BGE-m3).

**2. Storage: in-memory cosine over numpy.**
50 assignments does not need a vector database. The `embed_texts` function
is the boundary that maps to Databricks Vector Search in production; the
scoring code above it does not change.

**3. Embedding cache.**
On-disk pickle at `.cache/embeddings.pkl`, keyed by `sha256(text)`. Stable
across processes (unlike Python's built-in `hash()`). Corrupted or missing
files are caught and rebuilt.

**4. Score blend: `combined = α · semantic_sim + (1 − α) · skill_overlap`. Default α = 1.0.**
The alpha sweep (below) shows semantic-only ranks best on the labeled set,
so the default is 1.0. The slider remains in the UI for inspection.
Required-skill overlap is still computed and used for the confidence
number, the matched/missing chips in the UI, and one of the three REVIEW
rules.

**5. Confidence: `min(semantic_sim, skill_overlap)`.**
Confidence is high only when both signals agree. Smoother alternatives
(such as `combined − |semantic_sim − skill_overlap|`) reduce the gap
between the two signals, which is the gap the REVIEW flag is designed to
surface.

**6. REVIEW flag: three independent rules.**
Each rule fires on a distinct failure mode and surfaces a separate reason
on the card:
- Rule A: `combined < 0.40` → "Low overall match".
- Rule B: `semantic_sim − skill_overlap > 0.30` AND `skill_overlap < 0.50` → "Sounds relevant but missing required skills".
- Rule C: required skills exist AND `skill_overlap = 0` → "No required skills detected".

Counts at α = 1.0 over the 50 labeled pairs: A 17, C 12, B 6. Rules can
fire together; each contributes its own reason text.

**7. Skill extraction: keyword and phrase matching against a canonical 80-skill vocabulary.**
The blurb is lowercased. Single-word, alphanumeric skills (`python`, `sap`)
are matched as full tokens after splitting on non-alphanumerics, so `sap`
does not match inside `saps`. Multi-word or punctuated skills (`month-end
close`, `ci/cd`, `node.js`) are substring-matched. Deterministic, easy to
explain, fast.

Known failure mode: literal mismatches. The blurb `"FP&A"` does not extract
`financial planning`. `"financial models"` does not extract `financial
modeling`. This shows up in the eval as a REVIEW flag firing on the FP&A
candidate's correct direct-hit role. Stopgap: an alias map. Production
fix: an LLM or NER-based extractor.

## Eval

50 hand-labeled `(candidate, assignment, should_match)` pairs over 9
candidates. The 10th candidate is the demo trigger and is intentionally
unlabeled. Same scoring code as the app, run across three values of α.

| α    | Mode          | P@3  | MRR  | REVIEW recall | REVIEW precision |
|------|---------------|------|------|---------------|------------------|
| 0.00 | skill-only    | 0.37 | 0.74 | 0.65          | 0.87             |
| 0.50 | mid-blend     | 0.47 | 0.90 | 0.61          | 0.86             |
| 1.00 | semantic-only | 0.50 | 1.00 | 0.58          | 0.86             |

Read:
- Semantic-only ranks best on this set. MRR = 1.00 means the top-1 hit is
  in the truth set for every labeled candidate. Default α is set to 1.0
  on the basis of this result.
- REVIEW recall is highest at skill-only (0.65) and lowest at semantic-only
  (0.58). REVIEW precision is stable across the sweep (~0.86).
- P@3 is bounded above by `min(|truth|, 3) / 3` per candidate. Some
  candidates have 1 or 2 True labels, so their P@3 cannot reach 1.0. MRR
  does not have this ceiling and is the cleaner headline metric.

## Demo trigger

The 10th candidate, `AI Strategy Consultant`, is constructed to fire Rule B
on ASG-014 (AI Engineer). The blurb is heavy on LLM/RAG vocabulary
(producing high semantic similarity to ASG-014) and explicitly non-coding
(producing low skill overlap). At α = 1.0, ASG-014 ranks #1 with
`semantic = 0.64`, `skill = 0.25`, and a single REVIEW reason: "Sounds
relevant but missing required skills". The matched/missing chips show
`llm` matched and `python`, `aws`, `langchain` missing.

## Roadmap

1. LLM or NER skill extractor to replace keyword matching.
2. Multilingual embedding model for Dutch and mixed-language blurbs.
3. Recruiter feedback loop on shortlist accept/reject events; use as a
   ranking and confidence calibration signal.
4. Migration to Databricks Vector Search at the embedding-store boundary
   as the corpus grows past in-memory feasibility.
5. CV PDF parsing pipeline to feed the blurb from an uploaded CV.

## Out of scope

- FAISS, Pinecone, or any vector database: corpus too small.
- LangChain or agent framework: this is a retrieval problem.
- Pytest coverage beyond smoke tests: would add at the `extract_skills` and
  `score_match` boundaries for production.
- Confidence calibration: requires real recruiter accept/reject data.
- A/B harness for embedding models: premature without traffic.

---

Building this to get a feel for how this kind of tech works in the
staffing and recruiting sector, as preparation for the Applied AI
Engineer role at HeadFirst.
