"""
test_mechanic.py — G1..G5 gate tests for far-games/tools/mechanic.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "tools"))

from mechanic import compile_mechanic, gate  # noqa: E402


def _base_axes(**overrides):
    axes = {
        "medium": "web",
        "mechanic": "puzzle",
        "loop_length": "short_5-15min",
        "narrative_register": "minimal",
        "control_scheme": "keyboard_mouse",
        "save_format": "json",
        "royalty_mode": "original",
        "source_id": "kenney/puzzle-pack",
        "age_rating": "everyone",
        "performance_target": "60fps",
        "difficulty_curve": "linear_ramp",
        "commit_asset": "gate",
    }
    axes.update(overrides)
    return axes


def test_G1_repro_id():
    a = _base_axes()
    s1 = compile_mechanic(a)
    s2 = compile_mechanic(a)
    s3 = compile_mechanic(_base_axes(mechanic="shooter"))
    assert s1.mechanic_id == s2.mechanic_id, "G1: same axes -> same id"
    assert s1.mechanic_id != s3.mechanic_id, "G1: different axes -> different id"
    print("G1: ok")


def test_G2_banned_motif():
    s = compile_mechanic(_base_axes(banned_motifs=["microtransactions"]))
    allow, reason = gate(s, "we have microtransactions everywhere")
    assert not allow and "banned_motif" in reason, f"G2 fail: {reason}"
    allow, reason = gate(s, "")
    assert allow and reason == "ok", f"G2 clean fail: {reason}"
    print("G2: ok")


def test_G3_ids_survive_reload():
    axes = _base_axes()
    s1 = compile_mechanic(axes)
    s2 = compile_mechanic(axes)
    assert s1.mechanic_id == s2.mechanic_id
    assert s1.medium == s2.medium == "web"
    print("G3: ok")


def test_G4_axes_distinct():
    s_base = compile_mechanic(_base_axes())
    s_med = compile_mechanic(_base_axes(medium="mobile"))
    s_loop = compile_mechanic(_base_axes(loop_length="medium_15-60min"))
    s_curve = compile_mechanic(_base_axes(difficulty_curve="adaptive"))
    ids = {s_base.mechanic_id, s_med.mechanic_id,
           s_loop.mechanic_id, s_curve.mechanic_id}
    assert len(ids) == 4, f"G4: expected 4 distinct, got {len(ids)}"
    print("G4: ok")


def test_G5_no_house_default():
    allow, reason = gate(None)
    assert not allow and reason == "no_mechanic", f"G5 fail: {reason}"
    s_forbid = compile_mechanic(_base_axes(commit_asset="forbid"))
    allow, reason = gate(s_forbid)
    assert not allow and reason == "commit_forbidden", f"G5 forbid fail: {reason}"
    print("G5: ok")


def main():
    test_G1_repro_id()
    test_G2_banned_motif()
    test_G3_ids_survive_reload()
    test_G4_axes_distinct()
    test_G5_no_house_default()
    print("\nALL G1..G5 PASS")


if __name__ == "__main__":
    main()