#!/usr/bin/env python3
"""Offline RFC 3161 query/receipt checks using local OpenSSL. Never sends a request."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import ledger


def openssl(arguments):
    binary = shutil.which("openssl")
    ledger.require(binary is not None, "OpenSSL is required for local timestamp checks")
    result = subprocess.run([binary, *map(str, arguments)], capture_output=True, text=True,
                            timeout=15, env={**os.environ, "LC_ALL": "C"})
    ledger.require(result.returncode == 0, "OpenSSL verification/operation failed: " + result.stderr.strip())
    return result.stdout


def valid_digest(value):
    ledger.require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None, "Expected lowercase SHA-256 digest")


def make_query(expected_digest, output):
    valid_digest(expected_digest)
    path = Path(output)
    # Reserve the output path before invoking OpenSSL; refuse replacing a previous request.
    with path.open("xb"):
        pass
    openssl(["ts", "-query", "-digest", expected_digest, "-sha256", "-cert", "-out", path])
    text = openssl(["ts", "-query", "-in", path, "-text"])
    ledger.require("Nonce:" in text and "Nonce: unspecified" not in text, "Timestamp query must include a nonce")
    return {"query_file": str(path), "query_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "expected_digest": expected_digest, "sent_to_service": False,
            "independent_timing_verified": False}


def verify_receipt(expected_digest, query_file, response_file, ca_file, expected_ca_file_sha256,
                   signer_file, cutoff_utc, clock_error_bound_seconds):
    valid_digest(expected_digest)
    valid_digest(expected_ca_file_sha256)
    ledger.require(hashlib.sha256(Path(ca_file).read_bytes()).hexdigest() == expected_ca_file_sha256,
                   "Trust-anchor file does not match its pinned SHA-256")
    ledger.require(ledger.number(clock_error_bound_seconds) and clock_error_bound_seconds >= 0,
                   "Supply a nonnegative audited clock-error bound; do not assume zero")
    query = openssl(["ts", "-query", "-in", query_file, "-text"])
    ledger.require("Nonce:" in query and "Nonce: unspecified" not in query, "Missing query nonce")
    # ts lacks verify's -no-CApath/-no-CAstore flags: supply an empty directory
    # and the same pinned local root file as the explicit store instead.
    with tempfile.TemporaryDirectory(prefix="ai-hype-empty-ca-path-") as empty:
        trust = ["-CAfile", ca_file, "-CApath", empty, "-CAstore", Path(ca_file).resolve().as_uri(), "-untrusted", signer_file]
        # Bind the reply to this request (including nonce), then the exact ledger digest.
        openssl(["ts", "-verify", "-queryfile", query_file, "-in", response_file, *trust])
        openssl(["ts", "-verify", "-digest", expected_digest, "-in", response_file, *trust])
    text = openssl(["ts", "-reply", "-in", response_file, "-text"])
    match = re.search(r"^Time stamp:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    ledger.require(match is not None, "Missing signed generation time")
    signed = None
    for fmt in ("%b %d %H:%M:%S %Y GMT", "%b %d %H:%M:%S.%f %Y GMT"):
        try:
            signed = datetime.strptime(match.group(1), fmt).replace(tzinfo=timezone.utc)
            break
        except ValueError:
            pass
    ledger.require(signed is not None, "Unsupported signed timestamp format")
    before = signed + timedelta(seconds=clock_error_bound_seconds) < ledger.time(cutoff_utc)
    ledger.require(before, "Signed time plus configured error bound is not strictly before cutoff")
    return {"cryptographic_request_and_digest_match": True, "signed_at_utc": ledger.stamp(signed),
            "before_cutoff_under_supplied_bound": before,
            "clock_error_bound_seconds": clock_error_bound_seconds,
            "clock_bound_and_anchor_authenticity_require_independent_review": True,
            "ca_file_sha256": expected_ca_file_sha256,
            "response_sha256": hashlib.sha256(Path(response_file).read_bytes()).hexdigest(),
            "independent_timing_verified": False,
            "note": "Local cryptographic consistency is not proof this CA is an independently trusted timestamp authority. No revocation/network checks performed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    query = commands.add_parser("make-query")
    query.add_argument("--digest", required=True)
    query.add_argument("--out", required=True)
    verify = commands.add_parser("verify")
    for name in ("digest", "query", "response", "ca", "ca-file-sha256", "signer", "cutoff"):
        verify.add_argument("--" + name, required=True)
    verify.add_argument("--clock-error-bound-seconds", type=float, required=True)
    args = parser.parse_args()
    if args.command == "make-query":
        result = make_query(args.digest, args.out)
    else:
        result = verify_receipt(args.digest, args.query, args.response, args.ca, args.ca_file_sha256,
                                args.signer, args.cutoff, args.clock_error_bound_seconds)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        import sys
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(2)
