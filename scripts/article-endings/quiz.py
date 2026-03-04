"""German article gender quiz tool.

Run ``python quiz.py --help`` for usage information.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from words import Word, WORDS, get_words, list_categories


# ---------------------------------------------------------------------------
# ANSI colour codes
# ---------------------------------------------------------------------------

class Colors:
    DER       = "\033[34m"   # blue   — masculine
    DIE       = "\033[35m"   # magenta — feminine
    DAS       = "\033[32m"   # green  — neuter
    CORRECT   = "\033[32m"   # green
    INCORRECT = "\033[31m"   # red
    WARN      = "\033[33m"   # yellow for ⚠ warnings
    BOLD      = "\033[1m"
    END       = "\033[0m"


# ---------------------------------------------------------------------------
# Progress persistence
# ---------------------------------------------------------------------------

PROGRESS_FILE = Path(__file__).parent / "progress.json"


def load_progress() -> dict:
    """Load progress from JSON file.  Returns {} on missing or corrupt file."""
    if not PROGRESS_FILE.exists():
        return {}
    try:
        with open(PROGRESS_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        print(
            f"{Colors.WARN}⚠  Could not read progress file "
            f"({exc}); starting fresh.{Colors.END}"
        )
        return {}


def save_progress(progress: dict) -> None:
    """Persist progress dict to JSON file."""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as fh:
        json.dump(progress, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def color_gender(gender: str) -> str:
    """Return the coloured article string, e.g. '\\033[34mder\\033[0m'."""
    color_map = {
        "der": Colors.DER,
        "die": Colors.DIE,
        "das": Colors.DAS,
    }
    color = color_map.get(gender, "")
    return f"{color}{gender}{Colors.END}"


def parse_answer(raw: str) -> str | None:
    """Parse user input to 'der'/'die'/'das', or None if invalid.

    Accepts:
        '1' -> der, '2' -> die, '3' -> das
        'd'/'der' -> der, 'i'/'die' -> die, 'n'/'das' -> das
    Case-insensitive.
    """
    normalised = raw.strip().lower()
    match normalised:
        case "1" | "d" | "der":
            return "der"
        case "2" | "i" | "die":
            return "die"
        case "3" | "n" | "das":
            return "das"
        case _:
            return None


# ---------------------------------------------------------------------------
# Quiz loop
# ---------------------------------------------------------------------------

def run_quiz(
    words: list[Word],
    progress: dict,
    num: int,
    infinite: bool,
    show_hints: bool,
    desc: str = "All Genders & Categories",
) -> None:
    """Run the interactive quiz loop.

    Parameters
    ----------
    words:
        Word pool to draw from.
    progress:
        Mutable progress dict; updated and saved after each answer.
    num:
        Maximum questions per pass (0 = all words).
    infinite:
        If True, reshuffle and continue after exhausting the pool.
    show_hints:
        If False (--no-hints), hide category suffix hint before answering.
    desc:
        Human-readable description of active filters, shown in the header.
    """
    separator = "────────────────────────────────────────────────────"
    header_line = "===================================================="

    print(f"\n{header_line}")
    print(f"  German Article Quiz — {desc}")
    print(f"{header_line}")
    print("Press Ctrl+C to stop at any time.\n")

    pool = list(words)
    random.shuffle(pool)

    # Determine how many questions to ask per pass.
    questions_per_pass = len(pool) if num == 0 else min(num, len(pool))

    session_correct = 0
    session_total = 0
    queue = pool[:questions_per_pass]
    try:
        while True:
            for word in queue:
                session_total += 1

                # Build hint string.
                if word.category_type == "suffix":
                    hint_text = f"suffix {word.category}"
                else:
                    hint_text = word.category

                # Question prompt.
                hint_part = f" [{hint_text}]" if show_hints else ""
                if infinite:
                    q_label = f"Q{session_total}."
                else:
                    q_label = f"Q{session_total}/{questions_per_pass}."

                print(
                    f"{q_label} What is the article for: "
                    f"{Colors.BOLD}{word.german}{Colors.END} ({word.english})?{hint_part}"
                )

                # Warn about weak patterns regardless of --no-hints.
                if word.weak:
                    print(
                        f"  {Colors.WARN}⚠  Weak pattern — exceptions exist{Colors.END}"
                    )

                print(
                    f"\n  [1] {color_gender('der')}   "
                    f"[2] {color_gender('die')}   "
                    f"[3] {color_gender('das')}\n"
                )

                # Input loop — invalid input does not count as wrong.
                while True:
                    try:
                        raw = input("> ")
                    except EOFError:
                        print()
                        break
                    answer = parse_answer(raw)
                    if answer is not None:
                        break
                    print("Please enter 1, 2, or 3 (or der/die/das).")
                else:
                    # EOFError path — treat as keyboard interrupt.
                    raise KeyboardInterrupt

                # Evaluate answer.
                correct_article = word.gender
                entry = progress.setdefault(
                    word.german, {"correct": 0, "incorrect": 0}
                )

                if answer == correct_article:
                    session_correct += 1
                    entry["correct"] += 1
                    colored = color_gender(correct_article)
                    print(
                        f"\n{Colors.CORRECT}✓ Correct!{Colors.END} "
                        f"{colored} {word.german}"
                    )
                else:
                    entry["incorrect"] += 1
                    colored = color_gender(correct_article)
                    print(
                        f"\n{Colors.INCORRECT}✗ Incorrect!{Colors.END} "
                        f"{colored} {word.german} ({word.english})"
                    )

                # Always show rule.
                print(f"  Rule: {word.rule}")

                # Running total in infinite mode.
                if infinite:
                    print(
                        f"  Session total: "
                        f"{session_correct}/{session_total}"
                    )

                # Save progress; swallow errors so a save failure is non-fatal.
                try:
                    save_progress(progress)
                except OSError as exc:
                    print(
                        f"{Colors.WARN}⚠  Could not save progress: {exc}{Colors.END}"
                    )

                print(f"\n{separator}")

            # End of current queue.
            if not infinite:
                break

            # Infinite mode: reshuffle and continue.
            random.shuffle(pool)
            queue = pool

    except KeyboardInterrupt:
        print()

    # Session summary.
    if session_total > 0:
        pct = int(session_correct / session_total * 100)
        print(f"Results: {session_correct}/{session_total} ({pct}%)")
        if pct >= 90:
            print("Ausgezeichnet! Keep it up.")
        elif pct >= 70:
            print("Good progress! Keep practicing.")
        else:
            print("Keep studying — focus on the rules.")
    else:
        print("No questions answered.")


# ---------------------------------------------------------------------------
# Stats display
# ---------------------------------------------------------------------------

def show_stats(words: list[Word], progress: dict) -> None:
    """Print a detailed statistics overview."""
    if not progress:
        print(
            "No progress yet — start a quiz to see statistics!"
        )
        return

    total_words = len(words)
    reviewed = sum(
        1 for w in words
        if w.german in progress
        and (progress[w.german]["correct"] + progress[w.german]["incorrect"]) > 0
    )
    not_seen = total_words - reviewed

    print("=== German Article Learning Statistics ===\n")
    print(f"Total words available:  {total_words}")
    print(f"Words reviewed:          {reviewed}  ({int(reviewed / total_words * 100)}%)")
    print(f"Words not yet seen:      {not_seen}")

    # By gender.
    print("\nBy gender:")
    for gender in ("der", "die", "das"):
        gender_words = [w for w in words if w.gender == gender]
        g_reviewed = [
            w for w in gender_words
            if w.german in progress
            and (progress[w.german]["correct"] + progress[w.german]["incorrect"]) > 0
        ]
        if g_reviewed:
            g_correct = sum(progress[w.german]["correct"] for w in g_reviewed)
            g_total = sum(
                progress[w.german]["correct"] + progress[w.german]["incorrect"]
                for w in g_reviewed
            )
            g_pct = int(g_correct / g_total * 100) if g_total else 0
            acc_str = f"{g_pct}% accuracy"
        else:
            acc_str = "  -  "

        colored = color_gender(gender)
        print(
            f"  {colored}  {len(gender_words):3d} words | "
            f"{len(g_reviewed):3d} reviewed | "
            f"{acc_str}"
        )

    # By category.
    print("\nBy category (sorted by accuracy, reviewed words only):")

    # Collect all unique categories across the full word list.
    all_cats: dict[str, list[Word]] = {}
    for w in words:
        all_cats.setdefault(w.category, []).append(w)

    cat_stats: list[tuple[str, int, int, int]] = []  # (cat, correct, total, word_count)
    for cat, cat_words in all_cats.items():
        cat_correct = 0
        cat_total = 0
        for w in cat_words:
            if w.german in progress:
                cat_correct += progress[w.german]["correct"]
                cat_total += (
                    progress[w.german]["correct"] + progress[w.german]["incorrect"]
                )
        if cat_total > 0:
            cat_stats.append((cat, cat_correct, cat_total, len(cat_words)))

    # Sort by accuracy ascending (worst first at the bottom, so reverse for printing).
    cat_stats.sort(key=lambda x: x[1] / x[2])

    # Determine column width for category name.
    cat_col = max((len(c) for c, *_ in cat_stats), default=8)

    for i, (cat, correct, total, word_count) in enumerate(cat_stats):
        pct = int(correct / total * 100)
        suffix = "  <- focus here" if i == 0 and len(cat_stats) > 1 else ""
        print(
            f"  {cat:<{cat_col}}  {correct}/{total}  {pct:3d}%{suffix}"
        )

    # Hardest words.
    attempted: list[tuple[Word, int, int]] = []
    for w in words:
        if w.german in progress:
            c = progress[w.german]["correct"]
            inc = progress[w.german]["incorrect"]
            if c + inc >= 1:
                attempted.append((w, c, c + inc))

    if attempted:
        attempted.sort(key=lambda x: x[1] / x[2])
        print("\nHardest words (lowest accuracy, min 1 attempt):")
        for rank, (w, correct, total) in enumerate(attempted[:10], start=1):
            pct = int(correct / total * 100)
            colored = color_gender(w.gender)
            print(
                f"  {rank:2d}. {colored} {w.german:<20s}  "
                f"{correct}/{total}  {pct:3d}%"
            )


# ---------------------------------------------------------------------------
# Word list display
# ---------------------------------------------------------------------------

def show_list(words: list[Word]) -> None:
    """Print all words grouped by gender then category."""
    print("=== Word List ===")

    gender_order = ["der", "die", "das"]
    gender_labels = {
        "der": "der (masculine)",
        "die": "die (feminine)",
        "das": "das (neuter)",
    }

    total_count = len(words)
    all_cats: set[str] = set()

    for gender in gender_order:
        gender_words = [w for w in words if w.gender == gender]
        if not gender_words:
            continue

        label = gender_labels[gender]
        bar = "─" * (50 - len(label) - 4)
        print(f"\n── {label} {bar}")

        # Collect categories in order of first appearance.
        seen_cats: list[str] = []
        cat_map: dict[str, list[Word]] = {}
        for w in gender_words:
            if w.category not in cat_map:
                seen_cats.append(w.category)
                cat_map[w.category] = []
            cat_map[w.category].append(w)
            all_cats.add(w.category)

        for cat in seen_cats:
            cat_words = cat_map[cat]
            count = len(cat_words)
            samples = ", ".join(
                f"{w.german} ({w.english})" for w in cat_words[:6]
            )
            ellipsis = "..." if count > 6 else ""
            print(f"  {cat} ({count} words):")
            print(f"    {samples}{ellipsis}")

    print(f"\nTotal: {total_count} words across {len(all_cats)} categories")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construct and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="quiz.py",
        description="German Article Endings Quiz",
    )
    parser.add_argument(
        "--gender",
        choices=["m", "f", "n", "all"],
        default="all",
        metavar="{m,f,n,all}",
        help="Filter by gender: m=masculine, f=feminine, n=neuter [default: all]",
    )
    parser.add_argument(
        "--type",
        choices=["suffix", "semantic", "all"],
        default="all",
        metavar="{suffix,semantic,all}",
        help="Filter by category type [default: all]",
    )
    parser.add_argument(
        "--category",
        default=None,
        metavar="CATEGORY",
        help=(
            "Focus on a specific category, e.g. \"heit\", \"weather\" "
            "(leading dash optional)"
        ),
    )
    parser.add_argument(
        "--num",
        type=int,
        default=10,
        metavar="N",
        help="Number of questions [default: 10; use 0 for all]",
    )
    parser.add_argument(
        "--infinite",
        action="store_true",
        help="Keep quizzing until Ctrl+C",
    )
    parser.add_argument(
        "--no-hints",
        action="store_true",
        dest="no_hints",
        help="Hard mode: hide category hints before answering",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show learning statistics and exit",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all words by category and exit",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset all progress and exit",
    )
    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Map gender flag to actual article string.
    gender_map = {"m": "der", "f": "die", "n": "das", "all": None}
    gender = gender_map[args.gender]

    # Map type flag.
    type_map = {"suffix": "suffix", "semantic": "semantic", "all": None}
    cat_type = type_map[args.type]

    # Normalise category: strip leading dash and do case-insensitive substring match.
    category: str | None = None
    if args.category:
        cat_query = args.category.lstrip("-")
        all_cats = [
            c
            for gender_cats in list_categories().values()
            for c in gender_cats
        ]
        # Prefer exact match first, then substring match
        q = cat_query.lower()
        exact = [c for c in all_cats if c.lower().lstrip("-") == q]
        matches = exact if exact else [c for c in all_cats if q in c.lower().lstrip("-")]
        if not matches:
            print(
                f"Unknown category '{args.category}'. "
                "Use --list to see available categories."
            )
            sys.exit(1)
        category = matches[0]

    # --reset: delete progress file and exit.
    if args.reset:
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
            print("Progress reset.")
        else:
            print("No progress file found.")
        return

    # Load filtered word list (used for --stats, --list, quiz).
    filtered = get_words(gender=gender, category_type=cat_type, category=category)

    # --stats: always show over the complete word list.
    if args.stats:
        progress = load_progress()
        show_stats(WORDS, progress)
        return

    # --list: show filtered word list.
    if args.list:
        show_list(filtered)
        return

    if not filtered:
        print(
            "No words found for the given filters. "
            "Use --list to see available categories."
        )
        sys.exit(1)

    progress = load_progress()

    # Build description string for the quiz header.
    parts: list[str] = []
    if args.gender != "all":
        parts.append({"m": "Masculine", "f": "Feminine", "n": "Neuter"}[args.gender])
    if args.type != "all":
        parts.append(args.type.capitalize())
    if category:
        parts.append(f"'{category}'")
    desc = " · ".join(parts) if parts else "All Genders & Categories"

    run_quiz(
        words=filtered,
        progress=progress,
        num=args.num,
        infinite=args.infinite,
        show_hints=not args.no_hints,
        desc=desc,
    )


if __name__ == "__main__":
    main()
