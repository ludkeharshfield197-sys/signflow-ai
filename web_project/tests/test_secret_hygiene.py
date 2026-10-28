import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LIVE_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def test_active_python_sources_do_not_contain_embedded_api_credentials():
    findings = []
    for source in PROJECT_ROOT.rglob("*.py"):
        if any(part in {"tests", "__pycache__", "migrations"} for part in source.parts):
            continue
        text = source.read_text(encoding="utf-8", errors="ignore")
        for pattern in LIVE_SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(str(source.relative_to(PROJECT_ROOT)))

    assert findings == []
