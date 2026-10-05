"""
mechanic.py — Mechanic compile + gate (far-games).

Mirrors far-film/tools/shot.py structure. The schema (axes) is the
contract declared in AGENTS.md. Naked mechanics (no mechanic_id) are
refused with reason 'no_mechanic'. Banned motifs are refused with
reason 'banned_motif'.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums (the contract — see AGENTS.md)
# ---------------------------------------------------------------------------

# Media (platforms + form factors)
MEDIUMS = {"web", "desktop", "mobile", "tablet", "console", "handheld",
           "vr", "ar", "tabletop", "card", "board"}
# Mechanic (the verbs of the game)
MECHANICS = {"platformer", "shooter", "puzzle", "rpg", "strategy",
             "simulation", "rhythm", "fighting", "racing", "stealth",
             "survival", "sandbox", "tactical", "narrative", "exploration",
             "idle", "incremental", "roguelike", "twin_stick", "match3",
             "deckbuilder", "trading", "tycoon", "adventure", "horror"}
# Loop length (how long one play session is)
LOOP_LENGTHS = {"micro_<5min", "short_5-15min", "medium_15-60min",
                "long_1-4hr", "epic_>4hr", "persistent_forever"}
# Difficulty curve
DIFFICULTY_CURVES = {"flat", "linear_ramp", "exponential_ramp",
                     "logarithmic_plateau", "adaptive",
                     "player_chosen", "fixed_progression"}
# Narrative register
NARRATIVE_REGISTERS = {"none", "minimal", "diegetic", "lyric",
                       "epic", "satiric", "absurdist", "experimental",
                       "documentary", "mythic"}
# Control scheme
CONTROL_SCHEMES = {"keyboard_mouse", "touch", "gamepad", "single_button",
                   "motion", "voice", "eye_tracking", "brain_computer",
                   "asymmetric", "two_player_local", "two_player_remote"}
# Save format
SAVE_FORMATS = {"json", "binary", "sqlite", "cloud_sync", "none",
                "manual_snapshot"}
# Age rating (self-applied)
AGE_RATINGS = {"everyone", "e10+", "teen", "mature_17+", "adults_only_18+"}
# Performance target (per platform baseline)
PERFORMANCE_TARGETS = {"30fps", "60fps", "120fps", "uncapped",
                       "frame_pacing"}
# Royalty mode
ROYALTY_MODES = {"public_domain", "cc0", "cc_by", "cc_by_sa",
                 "original", "gpl", "mit"}
# Commit asset gate
COMMIT_ASSET = {"gate", "allow", "forbid"}


# ---------------------------------------------------------------------------
# Mechanic (the canonical record)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Mechanic:
    """A game mechanic — frozen record of axes per AGENTS.md."""

    # identity / lineage
    mechanic_id: str
    variant_of: str
    source_id: str  # pd oss content + license

    # Group A — medium + mechanic + loop
    medium: str
    mechanic: str
    loop_length: str

    # Group B — style + narrative
    art_style_id: str
    narrative_register: str

    # Group C — control + save
    control_scheme: str
    save_format: str

    # Group D — source discipline
    source_discipline: str
    banned_motifs: Tuple[str, ...]
    royalty_mode: str
    age_rating: str
    performance_target: str
    difficulty_curve: str

    # Pipeline
    tool_id: str
    model_id: str
    generator_may_propose: bool
    commit_asset: str


# ---------------------------------------------------------------------------
# Compile (the canonical form for hashing)
# ---------------------------------------------------------------------------

def _canonical(axes: Dict[str, Any]) -> str:
    """Return a canonical JSON string for hashing.

    Derived identity fields (mechanic_id) are stripped before hashing.
    """
    derived = {"mechanic_id"}
    filtered = {k: v for k, v in axes.items() if k not in derived}

    def norm(v):
        if isinstance(v, (list, tuple)):
            return sorted([norm(x) for x in v if x is not None])
        if isinstance(v, dict):
            return {k: norm(val) for k, val in sorted(v.items())}
        if v is None:
            return None
        return v

    return json.dumps(norm(filtered), sort_keys=True, separators=(",", ":"))


def compile_mechanic(axes: Dict[str, Any]) -> Mechanic:
    """Compile a dict of mechanic axes into a frozen Mechanic.

    The mechanic_id is sha256(canonical(axes)) truncated to 16 hex chars.
    """
    canonical = _canonical(axes)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    # Validate enums
    for k, vs, label in [
        ("medium", MEDIUMS, "Medium"),
        ("mechanic", MECHANICS, "Mechanic"),
        ("loop_length", LOOP_LENGTHS, "Loop"),
        ("difficulty_curve", DIFFICULTY_CURVES, "Difficulty"),
        ("narrative_register", NARRATIVE_REGISTERS, "Narrative"),
        ("control_scheme", CONTROL_SCHEMES, "Control"),
        ("save_format", SAVE_FORMATS, "Save"),
        ("age_rating", AGE_RATINGS, "Content"),
        ("performance_target", PERFORMANCE_TARGETS, "Performance"),
        ("royalty_mode", ROYALTY_MODES, "Lineage"),
        ("commit_asset", COMMIT_ASSET, "Pipeline"),
    ]:
        v = axes.get(k)
        if v is not None and v not in vs:
            raise ValueError(f"{label} axis {k!r}={v!r} not in {sorted(vs)}")

    return Mechanic(
        mechanic_id=digest,
        variant_of=axes.get("variant_of", ""),
        source_id=axes.get("source_id", ""),
        medium=axes.get("medium", "web"),
        mechanic=axes.get("mechanic", "puzzle"),
        loop_length=axes.get("loop_length", "short_5-15min"),
        art_style_id=axes.get("art_style_id", ""),
        narrative_register=axes.get("narrative_register", "minimal"),
        control_scheme=axes.get("control_scheme", "keyboard_mouse"),
        save_format=axes.get("save_format", "json"),
        source_discipline=axes.get("source_discipline", ""),
        banned_motifs=tuple(axes.get("banned_motifs", [])),
        royalty_mode=axes.get("royalty_mode", "original"),
        age_rating=axes.get("age_rating", "everyone"),
        performance_target=axes.get("performance_target", "60fps"),
        difficulty_curve=axes.get("difficulty_curve", "linear_ramp"),
        tool_id=axes.get("tool_id", ""),
        model_id=axes.get("model_id", ""),
        generator_may_propose=bool(axes.get("generator_may_propose", False)),
        commit_asset=axes.get("commit_asset", "gate"),
    )


# ---------------------------------------------------------------------------
# Gate (the single commit_asset checker)
# ---------------------------------------------------------------------------

def gate(mechanic: Optional[Mechanic], asset_text: str = "") -> Tuple[bool, str]:
    """Check the gate. Returns (allow, reason)."""

    if mechanic is None:
        return False, "no_mechanic"

    if mechanic.commit_asset == "forbid":
        return False, "commit_forbidden"

    if mechanic.commit_asset == "allow":
        return True, "ok"

    # commit_asset == "gate" (default)
    if not mechanic.mechanic_id:
        return False, "no_mechanic_id"

    if not mechanic.source_id:
        return False, "no_source_id"

    if mechanic.royalty_mode not in ROYALTY_MODES:
        return False, f"royalty_mode_invalid:{mechanic.royalty_mode}"

    if mechanic.banned_motifs:
        for motif in mechanic.banned_motifs:
            if re.search(re.escape(motif), asset_text, re.IGNORECASE):
                return False, f"banned_motif:{motif}"

    return True, "ok"


# ---------------------------------------------------------------------------
# to_dict
# ---------------------------------------------------------------------------

def mechanic_to_dict(mechanic: Mechanic) -> Dict[str, Any]:
    """Return a plain dict from a Mechanic."""
    d = asdict(mechanic)
    return {k: list(v) if isinstance(v, tuple) else v for k, v in d.items()}


__all__ = [
    "Mechanic",
    "compile_mechanic",
    "gate",
    "mechanic_to_dict",
    # enums
    "MEDIUMS", "MECHANICS", "LOOP_LENGTHS", "DIFFICULTY_CURVES",
    "NARRATIVE_REGISTERS", "CONTROL_SCHEMES", "SAVE_FORMATS",
    "AGE_RATINGS", "PERFORMANCE_TARGETS", "ROYALTY_MODES", "COMMIT_ASSET",
]