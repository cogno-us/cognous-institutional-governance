# Authority Context reference checks

**Summary:** These local checks exercise the proposed 0.1.0 interface and reject
represented scope and authority errors. They do not authenticate institutions,
enforce an external action or establish that a grant is real.

Read the [profile](../../../process/implementation/public-stack-v0.1/README.md),
[specification](../../../process/implementation/public-stack-v0.1/AUTHORITY_CONTEXT.md)
and [worked cases](../../../process/implementation/public-stack-v0.1/WORKED_CASES.md).

## Reproduce

From repository root, Python 3.10 or later:

```sh
python3 -m pip install -r testing/harness/requirements-authority.txt
python3 testing/harness/run_authority_context.py
python3 -m unittest discover -s tests -q
python3 tools/validate_bootstrap.py
python3 testing/harness/verify_snapshot.py
python3 testing/harness/verify_film_review.py
python3 testing/harness/verify_authorization_effect.py
```

The dedicated runner requires `jsonschema==4.26.0` and fails if missing. The
stdlib repository suite skips only its added Authority Context test when the
optional dependency is absent; a skipped test is not profile validation. Existing
checks retain their original dependencies and meanings. No external `$ref` is
fetched by this self-contained schema.

## Fixture layers

`bases.json` contains three explicit, invented assumed-input configurations:
routine, higher-consequence and bounded delegation. `cases.json` gives each
fixture's base, declarative changes, structural expectation and exact reference
error oracle. The runner applies set/delete patches; it does not execute fixture
code. Legitimate fixtures cover scoped class grants, explicit case approval and
attenuated delegation. Requirement-only and feedback-as-proposal cases preserve
those objects' distinct semantics.

Adverse fixtures cover missing authority basis, grant and approval; expiry,
suspension/revocation, stale/unknown status and changed revision; child excess,
revoked/absent parents, forbidden delegation, expiry and weakened obligations;
conflicting rules and incompatible roles; changed policy/payload and forged or
self/expired approvals; unsupported versions and malformed references; signature
or chain evidence as permission; outcome evidence as adoption; dropped required
approval, incorrect UNKNOWN semantics, T4 treated as routine, negative amount,
wrong target/domain/cap and injected runtime decision fields.

Schema checks establish shape, exact version and local reference format only.
Reference checks compare represented mandates, roles, requirement bindings,
policies/status/evidence and approvals against explicitly assumed inputs. Fixture
oracles are authored with this reference implementation and are not independent
institutional review. Results say neither `allow` nor `executed`.

These are separate from the existing AE adapter's 60 synthetic observations.
All three pre-existing archives remain unchanged, with their original scope and
limitations. No new fixtures are field cases, distributed enforcement, ODES
conformance or a measurement of incremental Alvorada benefit.

Actual results and reproduction hashes are recorded in
[the profile check record](AUTHORITY_CONTEXT_CHECKS.md). Human usability, real
mandates, protected rights, practical independence and comparative outcomes
remain further work.
