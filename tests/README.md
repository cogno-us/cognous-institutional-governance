# Repository conformance tests

These tests and `tools/validate_bootstrap.py` check encoded repository invariants and artifacts. They are distinct from the [testing and evaluation section](../testing/README.md), which contains incident-inspired operational proposals and synthetic adapter results.

Run from the root:

```sh
python3 tools/validate_bootstrap.py
python3 -m unittest discover -s tests -q
```

A passing suite supplies no field-performance, legal-compliance, ratification or production-authorization conclusion. See [recorded check results](../testing/results/2026-10-03-reference-v1/REPOSITORY_CHECKS.md) for execution provenance.

Current [evidence status](../docs/EVIDENCE_STATUS.md) explains that validator
readiness/comprehensibility fields check a recorded design review, not a new
human assessment. The modular charter, profiles and AI guidance do not inherit
v0.1's review status. Historical snapshots and hashes remain controlling for
archive-integrity checks; current documentation can evolve without rewriting them.
