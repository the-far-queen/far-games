"""
example-sokoban-clone.py — public-domain sokoban-like mechanic compiled
via far-games pipeline.

Source: open-source sokoban clones on github (original sokoban puzzle
game is from 1982 — pre-copyright era in many jurisdictions). Reference:
kenney.nl for tile assets + opengameart.org for cc0 sprite packs.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "tools"))

from mechanic import compile_mechanic, gate  # noqa: E402

axes = {
    "medium": "web",
    "mechanic": "puzzle",
    "loop_length": "micro_<5min",
    "art_style_id": "kenney/puzzle-pack",
    "narrative_register": "none",
    "control_scheme": "keyboard_mouse",
    "save_format": "json",
    "source_id": "github.com/sokoban-clones/grid-push",
    "source_discipline": "original puzzle concept (1982), MIT-licensed code",
    "banned_motifs": ["microtransactions", "ads", "always_online"],
    "royalty_mode": "mit",
    "age_rating": "everyone",
    "performance_target": "60fps",
    "difficulty_curve": "logarithmic_plateau",
    "tool_id": "sokoban-pipeline",
    "commit_asset": "gate",
}

m = compile_mechanic(axes)

print(f"mechanic_id:    {m.mechanic_id}")
print(f"medium:         {m.medium}")
print(f"mechanic:       {m.mechanic}")
print(f"loop_length:    {m.loop_length}")
print(f"difficulty:     {m.difficulty_curve}")
print(f"royalty_mode:   {m.royalty_mode}")
print(f"age_rating:     {m.age_rating}")
print()

allow, reason = gate(m)
print(f"gate: allow={allow}, reason={reason}")

allow, reason = gate(None)
print(f"gate(naked): allow={allow}, reason={reason}")

# verify banned motif is caught in asset text
test_asset = "buy gems and coins to unlock more levels"
allow, reason = gate(m, test_asset)
print(f"gate(banned): allow={allow}, reason={reason}")

m2 = compile_mechanic(axes)
assert m.mechanic_id == m2.mechanic_id, "must be deterministic"
print(f"\ndeterministic: ✓")