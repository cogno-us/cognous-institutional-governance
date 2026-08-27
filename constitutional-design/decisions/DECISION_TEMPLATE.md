# Constitutional Decision Record template

Copy these fields into a structured record without treating placeholders as
evidence:

```yaml
decision_id:
title:
status: UNRESOLVED
question:
related_issues: []
source_material: []
assumptions: []
candidate_architectures: []
historical_analogues: []
prior_art: []
advantages: []
failure_modes: []
bad_human_analysis: []
bad_artificial_intelligence_analysis: []
incentive_analysis: []
continuity_analysis: []
reversibility_analysis: []
human_comprehensibility_analysis: []
reviews: []
dissent: []
human_decision:
  authorized_by:
  authorization_record:
  decision_date:
decision_date:
supersedes: []
resulting_requirements: []
residual_uncertainty: []
provenance:
```

Allowed statuses: `PROPOSED`, `UNDER_REVIEW`, `DISPUTED`, `DECIDED`,
`DEFERRED`, `SUPERSEDED`, `UNRESOLVED`.

`DECIDED` is invalid unless all explicit human decision evidence fields are
present. Artificial intelligence consensus is not human authorization.

