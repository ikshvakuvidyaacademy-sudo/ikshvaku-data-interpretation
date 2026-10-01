#!/usr/bin/env python3
"""validate_questions.py - DI Validator"""
import os, sys, json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "questions"

def run():
    total, errors, seen = 0, [], set()
    for jf in QUESTIONS_DIR.rglob("*.json"):
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data if isinstance(data, list) else [data]
            for idx, q in enumerate(items):
                total += 1
                qid = q.get("id")
                if not qid:
                    errors.append(f"{jf} #{idx}: Missing ID")
                elif qid in seen:
                    errors.append(f"{jf} #{idx}: Duplicate ID {qid}")
                seen.add(qid)
                if q.get("answer") not in q.get("options", []):
                    errors.append(f"{jf} {qid}: Answer not in options")
        except Exception as e:
            errors.append(f"{jf}: {e}")

    print("=" * 80)
    print(" IKSHVAKU DATA INTERPRETATION - VALIDATION REPORT")
    print("=" * 80)
    print(f" Total Checked : {total:,}")
    print(f" Errors Found  : {len(errors)}")
    print("=" * 80)
    return len(errors) == 0

if __name__ == "__main__":
    sys.exit(0 if run() else 1)
