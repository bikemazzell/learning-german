#!/usr/bin/env python3
"""
German Irregular Verb Quiz - Mnemonic-based learning system

Usage:
    python quiz.py              # Interactive mode
    python quiz.py --mode 1     # Praeteritum quiz
    python quiz.py --mode 2     # Perfect quiz
    python quiz.py --mode 3     # Both forms quiz
    python quiz.py --mode 4     # English to German
    python quiz.py --phase 1    # Only Phase 1 verbs
    python quiz.py --mnemonic inka   # Only INKA verbs (mnemonic drill)
    python quiz.py --infinite   # Infinite mode (until Ctrl+C or 'q')
    python quiz.py --no-hints   # Hard mode - hide mnemonic hints
    python quiz.py --stats      # Show statistics
    python quiz.py --reset      # Reset progress
"""

import sys
import json
import random
import re
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

from german_common import (
    Verb, Colors, MNEMONIC_PATTERNS, MNEMONIC_COLORS, parse_markdown,
    VerbProgress, update_progress, get_due_verbs
)


def load_progress(filepath: Path) -> dict[str, VerbProgress]:
    """Load progress data from JSON file."""
    if filepath.exists():
        data = json.loads(filepath.read_text(encoding='utf-8'))
        return {k: VerbProgress(**v) for k, v in data.items()}
    return {}


def save_progress(filepath: Path, progress: dict[str, VerbProgress]):
    """Save progress data to JSON file."""
    data = {k: asdict(v) for k, v in progress.items()}
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def quiz_praeteritum(verb: Verb, show_hint: bool = True) -> tuple[str, str]:
    """Generate praeteritum quiz question."""
    if show_hint:
        color = MNEMONIC_COLORS.get(verb.mnemonic, "")
        hint = f" ({color}{verb.mnemonic.upper()}: {verb.pattern}{Colors.END})"
    else:
        hint = ""
    question = f"What is the Praeteritum of \"{verb.infinitive}\"?{hint}"
    return question, verb.praeteritum


def quiz_perfect(verb: Verb, show_hint: bool = True) -> tuple[str, str]:
    """Generate perfect quiz question."""
    if show_hint:
        color = MNEMONIC_COLORS.get(verb.mnemonic, "")
        hint = f" ({color}{verb.mnemonic.upper()}: {verb.pattern}{Colors.END})"
    else:
        hint = ""
    question = f"What is the Perfect of \"{verb.infinitive}\"?{hint}"
    return question, verb.perfect


def quiz_both(verb: Verb, show_hint: bool = True) -> tuple[str, str]:
    """Generate quiz for both forms."""
    if show_hint:
        color = MNEMONIC_COLORS.get(verb.mnemonic, "")
        hint = f" ({color}{verb.mnemonic.upper()}: {verb.pattern}{Colors.END})"
    else:
        hint = ""
    question = f"What are the Praeteritum and Perfect of \"{verb.infinitive}\"?{hint}\n(Format: praeteritum, perfect)"
    return question, f"{verb.praeteritum}, {verb.perfect}"


def quiz_english_to_german(verb: Verb, show_hint: bool = True) -> tuple[str, str]:
    """Generate English to German infinitive quiz."""
    question = f"What is the German verb for \"{verb.english}\"?"
    return question, verb.infinitive


def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison."""
    return answer.lower().strip().replace("ß", "ss")


def check_answer(user_answer: str, correct_answer: str, mode: int) -> bool:
    """Check if user's answer is correct."""
    user = normalize_answer(user_answer)
    correct = normalize_answer(correct_answer)

    if mode == 3:
        user_parts = re.split(r'[,/\s]+', user)
        correct_parts = re.split(r'[,/\s]+', correct)
        if len(user_parts) >= 2 and len(correct_parts) >= 2:
            return (normalize_answer(user_parts[0]) == normalize_answer(correct_parts[0]) and
                    normalize_answer(user_parts[1]) == normalize_answer(correct_parts[1]))

    return user == correct


def print_stats(verbs: list[Verb], progress: dict[str, VerbProgress]):
    """Print learning statistics."""
    print(f"\n{Colors.BOLD}=== Learning Statistics ==={Colors.END}\n")

    total = len(verbs)
    reviewed = len([v for v in verbs if v.infinitive in progress])
    mastered = len([v for v in verbs if v.infinitive in progress and
                    progress[v.infinitive].correct >= 3 and
                    progress[v.infinitive].ease_factor >= 2.5])

    print(f"Total verbs: {total}")
    print(f"Reviewed: {reviewed} ({100*reviewed//total}%)")
    print(f"Mastered: {mastered} ({100*mastered//total}%)")

    print(f"\n{Colors.BOLD}By Mnemonic:{Colors.END}")
    for mnemonic in MNEMONIC_PATTERNS.keys():
        mnemonic_verbs = [v for v in verbs if v.mnemonic == mnemonic]
        if mnemonic_verbs:
            correct = sum(progress.get(v.infinitive, VerbProgress()).correct for v in mnemonic_verbs)
            incorrect = sum(progress.get(v.infinitive, VerbProgress()).incorrect for v in mnemonic_verbs)
            total_attempts = correct + incorrect
            accuracy = 100 * correct // total_attempts if total_attempts > 0 else 0
            color = MNEMONIC_COLORS.get(mnemonic, "")
            print(f"  {color}{mnemonic.upper():10}{Colors.END} ({MNEMONIC_PATTERNS[mnemonic]:6}): "
                  f"{len(mnemonic_verbs):2} verbs, {accuracy:3}% accuracy")

    print(f"\n{Colors.BOLD}By Phase:{Colors.END}")
    for phase in range(1, 5):
        phase_verbs = [v for v in verbs if v.phase == phase]
        if phase_verbs:
            correct = sum(progress.get(v.infinitive, VerbProgress()).correct for v in phase_verbs)
            incorrect = sum(progress.get(v.infinitive, VerbProgress()).incorrect for v in phase_verbs)
            total_attempts = correct + incorrect
            accuracy = 100 * correct // total_attempts if total_attempts > 0 else 0
            print(f"  Phase {phase}: {len(phase_verbs):2} verbs, {accuracy:3}% accuracy")

    print(f"\n{Colors.BOLD}Verbs needing practice:{Colors.END}")
    weak_verbs = []
    for verb in verbs:
        if verb.infinitive in progress:
            p = progress[verb.infinitive]
            if p.incorrect > 0:
                accuracy = p.correct / (p.correct + p.incorrect)
                weak_verbs.append((verb, accuracy, p.incorrect))

    weak_verbs.sort(key=lambda x: x[1])
    for verb, accuracy, errors in weak_verbs[:5]:
        color = MNEMONIC_COLORS.get(verb.mnemonic, "")
        print(f"  {verb.infinitive:15} ({color}{verb.mnemonic.upper()}{Colors.END}): "
              f"{100*accuracy:.0f}% accuracy, {errors} errors")


def list_verbs_by_mnemonic(verbs: list[Verb]):
    """List all verbs organized by mnemonic pattern."""
    for mnemonic in MNEMONIC_PATTERNS.keys():
        color = MNEMONIC_COLORS.get(mnemonic, "")
        mnemonic_verbs = [v for v in verbs if v.mnemonic == mnemonic]
        print(f"{color}{mnemonic.upper()}{Colors.END} ({MNEMONIC_PATTERNS[mnemonic]}):")
        for v in mnemonic_verbs:
            freq = "★" * v.frequency + "☆" * (3 - v.frequency)
            print(f"  {v.infinitive:15} → {v.praeteritum:12} → {v.perfect:15} ({v.english}) {freq}")
        print()


def show_mnemonic_intro(verbs: list[Verb], mnemonic: str):
    """Show all verbs for a mnemonic group before drilling."""
    color = MNEMONIC_COLORS.get(mnemonic, "")
    pattern = MNEMONIC_PATTERNS.get(mnemonic, "")
    group_verbs = [v for v in verbs if v.mnemonic == mnemonic]

    print(f"\n{Colors.BOLD}{'='*50}{Colors.END}")
    print(f"{Colors.BOLD}Mnemonic drill: {color}{mnemonic.upper()}{Colors.END}{Colors.BOLD} ({pattern}){Colors.END}")
    print(f"{'='*50}{Colors.END}")
    print(f"\nAll {len(group_verbs)} verbs in this group:\n")
    print(f"  {'Infinitive':<16} {'Praeteritum':<14} {'Perfect':<18} English")
    print(f"  {'-'*14:<16} {'-'*12:<14} {'-'*16:<18} {'-'*10}")
    for v in group_verbs:
        freq = "★" * v.frequency + "☆" * (3 - v.frequency)
        print(f"  {v.infinitive:<16} {v.praeteritum:<14} {v.perfect:<18} {v.english}  {freq}")
    print(f"\n{Colors.CYAN}Study the pattern above, then press Enter to start the quiz...{Colors.END}")
    input()


def run_quiz(verbs: list[Verb], progress: dict[str, VerbProgress],
             mode: int, phase: int | None, num_questions: int = 10,
             spaced: bool = True, infinite: bool = False, show_hints: bool = True,
             mnemonic: str | None = None):
    """Run an interactive quiz session."""

    all_verbs = verbs
    if mnemonic:
        all_verbs = [v for v in verbs if v.mnemonic == mnemonic.lower()]
        if not all_verbs:
            print(f"{Colors.RED}No verbs found for mnemonic '{mnemonic.upper()}'.{Colors.END}")
            return
    elif phase:
        all_verbs = [v for v in verbs if v.phase == phase]

    if spaced and not infinite:
        due_verbs = get_due_verbs(all_verbs, progress)
        if not due_verbs:
            print(f"\n{Colors.GREEN}All verbs reviewed! Come back later for spaced repetition.{Colors.END}")
            print("Use --no-spaced to quiz all verbs regardless of schedule.")
            return
        all_verbs = due_verbs

    print(f"\n{Colors.BOLD}=== German Irregular Verb Quiz ==={Colors.END}")
    mode_names = {1: "Praeteritum", 2: "Perfect", 3: "Both Forms", 4: "English→German"}
    print(f"Mode: {mode_names.get(mode, 'Unknown')}")
    if mnemonic:
        color = MNEMONIC_COLORS.get(mnemonic.lower(), "")
        pattern = MNEMONIC_PATTERNS.get(mnemonic.lower(), "")
        print(f"Mnemonic: {color}{mnemonic.upper()}{Colors.END} ({pattern}) — {len(all_verbs)} verbs")
    elif phase:
        print(f"Phase: {phase}")
    if infinite:
        print(f"Questions: ∞ (Ctrl+C to stop)")
    else:
        print(f"Questions: {min(num_questions, len(all_verbs))}")
    if not show_hints:
        print(f"{Colors.YELLOW}Hard mode: Mnemonic hints hidden{Colors.END}")
    print(f"Type 'q' to quit, 'h' for hint\n")
    print("-" * 40)

    correct_count = 0
    total_count = 0
    quit_requested = False

    quiz_funcs = {
        1: quiz_praeteritum,
        2: quiz_perfect,
        3: quiz_both,
        4: quiz_english_to_german
    }

    question_num = 0

    while not quit_requested:
        quiz_verbs = all_verbs.copy()
        random.shuffle(quiz_verbs)

        if not infinite:
            quiz_verbs = quiz_verbs[:num_questions]

        for verb in quiz_verbs:
            question_num += 1
            question, answer = quiz_funcs[mode](verb, show_hints)

            print(f"\n{Colors.BOLD}Q{question_num}.{Colors.END} {question}")

            while True:
                user_input = input("> ").strip()

                if user_input.lower() == 'q':
                    print(f"\n{Colors.YELLOW}Quiz ended.{Colors.END}")
                    quit_requested = True
                    break

                if user_input.lower() == 'h':
                    color = MNEMONIC_COLORS.get(verb.mnemonic, "")
                    print(f"  {Colors.CYAN}Hint:{Colors.END} {color}{verb.mnemonic.upper()}{Colors.END} = {verb.pattern}")
                    print(f"  English: {verb.english}")
                    continue

                total_count += 1
                is_correct = check_answer(user_input, answer, mode)

                if verb.infinitive not in progress:
                    progress[verb.infinitive] = VerbProgress()
                progress[verb.infinitive] = update_progress(progress[verb.infinitive], is_correct)

                if is_correct:
                    correct_count += 1
                    print(f"  {Colors.GREEN}✓ Correct!{Colors.END}")
                else:
                    print(f"  {Colors.RED}✗ Incorrect.{Colors.END} Answer: {Colors.BOLD}{answer}{Colors.END}")
                    color = MNEMONIC_COLORS.get(verb.mnemonic, "")
                    print(f"  Remember: {color}{verb.mnemonic.upper()}{Colors.END} = {verb.pattern}")
                break

            if quit_requested:
                break

        if not infinite:
            break

    if total_count > 0:
        percentage = 100 * correct_count // total_count
        print(f"\n{Colors.BOLD}{'='*40}{Colors.END}")
        print(f"{Colors.BOLD}Final Score: {correct_count}/{total_count} ({percentage}%){Colors.END}")

        if percentage >= 90:
            print(f"{Colors.GREEN}Excellent! 🎉{Colors.END}")
        elif percentage >= 70:
            print(f"{Colors.YELLOW}Good progress! Keep practicing.{Colors.END}")
        else:
            print(f"{Colors.RED}Keep studying! Focus on the mnemonic patterns.{Colors.END}")


def main():
    parser = argparse.ArgumentParser(description="German Irregular Verb Quiz")
    parser.add_argument("--mode", type=int, choices=[1, 2, 3, 4], default=None,
                        help="Quiz mode: 1=Praeteritum, 2=Perfect, 3=Both, 4=English→German")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], default=None,
                        help="Filter by learning phase (1-4)")
    parser.add_argument("--mnemonic", type=str, choices=list(MNEMONIC_PATTERNS.keys()),
                        metavar="MNEMONIC", default=None,
                        help=f"Drill a single mnemonic group: {', '.join(MNEMONIC_PATTERNS.keys())}")
    parser.add_argument("--num", type=int, default=10,
                        help="Number of questions (default: 10)")
    parser.add_argument("--stats", action="store_true",
                        help="Show learning statistics")
    parser.add_argument("--reset", action="store_true",
                        help="Reset all progress")
    parser.add_argument("--no-spaced", action="store_true",
                        help="Disable spaced repetition filtering")
    parser.add_argument("--infinite", action="store_true",
                        help="Infinite mode - keep quizzing until Ctrl+C or 'q'")
    parser.add_argument("--no-hints", action="store_true",
                        help="Hard mode - hide mnemonic hints in questions")
    parser.add_argument("--list", action="store_true",
                        help="List all verbs by mnemonic")

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    md_file = script_dir / "irregular-perfect.md"
    progress_file = script_dir / "progress.json"

    if not md_file.exists():
        print(f"{Colors.RED}Error: {md_file} not found{Colors.END}")
        return 1

    verbs = parse_markdown(md_file)
    print(f"Loaded {len(verbs)} verbs from {md_file.name}")

    if not verbs:
        print(f"{Colors.RED}Error: No verbs found in {md_file.name}{Colors.END}")
        print("Please check that the markdown file is properly formatted.")
        return 1

    progress = load_progress(progress_file)

    if args.reset:
        progress_file.unlink(missing_ok=True)
        print(f"{Colors.GREEN}Progress reset.{Colors.END}")
        sys.exit(0)

    if args.stats:
        print_stats(verbs, progress)
        return 0

    if args.list:
        print(f"\n{Colors.BOLD}All Verbs by Mnemonic:{Colors.END}\n")
        list_verbs_by_mnemonic(verbs)
        return 0

    mode = args.mode
    if mode is None:
        print(f"\n{Colors.BOLD}Select Quiz Mode:{Colors.END}")
        print("  [1] Praeteritum (infinitive → past tense)")
        print("  [2] Perfect (infinitive → perfect participle)")
        print("  [3] Both forms")
        print("  [4] English → German infinitive")
        print("  [s] Show statistics")
        print("  [l] List all verbs")
        print("  [q] Quit")

        while True:
            choice = input("\nMode> ").strip().lower()
            if choice == 'q':
                return 0
            if choice == 's':
                print_stats(verbs, progress)
                continue
            if choice == 'l':
                print(f"\n{Colors.BOLD}All Verbs by Mnemonic:{Colors.END}\n")
                list_verbs_by_mnemonic(verbs)
                continue
            if choice in ['1', '2', '3', '4']:
                mode = int(choice)
                if mode not in [1, 2, 3, 4]:
                    print(f"{Colors.RED}Error: Invalid mode selected{Colors.END}")
                    continue
                break
            print("Invalid choice. Please enter 1-4, s, l, or q.")

    # Determine filter: mnemonic takes priority over phase
    selected_mnemonic = args.mnemonic.lower() if args.mnemonic else None
    phase = args.phase

    if selected_mnemonic is None and phase is None:
        print(f"\n{Colors.BOLD}Filter by:{Colors.END}")
        print("  [p] Phase")
        print("  [m] Mnemonic group (drill one pattern)")
        print("  [a] All verbs")

        while True:
            filter_choice = input("\nFilter> ").strip().lower()
            if filter_choice == 'a':
                break
            if filter_choice == 'p':
                print(f"\n{Colors.BOLD}Select Phase:{Colors.END}")
                print("  [1] Phase 1: Strong Mnemonics (INKA, BARREL, SAUDI)")
                print("  [2] Phase 2: Moderate (USA, LASSO)")
                print("  [3] Phase 3: O-Pattern (POLO)")
                print("  [4] Phase 4: Special (MIRROR, ANACONDA)")
                print("  [a] All phases")
                while True:
                    choice = input("\nPhase> ").strip().lower()
                    if choice == 'a':
                        break
                    if choice in ['1', '2', '3', '4']:
                        phase = int(choice)
                        break
                    print("Invalid choice. Please enter 1-4 or a.")
                break
            if filter_choice == 'm':
                print(f"\n{Colors.BOLD}Select Mnemonic:{Colors.END}")
                for i, (mn, pat) in enumerate(MNEMONIC_PATTERNS.items(), 1):
                    color = MNEMONIC_COLORS.get(mn, "")
                    count = len([v for v in verbs if v.mnemonic == mn])
                    print(f"  [{i}] {color}{mn.upper():<10}{Colors.END} ({pat}) — {count} verbs")
                mn_list = list(MNEMONIC_PATTERNS.keys())
                while True:
                    choice = input("\nMnemonic> ").strip().lower()
                    if choice in [str(i) for i in range(1, len(mn_list) + 1)]:
                        selected_mnemonic = mn_list[int(choice) - 1]
                        break
                    if choice in mn_list:
                        selected_mnemonic = choice
                        break
                    print(f"Invalid choice. Enter 1-{len(mn_list)} or the mnemonic name.")
                break
            print("Invalid choice. Please enter p, m, or a.")

    if selected_mnemonic:
        show_mnemonic_intro(verbs, selected_mnemonic)

    try:
        run_quiz(verbs, progress, mode, phase, args.num,
                 spaced=not args.no_spaced,
                 infinite=args.infinite,
                 show_hints=not args.no_hints,
                 mnemonic=selected_mnemonic)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Quiz interrupted.{Colors.END}")
    finally:
        save_progress(progress_file, progress)
        print(f"\nProgress saved to {progress_file.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
