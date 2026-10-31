from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import ssl
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from typing import Iterable

from .config import PipelineConfig, SourceSpec
from .provenance import read_json, sha256_bytes, write_json


class FetchError(RuntimeError):
    pass


def manifest_path(workspace: Path) -> Path:
    return workspace / "raw" / "manifest.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def certificate_context() -> ssl.SSLContext:
    """Use an explicit CA bundle when Python's bundled OpenSSL has none.

    Verification is always required. `PRESIDENTIAL_PIPELINE_CA_FILE` is the
    portable override; common system bundles are only fallbacks.
    """
    candidates = [
        os.environ.get("PRESIDENTIAL_PIPELINE_CA_FILE"),
        "/etc/ssl/cert.pem",
        "/etc/ssl/certs/ca-certificates.crt",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return ssl.create_default_context(cafile=candidate)
    return ssl.create_default_context()


def fetch_source(workspace: Path, source: SourceSpec, timeout_seconds: int = 30) -> dict[str, object]:
    """Fetch one public source only when called explicitly by the CLI."""
    request = Request(source.url, headers={"User-Agent": "presidential-impact-data/0.1 (+local research)"})
    try:
        with urlopen(request, timeout=timeout_seconds, context=certificate_context()) as response:
            payload = response.read()
            headers = {key.lower(): value for key, value in response.headers.items()}
            final_url = response.url
            status = getattr(response, "status", 200)
    except OSError as exc:
        raise FetchError(f"{source.id}: {exc}") from exc
    if not payload:
        raise FetchError(f"{source.id}: response body is empty")
    checksum = sha256_bytes(payload)
    retrieved_at = _timestamp()
    # Query parameters (for example FRED's ``?id=FEDFUNDS``) are not part of
    # a filename extension.  Preserve the server path's extension only.
    suffix = Path(urlsplit(final_url).path).suffix or ".bin"
    relative = Path("raw") / source.id / f"{retrieved_at.replace(':', '').replace('-', '')}_{checksum[:12]}{suffix}"
    destination = workspace / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return {
        "source_id": source.id,
        "url": source.url,
        "final_url": final_url,
        "retrieved_at": retrieved_at,
        "http_status": status,
        "content_type": headers.get("content-type"),
        "etag": headers.get("etag"),
        "last_modified": headers.get("last-modified"),
        "bytes": len(payload),
        "sha256": checksum,
        "relative_path": str(relative),
        "parser": source.parser,
        "status": "FETCHED",
    }


def fetch_sources(workspace: Path, config: PipelineConfig, source_ids: Iterable[str] | None = None) -> list[dict[str, object]]:
    requested = set(source_ids or ())
    sources = [source for source in config.sources if source.enabled and (not requested or source.id in requested)]
    unknown = requested - {source.id for source in config.sources}
    if unknown:
        raise FetchError(f"Unknown source ID(s): {', '.join(sorted(unknown))}")
    if not sources:
        raise FetchError("No enabled sources selected")
    manifest = read_json(manifest_path(workspace), {"schema_version": 1, "artifacts": []})
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("artifacts"), list):
        raise FetchError("raw manifest has an unsupported schema")
    records: list[dict[str, object]] = []
    for source in sources:
        try:
            record = fetch_source(workspace, source)
        except FetchError as exc:
            # Keep a durable audit trail even when a later source in a batch
            # fails.  Earlier successful payloads remain reproducible and the
            # failed request is visible rather than silently disappearing.
            manifest["artifacts"].append(
                {
                    "source_id": source.id,
                    "url": source.url,
                    "retrieved_at": _timestamp(),
                    "parser": source.parser,
                    "status": "FAILED",
                    "error": str(exc),
                }
            )
            write_json(manifest_path(workspace), manifest)
            raise
        manifest["artifacts"].append(record)
        records.append(record)
        # Persist after every source so an interrupted batch never leaves a
        # raw file without provenance in the manifest.
        write_json(manifest_path(workspace), manifest)
    return records


def latest_artifact(workspace: Path, source_id: str) -> dict[str, object]:
    manifest = read_json(manifest_path(workspace), {"artifacts": []})
    artifacts = [item for item in manifest.get("artifacts", []) if item.get("source_id") == source_id and item.get("status") == "FETCHED"]
    if not artifacts:
        raise FetchError(f"No fetched raw artifact for {source_id}; run fetch first")
    return max(artifacts, key=lambda item: str(item.get("retrieved_at", "")))
