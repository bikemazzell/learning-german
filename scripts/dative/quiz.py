#!/usr/bin/env python3
"""
German Dative Verb Quiz

Usage:
    python quiz.py              # Interactive mode selection
    python quiz.py --mode de    # German → English
    python quiz.py --mode en    # English → German
    python quiz.py --mode random  # Mixed DE/EN
    python quiz.py --mode dative  # Fill in the dative article (dem/der/den)
    python quiz.py --num 20     # 20 questions
    python quiz.py --infinite   # Keep quizzing until Ctrl+C or 'q'
    python quiz.py --no-hints   # Hard mode: hide hints
    python quiz.py --stats      # Show statistics
    python quiz.py --list       # List all verbs
    python quiz.py --reset      # Reset progress
"""

import sys
import json
import random
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict


# ---------------------------------------------------------------------------
# ANSI colour codes
# ---------------------------------------------------------------------------

class Colors:
    GREEN  = "\033[32m"
    RED    = "\033[31m"
    YELLOW = "\033[33m"
    CYAN   = "\033[36m"
    BLUE   = "\033[34m"
    BOLD   = "\033[1m"
    END    = "\033[0m"


# ---------------------------------------------------------------------------
# Verb data
# ---------------------------------------------------------------------------

@dataclass
class Verb:
    german: str
    english: str
    memory: str
    # Dative-case example: sentence with ___ placeholder, correct article,
    # the noun as it appears in the sentence, and its base (nominative) article.
    example: str       # "Dracula sagt ___ Arzt den Termin ab."
    article: str       # correct dative article: dem / der / den
    noun: str          # noun as used in the sentence, e.g. "Arzt"
    noun_base: str     # base article + noun, e.g. "der Arzt"


# Dative article rules (for explanations):
#   der  → dem     (masculine)
#   die  → der     (feminine)
#   das  → dem     (neuter)
#   pl.  → den     (plural)

VERBS = [
    Verb("absagen",            "to cancel",
         "Dracula cancels your appointment.",
         "Dracula sagt ___ Arzt den Termin ab.",
         "dem", "Arzt", "der Arzt"),

    Verb("antworten",          "to answer",
         "The diplomat just doesn't answer.",
         "Der Diplomat antwortet ___ Chef nicht.",
         "dem", "Chef", "der Chef"),

    Verb("begegnen",           "to encounter",
         "I have encountered Donald Duck.",
         "Ich bin ___ Donald Duck begegnet.",
         "dem", "Donald Duck", "der Donald Duck"),

    Verb("danken",             "to thank",
         "I thank Dracula for my eternal life.",
         "Ich danke ___ Dracula für alles.",
         "dem", "Dracula", "der Dracula"),

    Verb("drohen",             "to threaten",
         "The director threatens with dismissal.",
         "Der Direktor droht ___ Mitarbeiterin.",
         "der", "Mitarbeiterin", "die Mitarbeiterin"),

    Verb("einfallen",          "to have an idea",
         "Dracula has a dumb idea.",
         "Nichts fällt ___ Studentin ein.",
         "der", "Studentin", "die Studentin"),

    Verb("entgegenkommen",     "to approach",
         "A Dino is approaching me.",
         "Ein Dino kommt ___ Mann entgegen.",
         "dem", "Mann", "der Mann"),

    Verb("fehlen",             "to miss",
         "Dracula is missing two teeth.",
         "Du fehlst ___ Mutter sehr.",
         "der", "Mutter", "die Mutter"),

    Verb("folgen",             "to follow",
         "The dachshund follows the badger.",
         "Der Dackel folgt ___ Dachs.",
         "dem", "Dachs", "der Dachs"),

    Verb("gefallen",           "to appeal",
         "The steamroller appeals to Donald.",
         "Das Kleid gefällt ___ Frau.",
         "der", "Frau", "die Frau"),

    Verb("gehen",              "to be (e.g. fine)",
         "The dictator is fine.",
         "Es geht ___ Diktator gut.",
         "dem", "Diktator", "der Diktator"),

    Verb("gehören",            "to belong",
         "The tiara belongs to Lady Diana.",
         "Die Krone gehört ___ Königin.",
         "der", "Königin", "die Königin"),

    Verb("gelingen",           "to accomplish",
         "The design was accomplished.",
         "Das Design gelingt ___ Designer.",
         "dem", "Designer", "der Designer"),

    Verb("genügen",            "to suffice",
         "The drugs didn't suffice the thieve.",
         "Das Geld genügt ___ Dieb nicht.",
         "dem", "Dieb", "der Dieb"),

    Verb("glauben",            "to believe",
         "The detective doesn't believe the thieve.",
         "Der Detektiv glaubt ___ Zeugin nicht.",
         "der", "Zeugin", "die Zeugin"),

    Verb("gratulieren",        "to congratulate",
         "The director congratulated the diva.",
         "Der Direktor gratuliert ___ Diva.",
         "der", "Diva", "die Diva"),

    Verb("gut tun",            "to do good",
         "Diarrhea doesn't do Dracula good.",
         "Sport tut ___ Körper gut.",
         "dem", "Körper", "der Körper"),

    Verb("helfen",             "to help",
         "The deodorant helped the Danish dandy.",
         "Das Deodorant hilft ___ Dandy.",
         "dem", "Dandy", "der Dandy"),

    Verb("kalt/warm sein",     "to be cold/warm",
         "The dame was cold.",
         "Es ist ___ Dame kalt.",
         "der", "Dame", "die Dame"),

    Verb("leid tun",           "to be sorry",
         "The despot was sorry.",
         "Es tut ___ Despoten leid.",
         "dem", "Despoten", "der Despot"),

    Verb("sich nähern",        "to approach",
         "The thief approaches the depot.",
         "Der Dieb nähert sich ___ Depot.",
         "dem", "Depot", "das Depot"),

    Verb("nachlaufen",         "to run after",
         "The dog runs after the dandy.",
         "Der Hund läuft ___ Dandy nach.",
         "dem", "Dandy", "der Dandy"),

    Verb("nützen",             "to avail",
         "The dynamite will avail dracula nothing.",
         "Das nützt ___ Dracula nichts.",
         "dem", "Dracula", "der Dracula"),

    Verb("passen",             "to suit/fit",
         "The diadem suited Diana perfectly.",
         "Das Diadem passt ___ Diana perfekt.",
         "der", "Diana", "die Diana"),

    Verb("passieren",          "to happen",
         "A disaster happened to the DJ.",
         "Eine Katastrophe passiert ___ DJ.",
         "dem", "DJ", "der DJ"),

    Verb("raten",              "to recommend",
         "The diplomat recommends full disclosure of all documents.",
         "Der Diplomat rät ___ Minister.",
         "dem", "Minister", "der Minister"),

    Verb("schaden",            "to do harm",
         "Drama doesn't do a diamond any harm.",
         "Das schadet ___ Gesundheit.",
         "der", "Gesundheit", "die Gesundheit"),

    Verb("schmecken",          "to taste",
         "Drugs just don't taste good.",
         "Das schmeckt ___ Kind gut.",
         "dem", "Kind", "das Kind"),

    Verb("stehen",             "to suit (e.g. clothing)",
         "The designer suit suits the big Danish man.",
         "Das Kleid steht ___ Frau gut.",
         "der", "Frau", "die Frau"),

    Verb("vertrauen",          "to trust",
         "I don't trust my dealer.",
         "Ich vertraue ___ Dealer nicht.",
         "dem", "Dealer", "der Dealer"),

    Verb("verzeihen/vergeben", "to forgive",
         "The docent forgives her ignorance.",
         "Der Dozent vergibt ___ Studentin.",
         "der", "Studentin", "die Studentin"),

    Verb("weh tun",            "to hurt",
         "The dragon is hurting the dodo.",
         "Der Drache tut ___ Dodo weh.",
         "dem", "Dodo", "der Dodo"),

    Verb("widersprechen",      "to contradict",
         "Never contradict your dominatrix.",
         "Widersprich niemals ___ Dominatrix!",
         "der", "Dominatrix", "die Dominatrix"),

    Verb("zuhören",            "to listen",
         "The dog listens to the diva.",
         "Der Hund hört ___ Diva zu.",
         "der", "Diva", "die Diva"),

    Verb("zusehen",            "to watch",
         "I could watch the dolphins forever.",
         "Ich könnte ___ Delfinen ewig zusehen.",
         "den", "Delfinen", "die Delfine (pl.)"),

    Verb("zustimmen",          "to agree",
         "The delegation agreed to the deal.",
         "Die Delegation stimmt ___ Vorschlag zu.",
         "dem", "Vorschlag", "der Vorschlag"),
]


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

@dataclass
class VerbProgress:
    correct: int = 0
    incorrect: int = 0
    dative_correct: int = 0
    dative_incorrect: int = 0


def load_progress(filepath: Path) -> dict[str, VerbProgress]:
    if filepath.exists():
        data = json.loads(filepath.read_text(encoding="utf-8"))
        return {k: VerbProgress(**v) for k, v in data.items()}
    return {}


def save_progress(filepath: Path, progress: dict[str, VerbProgress]) -> None:
    data = {k: asdict(v) for k, v in progress.items()}
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Answer checking — translation modes
# ---------------------------------------------------------------------------

def _normalize(s: str) -> str:
    return s.lower().strip()


def check_english(user: str, verb: Verb) -> bool:
    user_n = _normalize(user).removeprefix("to").strip()
    targets = {_normalize(v).removeprefix("to").strip() for v in verb.english.split("/")}
    return user_n in targets


def check_german(user: str, verb: Verb) -> bool:
    user_n = _normalize(user)
    targets = {_normalize(v) for v in verb.german.split("/")}
    return user_n in targets


# ---------------------------------------------------------------------------
# Answer checking — dative article mode
# ---------------------------------------------------------------------------

_ARTICLE_ALIASES: dict[str, str] = {
    "1": "dem", "2": "der", "3": "den",
    "dem": "dem", "der": "der", "den": "den",
}


def _dative_rule(noun_base: str) -> str:
    """Return a short explanation of the dative rule for this noun."""
    art = noun_base.split()[0].lower()
    rules = {
        "der": f"{Colors.BLUE}der{Colors.END} (m.) → dative = {Colors.BOLD}dem{Colors.END}",
        "die": f"{Colors.YELLOW}die{Colors.END} (f.) → dative = {Colors.BOLD}der{Colors.END}",
        "das": f"{Colors.GREEN}das{Colors.END} (n.) → dative = {Colors.BOLD}dem{Colors.END}",
    }
    if art in rules:
        return rules[art]
    # plural
    return f"plural → dative = {Colors.BOLD}den{Colors.END}"


def parse_article(raw: str) -> str | None:
    return _ARTICLE_ALIASES.get(raw.strip().lower())


# ---------------------------------------------------------------------------
# Quiz loop — translation (DE↔EN)
# ---------------------------------------------------------------------------

def run_translation_quiz(
    verbs: list[Verb],
    progress: dict[str, VerbProgress],
    mode: str,
    num: int,
    infinite: bool,
    show_hints: bool,
) -> None:
    sep = "────────────────────────────────────────"
    mode_label = {
        "de": "German → English",
        "en": "English → German",
        "random": "Random (mixed)",
    }[mode]

    questions = "∞" if infinite else str(min(num, len(verbs)))
    print(f"\n{Colors.BOLD}=== Dative Verb Quiz — {mode_label} ==={Colors.END}")
    print(f"Questions: {questions}  |  Type 'q' to quit, 'h' for memory hint\n")
    print(sep)

    correct_count = 0
    total_count = 0
    quit_requested = False
    pool = verbs.copy()

    while not quit_requested:
        random.shuffle(pool)
        batch = pool if infinite else pool[:num]

        for verb in batch:
            direction = mode if mode != "random" else random.choice(["de", "en"])

            if direction == "de":
                q_text = f"What does {Colors.BOLD}{verb.german}{Colors.END} mean?"
                correct_answer = verb.english
                check_fn = check_english
            else:
                q_text = f"German verb for \"{Colors.BOLD}{verb.english}{Colors.END}\"?"
                correct_answer = verb.german
                check_fn = check_german

            print(f"\n{q_text}")

            while True:
                try:
                    user_input = input("> ").strip()
                except EOFError:
                    quit_requested = True
                    break

                if user_input.lower() == "q":
                    quit_requested = True
                    break

                if user_input.lower() == "h":
                    print(f"  {Colors.CYAN}Memory: {verb.memory}{Colors.END}")
                    continue

                total_count += 1
                entry = progress.setdefault(verb.german, VerbProgress())

                if check_fn(user_input, verb):
                    correct_count += 1
                    entry.correct += 1
                    print(f"  {Colors.GREEN}✓ Correct!{Colors.END}  →  {correct_answer}")
                else:
                    entry.incorrect += 1
                    print(f"  {Colors.RED}✗ Incorrect.{Colors.END}  Answer: {Colors.BOLD}{correct_answer}{Colors.END}")

                if show_hints:
                    print(f"  {Colors.CYAN}Memory: {verb.memory}{Colors.END}")

                print(sep)
                break

            if quit_requested:
                break

        if not infinite:
            break

    _print_score(correct_count, total_count)


# ---------------------------------------------------------------------------
# Quiz loop — dative article
# ---------------------------------------------------------------------------

def run_dative_quiz(
    verbs: list[Verb],
    progress: dict[str, VerbProgress],
    num: int,
    infinite: bool,
    show_hints: bool,
) -> None:
    sep = "────────────────────────────────────────"
    print(f"\n{Colors.BOLD}=== Dative Article Quiz ==={Colors.END}")
    print(f"Fill in the correct dative article: dem / der / den")
    questions = "∞" if infinite else str(min(num, len(verbs)))
    print(f"Questions: {questions}  |  Type 'q' to quit\n")
    print(sep)

    correct_count = 0
    total_count = 0
    quit_requested = False
    pool = verbs.copy()

    while not quit_requested:
        random.shuffle(pool)
        batch = pool if infinite else pool[:num]

        for verb in batch:
            # Show sentence with blank
            highlighted = verb.example.replace(
                "___",
                f"{Colors.BOLD}___{Colors.END}"
            )
            print(f"\n{highlighted}")
            if show_hints:
                print(f"  ({verb.noun_base})")
            print(f"\n  [1] dem   [2] der   [3] den\n")

            while True:
                try:
                    raw = input("> ").strip()
                except EOFError:
                    quit_requested = True
                    break

                if raw.lower() == "q":
                    quit_requested = True
                    break

                answer = parse_article(raw)
                if answer is None:
                    print("  Enter dem, der, or den  (or 1 / 2 / 3).")
                    continue

                total_count += 1
                entry = progress.setdefault(verb.german, VerbProgress())

                filled = verb.example.replace("___", f"{Colors.BOLD}{verb.article}{Colors.END}")
                rule = _dative_rule(verb.noun_base)

                if answer == verb.article:
                    correct_count += 1
                    entry.dative_correct += 1
                    print(f"  {Colors.GREEN}✓ Correct!{Colors.END}  {filled}")
                else:
                    entry.dative_incorrect += 1
                    print(f"  {Colors.RED}✗ Incorrect.{Colors.END}  {filled}")

                print(f"  Rule: {verb.noun_base}  →  {rule}")
                print(sep)
                break

            if quit_requested:
                break

        if not infinite:
            break

    _print_score(correct_count, total_count)


# ---------------------------------------------------------------------------
# Shared score display
# ---------------------------------------------------------------------------

def _print_score(correct: int, total: int) -> None:
    if total > 0:
        pct = 100 * correct // total
        print(f"\n{Colors.BOLD}Score: {correct}/{total} ({pct}%){Colors.END}")
        if pct >= 90:
            print(f"{Colors.GREEN}Ausgezeichnet! Keep it up.{Colors.END}")
        elif pct >= 70:
            print(f"{Colors.YELLOW}Good progress! Keep practicing.{Colors.END}")
        else:
            print(f"{Colors.RED}Keep studying! Focus on the patterns.{Colors.END}")
    else:
        print("No questions answered.")


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def print_stats(verbs: list[Verb], progress: dict[str, VerbProgress]) -> None:
    if not progress:
        print("No progress yet — start a quiz to see statistics!")
        return

    total = len(verbs)
    reviewed = sum(1 for v in verbs if v.german in progress)
    print(f"\n{Colors.BOLD}=== Dative Verb Statistics ==={Colors.END}\n")
    print(f"Total verbs:   {total}")
    print(f"Reviewed:      {reviewed}  ({100 * reviewed // total}%)")
    print(f"Not yet seen:  {total - reviewed}")

    # Translation accuracy
    trans = [
        (v, p.correct, p.correct + p.incorrect)
        for v in verbs
        if v.german in progress
        for p in [progress[v.german]]
        if p.correct + p.incorrect > 0
    ]
    if trans:
        trans.sort(key=lambda x: x[1] / x[2])
        print(f"\n{Colors.BOLD}Translation — hardest verbs:{Colors.END}")
        col_w = max(len(v.german) for v, *_ in trans[:10])
        for v, correct, total_att in trans[:10]:
            pct = 100 * correct // total_att
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            print(f"  {v.german:<{col_w + 2}} {correct}/{total_att}  {pct:3d}%  {bar}")

    # Dative accuracy
    dative = [
        (v, p.dative_correct, p.dative_correct + p.dative_incorrect)
        for v in verbs
        if v.german in progress
        for p in [progress[v.german]]
        if p.dative_correct + p.dative_incorrect > 0
    ]
    if dative:
        dative.sort(key=lambda x: x[1] / x[2])
        print(f"\n{Colors.BOLD}Dative article — hardest verbs:{Colors.END}")
        col_w = max(len(v.german) for v, *_ in dative[:10])
        for v, correct, total_att in dative[:10]:
            pct = 100 * correct // total_att
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            print(f"  {v.german:<{col_w + 2}} {correct}/{total_att}  {pct:3d}%  {bar}  ({v.noun_base})")


# ---------------------------------------------------------------------------
# List verbs
# ---------------------------------------------------------------------------

def list_verbs(verbs: list[Verb]) -> None:
    print(f"\n{Colors.BOLD}Dative Verbs — {len(verbs)} total{Colors.END}\n")
    col_w = max(len(v.german) for v in verbs) + 2
    for v in verbs:
        print(f"  {Colors.BOLD}{v.german:<{col_w}}{Colors.END}{v.english}")
        print(f"  {' ' * col_w}{Colors.CYAN}{v.memory}{Colors.END}")
        print(f"  {' ' * col_w}{v.example.replace('___', Colors.BOLD + v.article + Colors.END)}")
        print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="German Dative Verb Quiz")
    parser.add_argument(
        "--mode", choices=["de", "en", "random", "dative"], default=None,
        help="de=German→English, en=English→German, random=mixed, dative=article quiz",
    )
    parser.add_argument("--num", type=int, default=10, metavar="N",
                        help="Number of questions (default: 10; 0=all)")
    parser.add_argument("--infinite", action="store_true",
                        help="Keep quizzing until Ctrl+C or 'q'")
    parser.add_argument("--no-hints", dest="no_hints", action="store_true",
                        help="Hard mode: hide hints")
    parser.add_argument("--stats", action="store_true",
                        help="Show learning statistics and exit")
    parser.add_argument("--list", action="store_true",
                        help="List all verbs and exit")
    parser.add_argument("--reset", action="store_true",
                        help="Reset all progress and exit")
    args = parser.parse_args()

    progress_file = Path(__file__).parent / "progress.json"
    progress = load_progress(progress_file)

    if args.reset:
        progress_file.unlink(missing_ok=True)
        print(f"{Colors.GREEN}Progress reset.{Colors.END}")
        return 0

    if args.stats:
        print_stats(VERBS, progress)
        return 0

    if args.list:
        list_verbs(VERBS)
        return 0

    num = len(VERBS) if args.num == 0 else args.num

    mode = args.mode
    if mode is None:
        print(f"\n{Colors.BOLD}Select quiz mode:{Colors.END}")
        print("  [1] German → English")
        print("  [2] English → German")
        print("  [3] Random (mixed)")
        print(f"  [4] Dative article  (fill in {Colors.BOLD}dem{Colors.END} / {Colors.BOLD}der{Colors.END} / {Colors.BOLD}den{Colors.END})")
        print("  [s] Statistics")
        print("  [l] List all verbs")
        print("  [q] Quit")
        while True:
            choice = input("\nMode> ").strip().lower()
            if choice == "q":
                return 0
            if choice == "s":
                print_stats(VERBS, progress)
                continue
            if choice == "l":
                list_verbs(VERBS)
                continue
            if choice in ("1", "de"):
                mode = "de"; break
            if choice in ("2", "en"):
                mode = "en"; break
            if choice in ("3", "r", "random"):
                mode = "random"; break
            if choice in ("4", "dative", "d"):
                mode = "dative"; break
            print("Invalid choice. Enter 1–4, s, l, or q.")

    try:
        if mode == "dative":
            run_dative_quiz(
                VERBS, progress,
                num=num,
                infinite=args.infinite,
                show_hints=not args.no_hints,
            )
        else:
            run_translation_quiz(
                VERBS, progress, mode,
                num=num,
                infinite=args.infinite,
                show_hints=not args.no_hints,
            )
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Quiz interrupted.{Colors.END}")
    finally:
        save_progress(progress_file, progress)
        print(f"Progress saved to {progress_file.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
