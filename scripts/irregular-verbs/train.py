#!/usr/bin/env python3
"""
German Irregular Verb Training - Memorization system

Usage:
    python train.py --phase 1           # Train Phase 1 verbs
    python train.py --phase all         # Train all phases
    python train.py --phase 1 --num 10  # Train 10 verbs from Phase 1
    python train.py --review            # Train only verbs needing review
    python train.py --infinite          # Train until Ctrl+C
    python train.py --stats             # Show training statistics
    python train.py --reset             # Reset all training progress
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from german_common import (
    Verb, Colors, MNEMONIC_PATTERNS, MNEMONIC_COLORS, parse_markdown
)


@dataclass
class TrainingProgress:
    """Track training progress for a single verb."""
    exposures: int = 0
    correct: int = 0
    incorrect: int = 0
    last_seen: str = ""
    status: str = "learning"


def load_training_progress(filepath: Path) -> dict[str, TrainingProgress]:
    """Load training progress from JSON file."""
    if filepath.exists():
        data = json.loads(filepath.read_text(encoding='utf-8'))
        return {k: TrainingProgress(**v) for k, v in data.items()}
    return {}


def save_training_progress(filepath: Path, progress: dict[str, TrainingProgress]):
    """Save training progress to JSON file."""
    data = {k: asdict(v) for k, v in progress.items()}
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def update_training_progress(progress: TrainingProgress, known: bool) -> TrainingProgress:
    """Update training progress based on user's self-assessment."""
    progress.exposures += 1
    progress.last_seen = datetime.now().isoformat()

    if known:
        progress.correct += 1
    else:
        progress.incorrect += 1

    if (progress.exposures >= 5 and
        progress.correct >= 3 and
        (progress.correct / progress.exposures) >= 0.8):
        progress.status = "mastered"
    else:
        progress.status = "learning"

    return progress


def get_verbs_for_training(verbs: list[Verb], training_progress: dict[str, TrainingProgress],
                          phase: int | str, review_only: bool) -> list[Verb]:
    """Get verbs for training session based on filters and priority."""
    if phase == "all":
        filtered_verbs = verbs
    else:
        filtered_verbs = [v for v in verbs if v.phase == phase]

    if review_only:
        review_verbs = []
        for verb in filtered_verbs:
            if verb.infinitive not in training_progress:
                continue
            p = training_progress[verb.infinitive]
            if p.status == "learning":
                accuracy = p.correct / p.exposures if p.exposures > 0 else 0
                if accuracy < 0.7 or p.incorrect > 0:
                    review_verbs.append(verb)
        filtered_verbs = review_verbs

    def sort_key(verb):
        if verb.infinitive not in training_progress:
            return (0, 0)
        p = training_progress[verb.infinitive]
        if p.status == "learning" and (p.correct / p.exposures < 0.7 if p.exposures > 0 else False):
            return (0, p.exposures)
        return (1, p.exposures)

    filtered_verbs.sort(key=sort_key)
    return filtered_verbs


def display_verb(verb: Verb, num: int, total: int):
    """Display a single verb for study."""
    color = MNEMONIC_COLORS.get(verb.mnemonic, "")
    print(f"\n{Colors.BOLD}{'━' * 50}{Colors.END}")
    print(f"{Colors.BOLD}Verb #{num} of {total}{Colors.END}")
    print(f"{Colors.BOLD}{color}[Phase {verb.phase}] {verb.mnemonic.upper()}{Colors.END}")
    print(f"{Colors.BOLD}{'━' * 50}{Colors.END}\n")
    print(f"{Colors.CYAN}{verb.infinitive}{Colors.END}")


def display_answer(verb: Verb):
    """Display the answer after user presses Enter."""
    color = MNEMONIC_COLORS.get(verb.mnemonic, "")
    print(f"\n{Colors.BOLD}{'━' * 50}{Colors.END}")
    print(f"{Colors.BOLD}REVEALED{Colors.END}")
    print(f"{Colors.BOLD}{'━' * 50}{Colors.END}\n")
    print(f"{Colors.GREEN}German:{Colors.END}  {verb.infinitive}")
    print(f"{Colors.GREEN}English:{Colors.END} {verb.english}")
    print(f"{Colors.YELLOW}Mnemonic:{Colors.END} {color}{verb.mnemonic.upper()}{Colors.END} ({verb.pattern})")
    print(f"{Colors.BLUE}Forms:{Colors.END}   {verb.praeteritum} | {verb.perfect}")


def print_training_stats(verbs: list[Verb], training_progress: dict[str, TrainingProgress]):
    """Print training statistics."""
    print(f"\n{Colors.BOLD}{'=' * 50}{Colors.END}")
    print(f"{Colors.BOLD}Training Statistics{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 50}{Colors.END}\n")

    total = len(verbs)
    studied = len([v for v in verbs if v.infinitive in training_progress])
    mastered = len([v for v in verbs if v.infinitive in training_progress and
                   training_progress[v.infinitive].status == "mastered"])

    print(f"Total verbs: {total}")
    print(f"Studied: {studied} ({100*studied//total}%)")
    print(f"Mastered: {mastered} ({100*mastered//total}%)\n")

    print(f"{Colors.BOLD}By Phase:{Colors.END}")
    for phase in range(1, 5):
        phase_verbs = [v for v in verbs if v.phase == phase]
        if phase_verbs:
            studied_count = sum(1 for v in phase_verbs if v.infinitive in training_progress)
            mastered_count = sum(1 for v in phase_verbs
                               if v.infinitive in training_progress and
                               training_progress[v.infinitive].status == "mastered")
            print(f"  Phase {phase}: {studied_count}/{len(phase_verbs)} ({100*studied_count//len(phase_verbs)}%) studied, "
                  f"{mastered_count}/{len(phase_verbs)} ({100*mastered_count//len(phase_verbs)}%) mastered")

    print(f"\n{Colors.BOLD}By Mnemonic:{Colors.END}")
    for mnemonic in MNEMONIC_PATTERNS.keys():
        mnemonic_verbs = [v for v in verbs if v.mnemonic == mnemonic]
        if mnemonic_verbs:
            studied_count = sum(1 for v in mnemonic_verbs if v.infinitive in training_progress)
            mastered_count = sum(1 for v in mnemonic_verbs
                               if v.infinitive in training_progress and
                               training_progress[v.infinitive].status == "mastered")
            color = MNEMONIC_COLORS.get(mnemonic, "")
            print(f"  {color}{mnemonic.upper():10}{Colors.END}: {studied_count}/{len(mnemonic_verbs)} studied, "
                  f"{mastered_count}/{len(mnemonic_verbs)} mastered")

    review_verbs = []
    for verb in verbs:
        if verb.infinitive in training_progress:
            p = training_progress[verb.infinitive]
            if p.status == "learning":
                accuracy = p.correct / p.exposures if p.exposures > 0 else 0
                if accuracy < 0.7 or p.incorrect > 0:
                    review_verbs.append((verb, accuracy))

    if review_verbs:
        review_verbs.sort(key=lambda x: x[1])
        print(f"\n{Colors.BOLD}Verbs Needing Review:{Colors.END}")
        for verb, accuracy in review_verbs[:10]:
            p = training_progress[verb.infinitive]
            print(f"  {verb.infinitive:15} ({p.exposures} exposures, {100*accuracy:.0f}% accuracy)")


def run_training_session(verbs: list[Verb], training_progress: dict[str, TrainingProgress],
                        num_verbs: int, infinite: bool, progress_file: Path):
    """Run an interactive training session."""
    import random

    num_verbs = min(num_verbs, len(verbs))
    training_verbs = verbs[:num_verbs]

    print(f"\n{Colors.BOLD}{'=' * 50}{Colors.END}")
    print(f"{Colors.BOLD}German Verb Training Session{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 50}{Colors.END}")
    print(f"Verbs: {len(training_verbs)}")
    if infinite:
        print(f"Mode: Infinite (Ctrl+C to stop)")
    else:
        print(f"Mode: Session ({len(training_verbs)} verbs)")
    print(f"\n{Colors.CYAN}Instructions:{Colors.END}")
    print(f"  1. Study the German verb")
    print(f"  2. Press Enter to reveal the answer")
    print(f"  3. Mark as [k]nown or [d]idn't know")
    print(f"  4. Press [q] to quit at any time\n")

    session_start = True

    while session_start:
        for i, verb in enumerate(training_verbs, 1):
            display_verb(verb, i, len(training_verbs))

            input()
            display_answer(verb)

            while True:
                try:
                    user_input = input(f"\n{Colors.BOLD}Did you know it?{Colors.END} [k/d/q] > ").strip().lower()

                    if user_input == 'q':
                        print(f"\n{Colors.YELLOW}Training session ended.{Colors.END}")
                        return
                    elif user_input == 'k':
                        if verb.infinitive not in training_progress:
                            training_progress[verb.infinitive] = TrainingProgress()
                        training_progress[verb.infinitive] = update_training_progress(
                            training_progress[verb.infinitive], known=True)
                        print(f"  {Colors.GREEN}✓ Marked as known{Colors.END}")
                        break
                    elif user_input == 'd':
                        if verb.infinitive not in training_progress:
                            training_progress[verb.infinitive] = TrainingProgress()
                        training_progress[verb.infinitive] = update_training_progress(
                            training_progress[verb.infinitive], known=False)
                        print(f"  {Colors.RED}✗ Marked as unknown{Colors.END}")
                        break
                    else:
                        print(f"  Please enter [k]nown, [d]idn't know, or [q]uit")

                except EOFError:
                    print(f"\n{Colors.YELLOW}Training session ended.{Colors.END}")
                    return

            save_training_progress(progress_file, training_progress)

        if not infinite:
            break

        random.shuffle(training_verbs)
        print(f"\n{Colors.CYAN}Starting new round...{Colors.END}\n")


def main():
    parser = argparse.ArgumentParser(description="German Irregular Verb Training")
    parser.add_argument("--phase", type=str, choices=["1", "2", "3", "4", "all"], default="1",
                        help="Phase to train (1-4, or all)")
    parser.add_argument("--num", type=int, default=None,
                        help="Number of verbs per session (default: all in phase)")
    parser.add_argument("--stats", action="store_true",
                        help="Show training statistics")
    parser.add_argument("--reset", action="store_true",
                        help="Reset all training progress")
    parser.add_argument("--review", action="store_true",
                        help="Train only verbs needing review")
    parser.add_argument("--infinite", action="store_true",
                        help="Infinite mode - keep training until Ctrl+C")

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    md_file = script_dir / "irregular-perfect.md"
    progress_file = script_dir / "training_progress.json"

    if not md_file.exists():
        print(f"{Colors.RED}Error: {md_file} not found{Colors.END}")
        return 1

    verbs = parse_markdown(md_file)
    if not verbs:
        print(f"{Colors.RED}Error: No verbs found in {md_file.name}{Colors.END}")
        print("Please check that the markdown file is properly formatted.")
        return 1

    print(f"Loaded {len(verbs)} verbs from {md_file.name}")

    training_progress = load_training_progress(progress_file)

    if args.reset:
        progress_file.unlink(missing_ok=True)
        print(f"{Colors.GREEN}Training progress reset.{Colors.END}")
        return 0

    if args.stats:
        print_training_stats(verbs, training_progress)
        return 0

    phase = args.phase
    if phase == "all":
        phase_filter = "all"
    else:
        phase_filter = int(phase)

    training_verbs = get_verbs_for_training(verbs, training_progress, phase_filter, args.review)

    if not training_verbs:
        print(f"\n{Colors.YELLOW}No verbs match your criteria.{Colors.END}")
        if args.review:
            print("Try training without the --review flag to learn new verbs.")
        return 0

    if args.num:
        num_verbs = min(args.num, len(training_verbs))
        training_verbs = training_verbs[:num_verbs]
    else:
        num_verbs = len(training_verbs)

    try:
        run_training_session(training_verbs, training_progress, num_verbs, args.infinite, progress_file)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Training session interrupted. Progress saved.{Colors.END}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
