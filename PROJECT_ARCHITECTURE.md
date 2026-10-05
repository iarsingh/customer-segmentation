# customer-segmentation — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

Split customers into low and high spend clusters using the min and max as starting centers.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/segments/__init__.py"]
    M1["src/segments/main.py"]
    M2["src/segments/segment.py"]
    M1 -->|imports| M2
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/segments/main.py`](src/segments/main.py) | HTTP handlers: `GET /healthz`, `POST /segment` |
| [`src/segments/segment.py`](src/segments/segment.py) | Functions: `segment` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/segments/__init__.py`](src/segments/__init__.py) | Implementation or supporting configuration |
| [`tests/test_segment.py`](tests/test_segment.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `GET /healthz` | `healthz` | [`src/segments/main.py`](src/segments/main.py#L8) |
| `POST /segment` | `post_segment` | [`src/segments/main.py`](src/segments/main.py#L13) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `segment(rows, k=2)`

Source: [`src/segments/segment.py`](src/segments/segment.py#L5).

Calls visible in this function: `InputError`, `abs`, `assigned.append`, `float`, `isinstance`, `len`, `max`, `min`, `range`, `round`, `values.append`, `zip`.

```python
def segment(rows, k=2):
    if not isinstance(rows, list) or len(rows) < 2:
        raise InputError("need at least two rows")
    values = []
    for row in rows:
        try:
            values.append(float(row["spend"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise InputError("each row needs numeric spend") from exc
    lo, hi = min(values), max(values)
    centers = [lo, hi] if k == 2 else [lo + (hi - lo) * i / (k - 1) for i in range(k)]
    assigned = []
    for row, value in zip(rows, values):
        cluster = min(range(len(centers)), key=lambda i: abs(value - centers[i]))
        assigned.append({**row, "cluster": cluster})
    return {"clusters": k, "centers": [round(c, 4) for c in centers], "rows": assigned}
```

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `HTTPException(status_code=422, detail=str(exc))` | [`src/segments/main.py`](src/segments/main.py#L17) |
| `InputError('need at least two rows')` | [`src/segments/segment.py`](src/segments/segment.py#L7) |
| `InputError('each row needs numeric spend')` | [`src/segments/segment.py`](src/segments/segment.py#L13) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data flow and design decisions

### What is the input-to-output contract of `segment`

In [`src/segments/segment.py`](src/segments/segment.py#L5), `segment(rows, k=2)` receives the inputs. The function computes these intermediate values:

- `values = []`
- `lo, hi = (min(values), max(values))`
- `centers = [lo, hi] if k == 2 else [lo + (hi - lo) * i / (k - 1) for i in range(k)]`
- `assigned = []`

Its result is defined by:

- `{'clusters': k, 'centers': [round(c, 4) for c in centers], 'rows': assigned}`

### Which decision rules or boundary conditions should an interviewer challenge

The implementation in [`src/segments/segment.py`](src/segments/segment.py#L5) branches on:

- `not isinstance(rows, list) or len(rows) < 2`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_segment.py`](tests/test_segment.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.
