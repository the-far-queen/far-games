---
name: mechanic-schema
description: >-
  Use when the user wants to compile a game mechanic, run the G gate, or load public-domain
  source discipline. Triggers: "game mechanic", "mechanic axes", "compile mechanic",
  "G gate", "kenney", "opengameart", "sokoban".
---

# Mechanic schema (far-games)

The mechanic is the **canonical unit** of game design in this repo. Every mechanic is a frozen dataclass with a deterministic id.

## Compile

```python
from far_games.tools.mechanic import compile_mechanic, gate

m = compile_mechanic({
    "medium": "web",
    "mechanic": "puzzle",
    "loop_length": "micro_<5min",
    "art_style_id": "kenney/puzzle-pack",
    "narrative_register": "none",
    "control_scheme": "keyboard_mouse",
    "save_format": "json",
    "royalty_mode": "mit",
    "source_id": "github.com/sokoban-clones/grid-push",
    "age_rating": "everyone",
    "performance_target": "60fps",
    "difficulty_curve": "logarithmic_plateau",
})
```

The mechanic_id is `sha256(canonical(axes))[:16]`. Same axes → same id.

## Gate

```python
allow, reason = gate(m, asset_text="...")
```

`commit_asset="gate"` refuses naked mechanics (`no_mechanic`) or mechanics without `source_id` (`no_source_id`) or with invalid `royalty_mode`. `banned_motifs` matches against asset text.

## Public-domain sources

See `docs/sources.md` in the repo. opengameart.org (CC0) + kenney.nl + libtcod + gnu games + freegamedev wiki.

## See also

- `AGENTS.md` in the repo — the contract
- `tests/test_mechanic.py` — G1..G5
- `examples/example-sokoban-clone.py` — worked example