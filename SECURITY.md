# Security and sensitive disclosure

This is a research repository with validation scripts, not a deployed
constitutional enforcement service. There are no supported production-runtime
versions or security certifications. The current `main` branch is the active
maintenance target; historical snapshots are not promised ongoing fixes.

## Report an ordinary defect

Use a public issue for reproducible validator defects, broken links, or
non-sensitive design concerns. Identify the commit, command or passage, expected
behavior, observed behavior, and relevant environment. Constitutional criticism
belongs in the review process even when it is not a software vulnerability.

## Report sensitive material or an exploitable issue

Do not put credentials, personal data, unpublished proprietary material, or a
usable exploit in a public issue or pull request. If GitHub offers **Report a
vulnerability** for this repository, use that private route. Its availability
has not been verified by this document.

Otherwise, post only a minimal request for a private reporting channel, without
sensitive details, and wait for a maintainer to establish one. A dedicated
private address and guaranteed response time have not been established. The
maintainer should acknowledge the report, determine scope, coordinate correction,
and agree on a suitable disclosure record without promising immunity or secrecy
beyond the channel's actual protections.

Removing content from the current branch does not erase public Git history or
copies. A leaked credential requires action by its actual controller; deleting
its text is not sufficient. Do not test against third-party systems or real
personal data to demonstrate a repository issue.

This policy describes reporting, not the result of a security audit. Read the
[public release review](docs/PUBLIC_RELEASE_REVIEW.md) and
[research limitations](research/LIMITATIONS_AND_EVALUATION.md).
