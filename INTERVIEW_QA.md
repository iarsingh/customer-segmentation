# customer-segmentation — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does customer-segmentation address, and what can you demonstrate?

Split customers into low and high spend clusters using the min and max as starting centers.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/segments/main.py`](src/segments/main.py): Implementation or supporting configuration.
- [`src/segments/segment.py`](src/segments/segment.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/segments/__init__.py`](src/segments/__init__.py): Implementation or supporting configuration.
- [`tests/test_segment.py`](tests/test_segment.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `segment` and explain the decision it makes?

The main walkthrough here is `segment(rows, k=2)` in [`src/segments/segment.py`](src/segments/segment.py#L5).

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

The implementation calls `InputError`, `abs`, `assigned.append`, `float`, `isinstance`, `len`, `max`, `min`, `range`. In an interview, trace those calls in execution order using a fixture input.

## 4. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=422, detail=str(exc))` in [`src/segments/main.py`](src/segments/main.py#L17).
- `InputError('need at least two rows')` in [`src/segments/segment.py`](src/segments/segment.py#L7).
- `InputError('each row needs numeric spend')` in [`src/segments/segment.py`](src/segments/segment.py#L13).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 5. Which test would you use to demonstrate correctness?

[`tests/test_segment.py`](tests/test_segment.py#L7) contains `test_splits_low_and_high`:

```python
def test_splits_low_and_high():
    payload = client.post("/segment", json={"rows": [{'id': 'a', 'spend': 10}, {'id': 'b', 'spend': 12}, {'id': 'c', 'spend': 90}]}).json()
    clusters = {row["spend"]: row["cluster"] for row in payload["rows"]}
    lows = [v for k, v in clusters.items() if k == min(clusters)]
    highs = [v for k, v in clusters.items() if k == max(clusters)]
    assert lows[0] != highs[0]
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 6. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/segments/main.py`](src/segments/main.py#L8).
- `POST /segment` → `post_segment` in [`src/segments/main.py`](src/segments/main.py#L13).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 7. How would you investigate data ownership and persistence?

Trace the data/configuration files and the code that reads or writes them in the component table. Identify which files are examples, which records are mutable, and which external store is actually configured. I would document those facts before discussing retention, backup, or tenant isolation.

## 8. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 9. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 10. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 11. What is the input-to-output contract of `segment`?

In [`src/segments/segment.py`](src/segments/segment.py#L5), `segment(rows, k=2)` receives the inputs. The function computes these intermediate values:

- `values = []`
- `lo, hi = (min(values), max(values))`
- `centers = [lo, hi] if k == 2 else [lo + (hi - lo) * i / (k - 1) for i in range(k)]`
- `assigned = []`

Its result is defined by:

- `{'clusters': k, 'centers': [round(c, 4) for c in centers], 'rows': assigned}`

## 12. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/segments/segment.py`](src/segments/segment.py#L5) branches on:

- `not isinstance(rows, list) or len(rows) < 2`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
