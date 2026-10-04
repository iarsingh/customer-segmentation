class InputError(ValueError):
    pass


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
