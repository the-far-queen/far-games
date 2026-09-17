# AGENTS.md — (far-games repo)

> A mechanic is not a vibe.

This file is the contract. Every commit gate checks against it.
Every mechanic references it. Every test (G1..G5) reads it.

If you change the schema, update AGENTS.md first. The repo is downstream
of this file.

## What this repo is

mechanics, levels, art assets, code modules, narrative scripts, save files, the games pipeline.

## Packet

```
mechanic  Mechanic | AssetRef
```

**No asset without `mechanic_id` + `hash`.** The gate refuses naked assets.

## Error this repo exists to stop

conflating every game into one house style. 'Make it fun' is not an axis. Mechanic, loop-length, and difficulty-curve are.

## Axes

games-pipeline axes: medium, mechanic, loop-length, difficulty-curve, art-style-id, narrative-register, control-scheme, platform, save-format, source-discipline, banned-motifs, royalty-mode, age-rating, performance-target.

The schema is in the pipeline source (`tools/sheet.py`). Axes are the
contract; vibe is not.

## Surface

```python
mechanic.compile(axes) -> Mechanic
level.from_mechanics(mechanics)
art.from_style(style_id)
narrative.beat(mechanic, beat_type)
save.format(state, fmt_id)
```

## Gate

`commit_asset` defaults to `{gate}`. The gate checks:

1. `mechanic_id` is set.
2. `mechanic_id == sha256(canonical(axes))`.
3. `variant_of` (if set) is a known parent.
4. No banned-motifs present.
5. Source-discipline: every claim links to a source.

A naked mechanic (no `mechanic_id`) is refused with reason `no_mechanic`.

## Tests

| # | Test | What it checks |
|---|---|---|
| G1 | repro id | Mechanic with same axes -> same id; different axes -> different id. |
| G2 | banned terms rejected | Mechanic with banned-terms + asset containing them -> refused. |
| G3 | ids survive restart | Compile + serialize + deserialize -> all ids preserved. |
| G4 | two different settings cannot share id | Vary primary axes -> different id. |
| G5 | prompt without mechanic does not apply house | Naked prompt + gate -> refused, no fallback to default. |

## Anti-patterns

- house-style default
- vibe without mechanics
- AI art without source-discipline
- loot boxes without age-rating.

## Related

- the-far-queen/far-art (art substrate), the-far-queen/far-film (cutscenes), the-far-queen/far-music (audio)

## License

MIT. Free for all agents, human and non-human.
