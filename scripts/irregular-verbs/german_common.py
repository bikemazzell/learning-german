#!/usr/bin/env python3
"""Shared utilities for German irregular verb learning system."""

import json
import random
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path


# ANSI colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


@dataclass
class Verb:
    infinitive: str
    praeteritum: str
    perfect: str
    english: str
    mnemonic: str
    pattern: str
    frequency: int
    phase: int
    semantic_group: str = ""
    has_ge_prefix: bool = True


@dataclass
class VerbProgress:
    correct: int = 0
    incorrect: int = 0
    last_reviewed: Optional[str] = None
    next_review: Optional[str] = None
    ease_factor: float = 2.5
    interval: int = 1


MNEMONIC_PATTERNS = {
    "inka": "→i/ie, →a",
    "barrel": "→a, →e",
    "saudi": "→a, →u",
    "usa": "→u, →a",
    "lasso": "→a, →o",
    "polo": "→o, →o",
    "mirror": "ei↔ie/i",
    "anaconda": "mixed"
}


MNEMONIC_COLORS = {
    "inka": Colors.RED,
    "barrel": Colors.GREEN,
    "saudi": Colors.YELLOW,
    "usa": Colors.BLUE,
    "lasso": Colors.MAGENTA,
    "polo": Colors.CYAN,
    "mirror": Colors.BLUE,
    "anaconda": Colors.MAGENTA
}


def parse_frequency(freq_str: str) -> int:
    """Convert star rating to number."""
    if "★★★" in freq_str:
        return 3
    elif "★★☆" in freq_str:
        return 2
    return 1


def parse_markdown(filepath: Path) -> list[Verb]:
    """Parse the irregular-perfect.md file and extract verbs."""
    verbs = []
    current_mnemonic = ""
    current_phase = 0
    current_semantic = ""

    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    for line in lines:
        if line.startswith("## PHASE"):
            match = re.search(r'PHASE (\d)', line)
            if match:
                current_phase = int(match.group(1))

        if line.startswith("### "):
            for mnemonic in MNEMONIC_PATTERNS.keys():
                if mnemonic.upper() in line.upper():
                    current_mnemonic = mnemonic
                    break

        if line.startswith("**") and not line.startswith("**Frequency"):
            match = re.match(r'\*\*([^*]+)\*\*', line)
            if match:
                current_semantic = match.group(1).strip()

        if line.startswith("| ") and not line.startswith("| Verb") and not line.startswith("|--"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 5:
                verb_name = parts[0]
                praeteritum = parts[1]
                perfect = parts[2]
                english = parts[3]
                freq_str = parts[4] if len(parts) > 4 else "★☆☆"

                has_ge = perfect.startswith("ge") or perfect.startswith("Ge")

                verb = Verb(
                    infinitive=verb_name,
                    praeteritum=praeteritum,
                    perfect=perfect,
                    english=english,
                    mnemonic=current_mnemonic,
                    pattern=MNEMONIC_PATTERNS.get(current_mnemonic, ""),
                    frequency=parse_frequency(freq_str),
                    phase=current_phase,
                    semantic_group=current_semantic,
                    has_ge_prefix=has_ge
                )
                verbs.append(verb)

    return verbs


def update_progress(progress: VerbProgress, correct: bool) -> VerbProgress:
    """Update progress using SM-2 spaced repetition algorithm."""
    now = datetime.now()

    if correct:
        progress.correct += 1
        if progress.interval == 1:
            progress.interval = 6
        else:
            progress.interval = int(progress.interval * progress.ease_factor)
        progress.ease_factor = max(1.3, progress.ease_factor + 0.1)
    else:
        progress.incorrect += 1
        progress.interval = 1
        progress.ease_factor = max(1.3, progress.ease_factor - 0.2)

    progress.last_reviewed = now.isoformat()
    progress.next_review = (now + timedelta(days=progress.interval)).isoformat()

    return progress


def get_due_verbs(verbs: list[Verb], progress: dict[str, VerbProgress]) -> list[Verb]:
    """Get verbs that are due for review based on spaced repetition."""
    now = datetime.now()
    due = []

    for verb in verbs:
        if verb.infinitive not in progress:
            due.append(verb)
        else:
            p = progress[verb.infinitive]
            if p.next_review:
                next_review = datetime.fromisoformat(p.next_review)
                if now >= next_review:
                    due.append(verb)
            else:
                due.append(verb)

    return due
