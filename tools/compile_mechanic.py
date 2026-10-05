"""
compile_mechanic.py — CLI for compiling a mechanic YAML/JSON file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from mechanic import compile_mechanic, mechanic_to_dict  # noqa: E402


def _load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    out = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Cannot parse YAML line: {line!r}")
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        if val.startswith("[") and val.endswith("]"):
            items = val[1:-1].split(",")
            val = [i.strip().strip('"').strip("'") for i in items if i.strip()]
        elif isinstance(val, str):
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
        out[key] = val
    return out


def main(argv):
    p = argparse.ArgumentParser(description="Compile a far-games mechanic.")
    p.add_argument("path", nargs="?", help="Path to mechanic YAML/JSON file.")
    p.add_argument("--stdin", action="store_true", help="Read JSON from stdin.")
    args = p.parse_args(argv)

    if args.stdin:
        axes = json.loads(sys.stdin.read())
    elif args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"error: {path} does not exist", file=sys.stderr)
            return 2
        axes = _load_yaml(path)
    else:
        from mechanic import (MEDIUMS, MECHANICS, LOOP_LENGTHS,
                             CONTROL_SCHEMES, AGE_RATINGS)
        print("far-games mechanic schema summary:")
        print(f"  mediums: {len(MEDIUMS)} ({sorted(MEDIUMS)[:6]}...)")
        print(f"  mechanics: {len(MECHANICS)} ({sorted(MECHANICS)[:6]}...)")
        print(f"  loop_lengths: {sorted(LOOP_LENGTHS)}")
        print(f"  control_schemes: {sorted(CONTROL_SCHEMES)}")
        print(f"  age_ratings: {sorted(AGE_RATINGS)}")
        return 0

    try:
        m = compile_mechanic(axes)
    except (KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    out = mechanic_to_dict(m)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))