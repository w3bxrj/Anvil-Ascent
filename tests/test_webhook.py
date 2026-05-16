import httpx

import asyncio

import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

SAMPLE_BUG_ISSUE = {

    "action": "opened",

    "issue": {

        "id": 1234567890,

        "number": 42,

        "title": "App crashes when clicking login button",

        "body": "When I click the login button, the app crashes with a NullPointerException. This happens on Android 14 only.",

        "state": "open",

        "labels": [{"name": "bug"}, {"name": "android"}],

        "user": {"login": "testuser"},

        "created_at": "2024-05-15T10:30:00Z",

        "updated_at": "2024-05-15T10:30:00Z",

        "html_url": "https://github.com/user/repo/issues/42"

    },

    "repository": {

        "name": "my-app",

        "full_name": "user/my-app"

    },

    "sender": {"login": "testuser"}

}

SAMPLE_FEATURE_ISSUE = {

    "action": "opened",

    "issue": {

        "id": 1234567891,

        "number": 43,

        "title": "Add dark mode support",

        "body": "It would be nice to have a dark mode option in settings. Many users have requested this feature.",

        "state": "open",

        "labels": [{"name": "enhancement"}],

        "user": {"login": "feature-requester"},

        "created_at": "2024-05-15T11:00:00Z",

        "updated_at": "2024-05-15T11:00:00Z",

        "html_url": "https://github.com/user/repo/issues/43"

    },

    "repository": {

        "name": "autonomous-issue-resolver",

        "full_name": "regencypatel/autonomous-issue-resolver"

    },

    "sender": {"login": "feature-requester"}

}

SAMPLE_SECURITY_ISSUE = {

    "action": "opened",

    "issue": {

        "id": 1234567892,

        "number": 44,

        "title": "SQL Injection vulnerability in login endpoint",

        "body": "The login endpoint is vulnerable to SQL injection. This is a critical security issue.",

        "state": "open",

        "labels": [{"name": "security"}, {"name": "critical"}],

        "user": {"login": "security-researcher"},

        "created_at": "2024-05-15T12:00:00Z",

        "updated_at": "2024-05-15T12:00:00Z",

        "html_url": "https://github.com/user/repo/issues/44"

    },

    "repository": {

        "name": "my-app",

        "full_name": "user/my-app"

    },

    "sender": {"login": "security-researcher"}

}

async def run_tests():

    """Send test payloads to local server"""

    async with httpx.AsyncClient() as client:

        for name, payload in [

            ("🐛 Bug", SAMPLE_BUG_ISSUE),

            ("✨ Feature", SAMPLE_FEATURE_ISSUE),

            ("🔒 Security", SAMPLE_SECURITY_ISSUE)

        ]:

            print(f"\n{'='*50}")

            print(f"Testing {name} issue...")

            print(f"{'='*50}")

            try:

                resp = await client.post(

                    "http://localhost:8000/webhook/github",

                    json=payload,

                    headers={"X-GitHub-Event": "issues"},

                    timeout=10.0

                )

                print(f"✅ Status: {resp.status_code}")

                data = resp.json()

                print(f"📊 Classification: {data.get('classification', {})}")

            except Exception as e:

                print(f"❌ Error: {e}")

if __name__ == "__main__":

    print("🚀 Starting webhook tests...")

    print("Make sure server is running: uvicorn src.main:app --reload")

    print(f"{'='*50}\n")

    asyncio.run(run_tests())
