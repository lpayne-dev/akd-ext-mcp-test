#!/usr/bin/env python3
"""Simple OpenAI API key check using .env."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import error, request


def load_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    data: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if (
            len(value) >= 2
            and ((value[0] == value[-1]) and value.startswith(("\"", "'")))
        ):
            value = value[1:-1]
        data[key] = value
    return data


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    dotenv_path = repo_root / ".env"

    dotenv = load_dotenv(dotenv_path)
    if "OPENAI_API_KEY" in dotenv:
        # Prefer the value from .env for this check.
        os.environ["OPENAI_API_KEY"] = dotenv["OPENAI_API_KEY"]

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        keys = sorted(dotenv.keys())
        keys_display = ", ".join(keys) if keys else "(none found)"
        print("OPENAI_API_KEY is not set.")
        print(f"Keys found in .env: {keys_display}")
        return 1

    req = request.Request("https://api.openai.com/v1/models")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with request.urlopen(req, timeout=15) as resp:
            body = resp.read()
        payload = json.loads(body)
        model_ids = [item.get("id") for item in payload.get("data", [])[:3]]
        model_ids = [m for m in model_ids if m]
        sample = ", ".join(model_ids) if model_ids else "(no models listed)"
        print("OK: API key is valid.")
        print(f"Sample models: {sample}")
        return 0
    except error.HTTPError as exc:
        if exc.code == 401:
            print("Unauthorized (401): API key is invalid or revoked.")
        elif exc.code == 429:
            print("Rate limited (429): key is valid but throttled; try again later.")
        else:
            print(f"HTTP {exc.code}: {exc.reason}")
        return 2
    except error.URLError as exc:
        print(f"Network error: {exc.reason}")
        return 3
    except json.JSONDecodeError:
        print("Unexpected response: could not parse JSON.")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
