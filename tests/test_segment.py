from fastapi.testclient import TestClient
from segments.main import app

client = TestClient(app)


def test_splits_low_and_high():
    payload = client.post("/segment", json={"rows": [{'id': 'a', 'spend': 10}, {'id': 'b', 'spend': 12}, {'id': 'c', 'spend': 90}]}).json()
    clusters = {row["spend"]: row["cluster"] for row in payload["rows"]}
    lows = [v for k, v in clusters.items() if k == min(clusters)]
    highs = [v for k, v in clusters.items() if k == max(clusters)]
    assert lows[0] != highs[0]
