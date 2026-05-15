import httpx
import json

payload = {
    "issue": {
        "id": 12345,
        "number": 42,
        "title": "Bug: Profile picture not updating",
        "body": "When I try to update my profile picture, it doesn't change on the dashboard.",
        "state": "open",
        "labels": [{"name": "bug"}],
        "user": {"login": "testuser"},
        "created_at": "2024-05-16T00:00:00Z",
        "updated_at": "2024-05-16T00:00:00Z",
        "html_url": "https://github.com/user/test-repo/issues/42"
    }
}

try:
    response = httpx.post("http://127.0.0.1:8001/simulate", json=payload, timeout=60.0)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
