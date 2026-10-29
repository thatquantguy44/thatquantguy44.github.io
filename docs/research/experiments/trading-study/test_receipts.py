"""Local test CA only. These signatures are never independent timestamp evidence."""

import hashlib
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import ledger
import receipts


@unittest.skipUnless(shutil.which("openssl"), "Local OpenSSL is not installed")
class LocalTimestampTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="ai-hype-untrusted-test-ca-")
        cls.path = Path(cls.temp.name)
        p = cls.path
        receipts.openssl(["req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=UNTRUSTED-OFFLINE-TEST-CA", "-keyout", p / "ca.key", "-out", p / "ca.pem", "-addext", "basicConstraints=critical,CA:TRUE", "-addext", "keyUsage=critical,keyCertSign,cRLSign"])
        receipts.openssl(["req", "-new", "-newkey", "rsa:2048", "-nodes", "-subj", "/CN=UNTRUSTED-OFFLINE-TEST-TSA", "-keyout", p / "tsa.key", "-out", p / "tsa.csr"])
        (p / "tsa.ext").write_text("basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\nextendedKeyUsage=critical,timeStamping\n")
        receipts.openssl(["x509", "-req", "-in", p / "tsa.csr", "-CA", p / "ca.pem", "-CAkey", p / "ca.key", "-CAcreateserial", "-days", "1", "-extfile", p / "tsa.ext", "-out", p / "tsa.pem"])
        (p / "serial").write_text("01\n")
        (p / "tsa.conf").write_text(f"""[tsa]
default_tsa = test_tsa
[test_tsa]
serial = {p / 'serial'}
signer_cert = {p / 'tsa.pem'}
signer_key = {p / 'tsa.key'}
certs = {p / 'ca.pem'}
signer_digest = sha256
default_policy = 1.2.3.4.1
digests = sha256
accuracy = secs:1
ordering = yes
tsa_name = yes
ess_cert_id_chain = no
ess_cert_id_alg = sha256
""")
        cls.expected = hashlib.sha256(b"PUBLIC SYNTHETIC OFFLINE TEST ONLY").hexdigest()
        cls.query = receipts.make_query(cls.expected, p / "request.tsq")
        receipts.openssl(["ts", "-reply", "-config", p / "tsa.conf", "-queryfile", p / "request.tsq", "-out", p / "response.tsr"])
        cls.ca_hash = hashlib.sha256((p / "ca.pem").read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def verify(self, digest=None, pin=None, cutoff=None):
        p = self.path
        return receipts.verify_receipt(digest or self.expected, p / "request.tsq", p / "response.tsr", p / "ca.pem", pin or self.ca_hash,
                                       p / "tsa.pem", cutoff or ledger.stamp(datetime.now(timezone.utc) + timedelta(hours=1)), 2)

    def test_local_signature_binds_request_digest_and_nonce_but_not_independence(self):
        result = self.verify()
        self.assertTrue(result["cryptographic_request_and_digest_match"])
        self.assertTrue(result["before_cutoff_under_supplied_bound"])
        self.assertFalse(result["independent_timing_verified"])
        self.assertFalse(self.query["sent_to_service"])

    def test_wrong_ledger_digest_fails(self):
        with self.assertRaisesRegex(ValueError, "OpenSSL"):
            self.verify(digest="a" * 64)

    def test_wrong_trust_anchor_pin_fails(self):
        with self.assertRaisesRegex(ValueError, "pinned"):
            self.verify(pin="a" * 64)

    def test_receipt_after_cutoff_is_not_accepted(self):
        with self.assertRaisesRegex(ValueError, "before cutoff"):
            self.verify(cutoff=ledger.stamp(datetime.now(timezone.utc) - timedelta(days=1)))

    def test_existing_query_is_not_overwritten(self):
        with self.assertRaises(FileExistsError):
            receipts.make_query(self.expected, self.path / "request.tsq")

    def test_same_digest_with_a_different_request_nonce_fails(self):
        query = self.path / 'new-nonce.tsq'
        receipts.make_query(self.expected, query)
        with self.assertRaisesRegex(ValueError, 'OpenSSL'):
            receipts.verify_receipt(self.expected, query, self.path / 'response.tsr', self.path / 'ca.pem', self.ca_hash,
                                    self.path / 'tsa.pem', ledger.stamp(datetime.now(timezone.utc) + timedelta(hours=1)), 2)


if __name__ == "__main__":
    unittest.main()
