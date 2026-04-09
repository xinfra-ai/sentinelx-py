# sentinelx-sdk

Whether it's an AI agent, a bank transfer, or a power grid — execution is permanent.

`sentinelx-sdk` enforces at the commit boundary. Before the action executes. Server-side. Unbypassable. Cryptographic receipt on every decision.

[![license](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![python](https://img.shields.io/badge/python-3.9+-blue)](https://python.org)

## Install

```bash
pip install sentinelx-sdk
```

## Quick Start

```python
from sentinelx import SentinelX, AdmissibilityError

sx = SentinelX(api_key="YOUR_API_KEY")

try:
    receipt = sx.enforce("ai.agent.action.execute", {
        "agent_id":               "agent-001",
        "action_type":            "file.write",
        "human_in_loop_required": True,
        "human_in_loop":          False,
        "action_within_scope":    True,
        "action_logged":          True,
    })
    print("ADMISSIBLE | Receipt:", receipt.receipt_hash)

except AdmissibilityError as e:
    print("INADMISSIBLE:", e.summary)
    print("Constraint:", e.constraint)
    print("Violations:", len(e.violations))
    print("Receipt hash:", e.receipt_hash)
    # Action never executed. Receipt sealed.
```

## SCADA Example

```python
receipt = sx.enforce("scada.setpoint.change", {
    "device_id":                  "rtu-456",
    "parameter":                  "voltage_setpoint",
    "operator_authorized":        True,
    "change_ticket_linked":       True,
    "change_logged":              True,
    "two_person_auth":            True,
    "rollback_procedure_defined": True,
    "action_logged":              True,
})
print("ADMISSIBLE | Receipt:", receipt.receipt_hash)
```

## Observe Mode — Never Throws

```python
# Always returns receipt. Never raises on INADMISSIBLE.
# Useful for logging pipelines and observe mode.
receipt = sx.evaluate("wire.transfer.execute", context)
print(receipt.verdict)  # "ADMISSIBLE" or "INADMISSIBLE"
```

## How It Works

SentinelX sits at the commit boundary between your system and execution. Before any irreversible action fires, the enforcement engine evaluates it against invariant constraints and returns a deterministic verdict with a provenance receipt.

- **ADMISSIBLE** → receipt returned, action may proceed
- **INADMISSIBLE** → `AdmissibilityError` raised, nothing executes, receipt sealed

The enforcement decision is made server-side. It cannot be bypassed client-side.

## AdmissibilityError

```python
except AdmissibilityError as e:
    e.verdict        # "INADMISSIBLE"
    e.constraint     # "AI_HUMAN_IN_LOOP_ENFORCED"
    e.violation_code # "INV-046"
    e.violations     # list of matched invariants
    e.summary        # "Action blocked: human oversight required before execution"
    e.receipt_hash   # sha256 sealed receipt
    e.trace_id       # unique per evaluation
    e.receipt        # full Receipt object
```

## Domain Coverage

| Domain | Example Actions |
|--------|----------------|
| AI/ML Agents | `ai.agent.action.execute`, `ml.model.deploy.production` |
| Financial | `wire.transfer.execute`, `algo.trade.execute` |
| OT/SCADA | `scada.setpoint.change`, `breaker.open.execute` |
| Grid/Energy | `load.transfer.execute`, `der.curtailment.execute.batch` |
| Cyber/RMM | `rmm.script.execute`, `rmm.privilege.escalate` |
| Healthcare | `medication.order.execute`, `patient.record.modify` |
| Mobility | `driver.payout.execute`, `surge.pricing.apply` |

## Get an API Key

```bash
curl -X POST https://enforce.sentinelx.ai/generate-key
```

Or visit [sentinelx.ai](https://sentinelx.ai).

## Links

- [sentinelx.ai](https://sentinelx.ai)
- [enforce.sentinelx.ai](https://enforce.sentinelx.ai)
- [@sentinelx/sdk on npm](https://npmjs.com/package/@sentinelx/sdk)
- [sentinelx-go on GitHub](https://github.com/xinfra-ai/sentinelx-go)

## License

Apache-2.0
