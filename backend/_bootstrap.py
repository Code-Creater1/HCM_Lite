# backend/_bootstrap.py  — run once: python _bootstrap.py
from pathlib import Path

BASE = Path(__file__).parent

FILES = {
    # Every package needs an __init__.py so Python sees it as a module
    "app/__init__.py":          "",
    "app/core/__init__.py":     "",
    "app/db/__init__.py":       "",
    "app/models/__init__.py":   "",
    "app/schemas/__init__.py":  "",
    "app/services/__init__.py": "",
    "app/api/__init__.py":      "",

    # The missing file that's crashing startup
    "app/db/base.py": (
        "from sqlalchemy.orm import DeclarativeBase\n"
        "\n"
        "class Base(DeclarativeBase):\n"
        "    pass\n"
    ),
}

for rel, content in FILES.items():
    p = BASE / rel
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        print(f"  + CREATED  {rel}")
    elif p.stat().st_size == 0 and content:
        p.write_text(content, encoding="utf-8")
        print(f"  ~ FILLED   {rel} (was empty)")
    else:
        print(f"  ✓ exists   {rel}")
