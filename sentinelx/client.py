from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional
import urllib.request
import urllib.error

BASE_URL = "https://enforce.sentinelx.ai"
VERSION = "0.1.0"


@dataclass
class Violation:
    primitive: str
    code: str
    constraint: str
    message: str


@dataclass
class Receipt:
    verdict: str
    summary: str
    constraint: Optional[str]
    constraint_pack: str
    violation_code: Optional[str]
    violations: list[Violation]
    mode: str
    envelope_class: str
    trace_id: str
    request_hash: str
    receipt_hash: str
    inv_version: str
    latency_ms: int

    @classmethod
    def from_dict(cls, data: dict) -> "Receipt":
        return cls(
            verdict=data.get("verdict", ""),
            summary=data.get("summary", ""),
            constraint=data.get("constraint"),
            constraint_pack=data.get("constraint_pack", ""),
            violation_code=data.get("violation_code"),
            violations=[
                Violation(
                    primitive=v.get("primitive", ""),
                    code=v.get("code", ""),
                    constraint=v.get("constraint", ""),
                    message=v.get("message", ""),
                )
                for v in data.get("violations", [])
            ],
            mode=data.get("mode", ""),
            envelope_class=data.get("envelope_class", ""),
            trace_id=data.get("trace_id", ""),
            request_hash=data.get("request_hash", ""),
            receipt_hash=data.get("receipt_hash", ""),
            inv_version=data.get("inv_version", ""),
            latency_ms=data.get("latency_ms", 0),
        )


class AdmissibilityError(Exception):
    """Raised when an action is INADMISSIBLE."""

    def __init__(self, receipt: Receipt):
        self.receipt = receipt
        self.verdict = receipt.verdict
        self.constraint = receipt.constraint
        self.violation_code = receipt.violation_code
        self.violations = receipt.violations
        self.summary = receipt.summary
        self.receipt_hash = receipt.receipt_hash
        self.trace_id = receipt.trace_id
        super().__init__(f"sentinelx: INADMISSIBLE — {receipt.summary}")


class SentinelX:
    """SentinelX enforcement client."""

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: int = 10,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, action: str, context: dict[str, Any]) -> Receipt:
        payload = json.dumps({"action": action, "context": context}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/v2/enforce",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
                "User-Agent": f"sentinelx-py/{VERSION}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read())
                return Receipt.from_dict(data)
        except urllib.error.HTTPError as e:
            data = json.loads(e.read())
            receipt = Receipt.from_dict(data)
            raise AdmissibilityError(receipt) from None

    def enforce(self, action: str, context: dict[str, Any]) -> Receipt:
        """
        Evaluate action admissibility. Returns Receipt on ADMISSIBLE.
        Raises AdmissibilityError on INADMISSIBLE.
        """
        return self._request(action, context)

    def evaluate(self, action: str, context: dict[str, Any]) -> Receipt:
        """
        Always returns the receipt. Never raises on INADMISSIBLE.
        Useful for logging pipelines and observe mode.
        """
        try:
            return self._request(action, context)
        except AdmissibilityError as e:
            return e.receipt
