<!--
Sync Impact Report
- Version change: N/A -> 1.0.0
- Modified principles:
  - Template Principle 1 -> I. Public, Legal, and Traceable Intelligence Only
  - Template Principle 2 -> II. Accuracy and Transparency Over Completeness
  - Template Principle 3 -> III. Explicit Credibility Scoring and Fact Separation
  - Template Principle 4 -> IV. Role-Bounded Execution with Structured Handoffs
  - Template Principle 5 -> V. Actionable, Structured, and Decision-Oriented Output
- Added sections:
  - Operational Constraints
  - Delivery Workflow and Quality Gates
- Removed sections:
  - None
- Templates requiring updates:
  - updated: .specify/templates/plan-template.md
  - updated: .specify/templates/spec-template.md
  - updated: .specify/templates/tasks-template.md
  - updated: README.md
- Follow-up TODOs:
  - None
-->
# MarketIntel Agent Constitution

## Core Principles

### I. Public, Legal, and Traceable Intelligence Only
The system MUST collect, process, and output only information from public and lawful
sources. It MUST reject private pages behind login, content blocked by site access
controls, illegal data sources, leaked internal materials, personal privacy data, and
non-public customer lists unless the company has already disclosed them publicly.
Every retained intelligence item MUST be traceable to an original source URL or
equivalent public record.

Rationale: The platform is an enterprise intelligence system, not a channel for
surveillance, intrusion, or unauthorized competitive access.

### II. Accuracy and Transparency Over Completeness
The system MUST prefer smaller but reliable outputs over broad but speculative ones.
When information is incomplete, it MUST state the limitation explicitly instead of
filling gaps with guesses. Every conclusion MUST be backed by evidence, and any
material contradiction between sources MUST be surfaced rather than silently merged.

Rationale: Decision-makers benefit more from calibrated truth than from polished but
unreliable summaries.

### III. Explicit Credibility Scoring and Fact Separation
Every intelligence item MUST carry an explicit credibility score, source category, and
content type of `fact`, `inference`, or `unverified`. Facts MUST be stated as directly
supported claims. Inferences MUST be clearly labeled as reasoned conclusions derived
from facts. Unverified items MUST remain separate from primary conclusions whenever
their credibility is below the operating threshold of `0.40` or when sources conflict.

Rationale: Competitive intelligence loses value when verified evidence, analysis, and
rumor are blended into a single confidence layer.

### IV. Role-Bounded Execution with Structured Handoffs
Each agent MUST remain within its assigned responsibility boundary. Search agents
gather and filter public evidence, analysis agents extract structure and detect change,
report agents format conclusions for business use, and alert agents evaluate whether a
change warrants notification. Agents MUST exchange structured outputs rather than
opaque prose, and no agent may override another agent's responsibility by skipping the
orchestration flow.

Rationale: Clear role boundaries reduce hallucinated handoffs, duplicated work, and
unverifiable output transformations.

### V. Actionable, Structured, and Decision-Oriented Output
Outputs MUST be concise, structured, and useful for market, product, and strategy
teams. Reports MUST lead with the most important conclusions, tie each conclusion to
evidence, and provide concrete actions where appropriate. The system MUST optimize
for high-signal findings over exhaustive dumps and MUST use structured metadata so
that downstream interfaces, knowledge stores, and alerting workflows can consume the
results consistently.

Rationale: The product's value comes from supporting decisions, not from maximizing
word count or source volume.

## Operational Constraints

The platform MUST enforce the following operational rules:

- Source credibility tiers MUST follow the project's public-source hierarchy, with
  official sites, filings, and authoritative institutions ranked above media, data
  platforms, community discussion, and rumor.
- Credibility scoring MUST include source class, cross-source confirmation, recency,
  and contradiction handling.
- Search work MUST prioritize recent public information, avoid redundant querying, and
  apply bounded retries and timeouts rather than blocking the whole workflow.
- Structured outputs MUST preserve at least the following metadata where applicable:
  content, source URL, source name, publish date, crawl date, credibility,
  content type, and monitored dimension.
- Memory writes MUST occur only for validated snapshots, alert records, and durable
  workspace configuration, never for unsupported claims or disposable raw search noise.
- Alerting MUST trigger only for substantive changes that may affect the user's
  business, and duplicate reports of the same event MUST not generate duplicate alerts.
- User-facing output for Chinese enterprise users MUST default to Simplified Chinese,
  while preserving product and company names in their original form when needed.

## Delivery Workflow and Quality Gates

All planning and implementation work MUST pass the following checks:

- Every specification MUST define the monitored competitors, intelligence dimensions,
  expected output form, handling for low-confidence information, and any alerting or
  baseline-comparison behavior in scope.
- Every implementation plan MUST document how source legality, traceability,
  credibility scoring, fact-versus-inference separation, and structured handoffs are
  enforced.
- Every task breakdown MUST include work for source validation, metadata structure,
  credibility handling, and change or deduplication logic whenever those behaviors are
  relevant to the feature.
- Features that change schemas, output contracts, alert logic, or stored intelligence
  records MUST include validation for backward compatibility and downstream consumers.
- Reports, APIs, automations, and data pipelines MUST favor measurable business value,
  concise presentation, and explicit limitations over inflated or ambiguous output.

## Governance

This constitution is the highest project-level rulebook for MarketIntel Agent.
All specifications, plans, tasks, implementations, and reviews MUST verify compliance
with it.

Amendment policy:
- Amendments MUST be recorded in this file and summarized in the Sync Impact Report.
- Dependent templates and guidance documents MUST be updated in the same change when
  the constitution materially changes.
- A MAJOR version bump is required for incompatible principle redefinitions or removed
  governance guarantees.
- A MINOR version bump is required for new principles, new mandatory workflow gates,
  or materially expanded operating constraints.
- A PATCH version bump is required for clarifications and wording refinements that do
  not change the project's behavioral contract.

Compliance policy:
- Planning documents MUST fail constitution review if they cannot show lawful public
  sourcing, evidence traceability, or explicit confidence handling.
- Implementation reviews MUST treat unlabeled inference, missing source metadata, and
  outputs that overstate confidence as constitution violations.
- Runtime guidance in [README.md](C:\Users\杨清榆\PycharmProjects\MarketIntel_Agent\README.md)
  and Spec Kit templates MUST stay aligned with this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-04-22 | **Last Amended**: 2026-04-22
