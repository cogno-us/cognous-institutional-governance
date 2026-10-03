"""Keep reviewed-text checks portable without accepting substantive edits."""

import hashlib
import unittest

from tools.validate_bootstrap import _reviewed_artifact_digest


class ReviewedArtifactDigestTests(unittest.TestCase):
    def test_lf_and_crlf_match_historical_crlf_digest(self):
        crlf = b"Human authority.\r\nDelegation remains bounded.\r\n"
        expected = hashlib.sha256(crlf).hexdigest()
        self.assertEqual(_reviewed_artifact_digest(crlf), expected)
        self.assertEqual(_reviewed_artifact_digest(crlf.replace(b"\r\n", b"\n")), expected)

    def test_substantive_mutation_still_changes_digest(self):
        original = b"Machine validation is not authority.\n"
        mutation = b"Machine validation is authority.\n"
        self.assertNotEqual(_reviewed_artifact_digest(original), _reviewed_artifact_digest(mutation))

    def test_whitespace_and_final_newline_remain_significant(self):
        original = b"Delegation is bounded.\n"
        self.assertNotEqual(_reviewed_artifact_digest(original), _reviewed_artifact_digest(original.rstrip(b"\n")))
        self.assertNotEqual(_reviewed_artifact_digest(original), _reviewed_artifact_digest(b"Delegation is bounded. \n"))
