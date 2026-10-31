"""Ask the Dartmouth backend whether this pull request needs review."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def require_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable {name} is missing.")
    return value


def pull_request_context() -> tuple[str, str]:
    """Return the base and head SHAs from GitHub's pull-request event file."""
    event_path = Path(require_environment("GITHUB_EVENT_PATH"))
    event = json.loads(event_path.read_text(encoding="utf-8"))
    try:
        pull_request = event["pull_request"]
        return pull_request["base"]["sha"], pull_request["head"]["sha"]
    except (KeyError, TypeError) as error:
        raise RuntimeError("This workflow must run for a pull_request event.") from error


def pull_request_diff(base_sha: str, head_sha: str) -> str:
    completed = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=0", base_sha, head_sha],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def backend_check_url(backend_url: str) -> str:
    base_url = backend_url.rstrip("/")
    return base_url if base_url.endswith("/check") else f"{base_url}/check"


def post_json(url: str, payload: dict[str, str], gate_secret: str) -> dict[str, object]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Gate-Secret": gate_secret,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except HTTPError as error:
        raise RuntimeError(f"Backend check failed with HTTP {error.code}.") from error
    except URLError as error:
        raise RuntimeError("Could not reach BACKEND_URL.") from error
    try:
        data = json.loads(body)
    except json.JSONDecodeError as error:
        raise RuntimeError("Backend /check did not return JSON.") from error
    if not isinstance(data, dict):
        raise RuntimeError("Backend /check returned an unexpected response.")
    return data


def write_output(name: str, value: str) -> None:
    """Make a value available to the following GitHub Actions step."""
    output_path = os.getenv("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write(f"{name}={value}\n")


def main() -> int:
    backend_url = require_environment("BACKEND_URL")
    gate_secret = require_environment("GATE_SECRET")
    repo = require_environment("GITHUB_REPOSITORY")
    base_sha, head_sha = pull_request_context()
    diff = pull_request_diff(base_sha, head_sha)
    result = post_json(backend_check_url(backend_url), {"repo": repo, "diff": diff}, gate_secret)

    status = result.get("status")
    if status == "pass":
        print("Comprehension Gate passed.")
        return 0
    if status != "fail":
        raise RuntimeError("Backend /check returned an unknown status.")

    unanswered = result.get("unanswered")
    if not isinstance(unanswered, list):
        raise RuntimeError("Backend /check returned an invalid unanswered list.")
    write_output("gate_status", "fail")
    write_output("unanswered", json.dumps(unanswered, separators=(",", ":")))
    print("Comprehension Gate found unanswered questions. The workflow will post a pull-request comment.")
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Comprehension Gate error: {error}")
        raise SystemExit(1)
