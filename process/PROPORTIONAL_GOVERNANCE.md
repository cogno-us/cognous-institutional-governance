# Proportional governance: consequence, evidence and overhead

**Executive summary:** Routine authorized work needs a lighter route than serious or irreversible choices. Stronger process cannot make prohibited acts permissible.

[Read the detailed guidance](#detailed-guidance).

## Detailed guidance

**PROPOSED OPERATING GUIDANCE. Does not waive controlling law or v0.1 rules.**

Govern the decision's plausible effects, not the label of the sector, the use
of AI or the length of the answer. Routine governance should usually be applied
at the level of the authorized action class. Reserve individual deliberation
for consequential choices, exceptions, uncertainty and challenges.

## Assess the act before choosing the route

Identify actual authority and prohibited actions first. Then assess plausible
harm and its severity, reversibility in practice, scope/population, rights and
vulnerability, uncertainty, downstream reliance, correlated repeated exposure,
and effective-power concentration. Evaluate both action and delay harms.
Uncertainty about a severe consequence is grounds for more inquiry, not a low
score. A tiny average risk can conceal a serious subgroup or tail consequence.

Do not multiply arbitrary severity/probability scores into a permission number.
Use quantitative evidence where genuinely calibrated, disclose its assumptions,
and retain qualitative constraints and credible worst cases. Reassess when the
content, audience, cumulative volume, source, dependency or intended use changes.

## Decision tiers

| Tier | Conditions/examples | Evidence needed | Review and record burden | Delay limit (maximum time to a recorded disposition) |
|---|---|---|---|---|
| T0: routine information | Reversible, low-reliance information within a clear grant; opening hours from a current source | Current authoritative source/version; no material conflict; answer within allowed scope | Standing human approval of action class; routine execution can be automatic; compact trace, exception route and sampled review | 4 hours (14,400 s) |
| T1: bounded ordinary action | Limited reversible effect; small refund within an actual policy cap | Applicable facts, source, grant, scope/cap and practical reversal/delivery evidence | Delegated human or AI execution if actually authorized; no mandatory per-case committee; transaction record, sampling and challenge | 1 day (86,400 s) |
| T2: consequential choice | Meaningful financial/access effects, sensitive reliance, dispute or material uncertainty | Claim-specific sources, contrary evidence, alternatives, affected people and reasons sufficient for the competent decision | Competent human prior decision for reserved/adverse choices; noninvolved review of challenges; short structured record and actual remedy check | 3 days (259,200 s) |
| T3: severe or difficult-to-reverse effect | Death/serious injury, coercion, substantial rights loss, critical infrastructure or credible systemic exposure | Strong contextual evidence, source independence where material, adverse scenarios, external standards, qualified review and unresolved limits | Actual competent human authorization; independent challenge before effect where required; fuller material record, response/continuity arrangements and separate effect verification | 7 days (604,800 s) |
| T4: foundational/structural change | Change to ends, protected constituency, decision rights or institutional architecture | Complete proposed change, legitimate constituency/process, alternatives, dependencies, dissent and cumulative effects | Reserved human constitutional/change process; cannot be delegated as a routine T0–T3 decision | 30 days (2,592,000 s), to a recorded disposition into the reserved process only |

The tier is a design recommendation, not a legal classification or validated
probability cutoff. Controlling sector rules may require stricter treatment at
any tier. T4 identifies the object of change; a T3 act can have more immediate
physical consequences. Prohibited acts are outside all authorization routes.

### Delay limits

**PROPOSED; values are placeholders for the project owner to confirm.** The last
column is the longest elapsed time a *complete* request (the requirement's
evidence is supplied and the act is ready for the tier's review) may remain at
that tier without a recorded disposition. A disposition is one of: the decision
or effect authorized by a competent human or by an actual grant; a narrower
authorized act; escalation to an alternate reviewer; or deferral with a stated
reason. The limit is measured in elapsed time, including queue and contact time,
not active person-minutes.

- **Not a license.** Expiry never approves, never authorizes the act and never
  moves it to a lower tier. A miss must trigger one of the Authority Context
  `on_miss` responses: `escalate_to_alternate_reviewer`, `defer_with_reason` or
  `narrower_authorized_action`. There is no automatic-approval value.
- **Ceilings, not targets to approach.** An institution's Authority Context may
  declare a shorter `max_pending_seconds` than its tier's value, never a longer
  one; the reference check rejects it as `delay_limit_exceeds_tier_ceiling`.
  Reclassifying to a lower tier therefore needs the shorter limit as well.
- **Unchanged limits.** The V.2 necessity fallback (earliest V.3 event, no later
  than 24 hours) and the V.4 filing and review times in
  [review calibration](REVIEW_CALIBRATION.md) are unaffected. A limit here neither
  replaces nor extends them and creates no emergency route.
- **Higher tiers are longer.** They require more sequential review (independent
  challenge, qualified review, separate effect verification), so their limits are
  longer, not because more delay is acceptable. Where delay itself is harmful,
  use a predelegated route or a narrower authorized act, and do not hide an
  unavailable reviewer behind the limit.
- **T4** has no decision deadline. Its limit applies only to recording that the
  proposal has entered the reserved constitutional/change process or has been
  deferred with reasons; the process sets its own timetable.
- **Not validated.** These values are not derived from the Constitution or tested
  against workload, harm or capacity data (see
  [review calibration](REVIEW_CALIBRATION.md#observe-and-recalibrate)). The
  competent human owner may change them by the competent procedure, and the
  numbers in the [Authority Context](implementation/public-stack-v0.1/AUTHORITY_CONTEXT.md)
  reference check (`TIER_DELAY_CEILING_SECONDS`) and in this table must agree; a
  test fails if they differ. The reference check only compares a declared limit
  with its tier ceiling. It does not measure elapsed time or enforce a miss
  response.

### Safeguards against false low-risk classification

A named competent human owns the class definitions and material reclassification.
AI can suggest a tier, flag escalation and prepare evidence; it cannot approve its
own downgrade or alter thresholds. Review some low-tier cases regardless of AI
flags, check user complaints and subgroup outcomes, and examine repeated small
acts together. If a source/grant changes, pause the affected class pending the
competent response. Unknown scope or authority is never treated as authorization.

An information-only answer about a refund entitlement can be T2 when reliance
is consequential. Routine healthcare scheduling becomes T3 if it delays urgent
care. A single mildly wrong answer repeated to a million people is not assessed
only as a single answer. Institution-level policy changes can be T4 even when
implemented by many individually small actions.

## Evidence burdens: distinguish four questions

1. **Permission:** what actual grant permits this act? Accuracy cannot supply it.
2. **Factual support:** what sources support each material proposition, what is
   contradicted or missing, and why are they sufficient for this use?
3. **Acceptance of residual risk:** which competent human can accept which
   remaining uncertainty within the applicable mandate and rights constraints?
4. **Formal proof:** what controlling legal/constitutional standard applies to
   the specific proceeding? This is not a model probability threshold.

Routine evidence can be a verified current source and a valid grant. A contested
or severe act needs deeper corroboration and independent examination. This guide
does not equate T2 with a legal preponderance standard or T3 with clear and
convincing evidence. Formal standards must come from actual controlling rules.
v0.1's specified clear-and-convincing burdens, office selection, emergency limits
and change thresholds remain fixed unless validly changed.

## Minimum records and review budget

A routine record references the standing grant, rule/source version, act,
time, responsible function, exception/uncertainty, effect status and challenge
route. Add decision-specific reasons, material alternatives, dissent and AI
dependencies when present. A field marked not applicable needs a reason when
material; routine economy is not permission to hide a disagreement.

Use one source packet, reuse verified standing context, batch permissible reviews,
write an exceptions-first briefing, and avoid duplicative worksheets. Each review
step should identify the failure it could catch, its decision consequence and
its real cost. Retain required safeguards; remove optional duplication only
through the competent procedure. Measure preparation, checking, queue, decision,
remedy and maintenance time, not just drafting speed.

Sampling is suitable for bounded routine classes; it cannot substitute for
required prior review. Set actual sample policy, strata and escalation thresholds
from contextual evidence and capacity. No universal sample percentage is proven
here. Class authorization should define who can stop/restore work, fallback
service, volume limits, expiry and complaints intake.

## Urgency and dynamic calibration

Within already permissible routes, ask whether additional inquiry is likely to
change the decision and whether its expected benefit exceeds delay harm and
burden. Quantify only supported inputs; otherwise document uncertainty. Use
bounded reversible measures when they adequately protect people. A deadline
must trigger an actual permitted response or escalation, not automatic approval.

Predelegated incident action can be rapid because its scope and evidence rules
were reviewed earlier. [Review calibration](REVIEW_CALIBRATION.md) preserves
v0.1's narrow exceptional route. A severe emergency may demand fewer sequential
administrative steps while retaining stronger substantive constraints and rapid
independent review. Time pressure does not reduce harm severity or confer power.

## Examples across every existing application

Use the [application routing map](../applications/MODULAR_ROUTING.md). An
institutional profile determines offices and tenure; this guide determines the
act's review intensity. The [AI assistance module](../applications/ai-assisted-institutional-governance.md)
reduces preparation work; the [recursion guide](VIRTUOUS_RECURSION.md) governs how
observed results inform future authorized improvements.
