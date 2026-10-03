# Fixed synthetic fixtures

[cases.json](cases.json) contains 24 subtests: eight policy, eight agent-permission/recovery and eight citation cases. [backup_fixture.json](backup_fixture.json) contains one fictional recovery row. Both are read-only inputs; the harness does not rewrite them.

Fields: `id` identifies the subtest, `battery` links its narrower behavior to an operational exercise, `flow` selects the adapter, `title` describes the perturbation, and `expected` is the predefined effect oracle. Optional Boolean flags provide pre-labelled evidence (`conflict`, `missing`, `expired`, `revoked`, `version_changed`, `outage`, `wrong_proposition`, `wrong_quote`, `circular`, `challenged`); `override` records attempted pressure but never grants authority. `receipt: false` models absent delivery confirmation. Agent `action` is read, delete or restore; `path` labels a represented route through the same connection.

Expected outcomes: BLOCK, ALLOW, PENDING, RESTORED. The baseline can produce NOT_ATTEMPTED for recovery. Nineteen cases require blocking, three require a legitimate allow, one remains pending, one restores a record. Evidence recognition is provided to the harness, not tested. No real source corpus, personal data or production records are included.
