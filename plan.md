This is a strong start. The separation you’ve drawn—Customer Agent (UX), Analysis Engine (math), Deal Finder (sourcing)—maps well to how valuation systems are built in practice. Below I’ll (1) highlight what’s good, (2) suggest targeted upgrades, and (3) give you ready‑to‑paste Copilot prompt packs for each agent plus a simple orchestrator and shared schemas. Everything stays non‑ML for v0; math and rules stay deterministic and auditable.

1) What’s strong already

Clear roles: UI vs. deterministic math vs. sourcing/alerts.

Knowledge files: keeping terminology and interpretability close to the Customer Agent is key.

ATTOM integration: good choice for property details, comps, and market stats.

Specialized schemas: you’re thinking in the right direction for structure and guardrails.

2) High‑impact upgrades (focused + practical)

Centralize the math in a shared valuation library (pure functions).
Let the Analysis Engine call this library so the LLM never “does math”—it only orchestrates.

Confidence & range by design.
Return weighted median as the point estimate and a MAD‑based band. Include the full adjustment log per comp.

Data provenance + auditability.
For every estimate, store: raw comps, time‑factor used, feature deltas, total adjustments, and final adjusted price. This becomes your “explain my price” trail.

Guardrails & compliance.

Non‑lending disclaimer; bias/fair‑housing language (no steering, no protected‑class inferences).

Input validation (e.g., reject GLA ≤ 0), and conspicuous handling of low confidence (few comps or massive adjustments).

Deal Finder realism.
Start rule‑based: scans pull candidates, compute quick valuations using the same library, rank by discount to model value, cap rate, and confidence. No ML necessary.

Coordination contract.
Define message schemas and tool/function signatures for agent hand‑offs. Avoid free‑form text between agents.

3) Shared data model (single source of truth)

Use this schema across all agents (matches your plan and keeps codegen consistent):

// Money in USD, areas in square feet, distances in miles.
{
  "PropertySnapshot": {
    "gla_sf": "number>0",
    "beds": "integer>=0",
    "baths": {"full": "integer>=0", "half": "integer>=0"},
    "lot_sf": "number>=0",
    "garage_spaces": "integer>=0",
    "condition": "poor|fair|average|good|excellent",
    "quality": "economy|standard|above_avg|premium|luxury",
    "features": {
      "pool": "boolean",
      "adu": "boolean",
      "view_score": "number in [0,1]",
      "busy_road": "boolean"
    }
  },
  "SubjectInput": {
    "valuation_date": "ISO date",
    "location_hint": "string",
    "property": "PropertySnapshot"
  },
  "CompSale": {
    "sale_price": "number>0",
    "close_date": "ISO date",
    "distance_miles": "number>=0",
    "property": "PropertySnapshot",
    "concessions": "number|null",
    "data_source": "string|null",
    "notes": "string|null"
  },
  "AdjustmentParams": {
    "annual_appreciation_rate": "number",
    "gla_incremental_per_sf": "number",
    "full_bath_value": "number",
    "half_bath_value": "number",
    "bedroom_value": "number",
    "garage_space_value": "number",
    "lot_incremental_per_sf": "number",
    "pool_value": "number",
    "adu_value": "number",
    "view_premium_per_point": "number",
    "busy_road_penalty": "number",
    "condition_step_value": "number",
    "quality_step_value": "number",
    "weight_k": "number",
    "weight_alpha_months": "number",
    "weight_beta_miles": "number",
    "trim_fraction": "number in [0,0.3]",
    "range_confidence_z": "number",
    "rounding_nearest": "integer>=1"
  }
}

4) Agent‑to‑tool contracts (function signatures)

Define these as callable tools from any agent (but mostly the Analysis Engine):

tool compute_valuation( 
  subject: SubjectInput, 
  comps: CompSale[], 
  params?: AdjustmentParams
) -> {
  estimated_value: number,
  low: number,
  high: number,
  stats: {
    median: number,
    trimmed_mean: number,
    weighted_average: number,
    weighted_median: number,
    ppsf_cross_check: number,
    mad: number,
    min_adj: number,
    max_adj: number
  },
  comp_logs: [{
    time_factor: number,
    time_adjusted_price: number,
    adjustments: Record<string, number>,
    total_feature_adjustment: number,
    final_adjusted_price: number,
    weight: number
  }],
  params_used: AdjustmentParams,
  notes: string[]
}

tool fetch_attom_property(query: { address?: string, apn?: string }) -> PropertyDetails
tool fetch_attom_comps(input: { address?: string, apn?: string, radius_miles: number, min_close_date?: string }) -> CompSale[]
tool fetch_market_stats(area: { geo_id: string }) -> { mos: number, list_to_sale: number, trend_12mo: number }


(Stub other providers with identically shaped outputs so your orchestration can swap sources.)

5) Scoring for the Deal Finder

Non‑ML, transparent:

discount_pct = (valuation.estimated_value - asking_price) / valuation.estimated_value
cap_rate = NOI / asking_price
confidence_penalty = clamp( MAD / estimated_value, 0, 0.15 )

risk_penalty = rule_based(
  {busy_road, flood_zone, very_old, unpermitted_space, thin_comp_count}, weights
)

deal_score =  0.50*discount_pct
            + 0.30*cap_rate
            - 0.10*confidence_penalty
            - 0.10*risk_penalty


Return a ranked list with why it ranked (feature contributions).

6) Evaluation & QA (baked in)

Deterministic unit tests for compute_valuation.

Schema validation on all inputs/outputs.

Sanity checks: min 3 comps; snap range to [min_adj, max_adj].

Shadow evaluation: keep a fixture set of 30–50 past sales; compare model to actual sold prices (MAPE/median abs error).

Red flags: if adjustments > 15% of comp price or comps older than 12 months → lower confidence + user explanation.

7) Copy‑paste Copilot prompt packs (one per agent + orchestrator)
A) System prompt — Agent 1: Customer Agent (User Interface)
Role: Front-door conversational agent for a real estate valuation app. 
Primary goals: 
- Collect structured inputs from users. 
- Explain results clearly. 
- Never do math; delegate to tools. 
- Avoid steering or bias. 
- Surface uncertainty and next steps.

Behavior:
- Ask for missing fields using the SubjectInput schema.
- Offer to auto-fetch comps via tools when given an address/APN.
- If fewer than 3 good comps are returned, ask the user to widen radius/date or provide manual comps.
- When results come back, render: estimated_value, low-high, key drivers (GLA, baths, condition), and caveats.
- If confidence is low (MAD/estimate > 8% or comps < 3), say so.
- For investment questions, can request the Analysis Engine to compute rent/cap-rate if provided rent/expenses.

Style:
- Friendly, concise, educational. Avoid slang. No protected-class proxies (schools by rating are okay; avoid demographic inferences).

Tools available:
- fetch_attom_property
- fetch_attom_comps
- fetch_market_stats
- compute_valuation

Output format:
- Human explanation + a machine-readable JSON block: 
  { "estimate": {...}, "assumptions": {...}, "data_provenance": {...} }

B) System prompt — Agent 2: Analysis Engine (Technical Expert)
Role: Deterministic calculator. You never guess. You call compute_valuation and return the result plus a short explanation. 
Never invent comps or parameters; use inputs or call tools.

Inputs:
- SubjectInput, CompSale[], AdjustmentParams (optional)

Actions:
1) If comps are missing, call fetch_attom_comps with sensible defaults: radius=1.0 mile, min_close_date = valuation_date - 12 months.
2) Invoke compute_valuation(subject, comps, params).
3) If MAD/estimate > 12% or fewer than 3 comps, add "LOW_CONFIDENCE" tag in notes and recommend user-provided comps or widened radius.
4) Return JSON ONLY to the Customer Agent, including comp_logs and params_used.

Policies:
- Adjust the comp to match the subject (never the reverse).
- Time-adjust using annual_appreciation_rate when provided; else 0.
- No fair-housing or demographic attributes are to be processed.

Output:
{ "estimated_value": number, "low": number, "high": number, "stats": {...}, "comp_logs": [...], "params_used": {...}, "notes": [...] }

C) System prompt — Agent 3: Deal Finder (Opportunity Scanner)
Role: Rule-based scanner that sources candidate deals and ranks them.

Inputs:
- Investor criteria: min_cap_rate, max_price, neighborhoods (geo_ids), property types, beds/baths, min_lot, exclusions (busy roads, flood), max_distance_to_X.

Actions:
1) For each geo_id, call fetch_attom_property or bulk search to get candidates (new listings, price changes).
2) For each candidate, call fetch_attom_comps then compute_valuation (fast params).
3) Compute deal_score using the formula provided; attach components: discount_pct, cap_rate, confidence_penalty, risk_penalty.
4) Return a sorted list with top-N and explanations suitable for notifications.

Output:
{
  "as_of": "ISO datetime",
  "criteria": {...},
  "candidates": [
    { "address": "...", "asking_price": 000000, "estimate": {...}, "deal_score": 0.00, "why": ["10% below model", "cap 5.3%", "low traffic street"] }
  ]
}

Guardrails:
- Skip properties with <3 comps or extreme adjustments.
- No demographic-based filtering. Use property and location features only.

D) System prompt — Orchestrator/Router
Role: Single entry point. Classify user intent and route:
- "valuation" → Customer Agent → Analysis Engine
- "deal_finder" or "alerts" → Deal Finder
- "explain" → Customer Agent only

Add a machine intent header:
{ "intent": "valuation|deal_finder|explain", "requested_action": "...", "missing_fields": [...] }
Ensure tools are only called by Analysis Engine or Deal Finder, not by the Customer Agent directly unless collecting simple lookups.

8) Concrete skills & knowledge files (ready to create)

Glossary.md: ARV, AVM, comps, GLA, FSD, MAD, PPSF, MOS, cap rate.

InterpretationGuide.md: “What a wide range means,” “How time adjustment works,” “Why small homes have higher PPSF.”

FAQ.md: “Why my Zestimate differs,” “How many comps do I need,” “What if there are no recent sales.”

RiskMatrix.json: busy_road penalty, flood zone penalty, unpermitted space penalty, thin comps penalty.

DealCriteriaTemplates.json: BRRRR, flip, long‑term rental, house‑hack.

9) Example end‑to‑end flow (happy path)

User: “Estimate value for 123 Oak St; 3/2; 1,800 sf; 7,000 sf lot.”

Customer Agent → gathers missing items, asks to auto‑fetch comps.

Analysis Engine → fetch_attom_comps → compute_valuation → returns $X with range and comp logs.

Customer Agent → explains headline, range, top 3 adjustments, and confidence; offers PDF/MD report.

10) Implementation checklist (no ML)

 Shared valuation library (pure functions)

 FastAPI endpoints for tools (or direct module calls)

 Agent runners (system prompts above)

 Schema validation + unit tests for edge cases

 ATTOM integration + key handling + backoff/retry

 Logging/audit trail (comp logs + parameters)

 Compliance text and fair‑housing guardrails

 Deal Finder job with idempotent pagination and dedupe

11) Want a single Copilot “make the repo” prompt?

Paste this into Copilot to scaffold the multi‑agent app (Python FastAPI + your shared valuation lib):

Create a monorepo `realval/` with:

packages/valuation_core/    # pure math + models
  - models.py, adjustments.py, estimator.py, __init__.py
  - tests/ (unit tests covering edge cases and example fixtures)

services/agents/
  - orchestrator.py          # routes intents to agents
  - agent_customer.py        # System prompt from spec; no math
  - agent_analysis.py        # calls valuation_core + data tools
  - agent_dealfinder.py      # scans, scores, explains
  - tools/attom_client.py    # typed client; retries; rate-limit
  - tools/reporting.py       # markdown report generator
  - api.py                   # FastAPI: /estimate, /scan, /health

configs/
  - params.default.json      # AdjustmentParams defaults
  - deal_criteria.samples.json

docs/
  - Glossary.md, InterpretationGuide.md, FAQ.md
  - API.md with tool schemas

Implementation requirements:
- Use the shared schemas from the spec.
- Strict type hints and Pydantic validation on all I/O.
- `compute_valuation` implements: time-adjustment, feature deltas, weighted median, MAD band, ppsf cross-check, comp logs.
- Agents adhere to their system prompts; Customer Agent never computes.
- Add simple auth (token header) and redact keys in logs.
- Unit tests: math determinism, schema validation, and deal_score monotonicity.
- Provide a Makefile with run, test, lint targets.
- Provide curl examples for /estimate and /scan in README.

Bottom line

Your 3‑agent structure is solid. With the upgrades above—shared library, strict schemas, confidence/range, audit trail, guardrails, and the prompt packs—you’ll have a robust, transparent valuation assistant that doesn’t rely on ML. If you want, I can adapt these prompts to a TypeScript/Node stack or add a minimal OLS “calibrate” helper later without changing the agent boundaries.