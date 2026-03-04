from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Word:
    german: str        # e.g. "Freiheit"
    english: str       # e.g. "freedom"
    gender: str        # "der" | "die" | "das"
    category: str      # e.g. "-heit", "weather", "Ge-"
    category_type: str # "suffix" | "semantic"
    rule: str          # explanation shown after answering
    weak: bool = False # True for -ig, -nis, -e (caveat shown)


# ---------------------------------------------------------------------------
# Rules (defined once, referenced in Word entries)
# ---------------------------------------------------------------------------

_RULE_IG = (
    "Nouns ending in -ig are usually masculine — but most -ig words are "
    "adjectives, not nouns. When you do see a noun ending in -ig, masculine "
    "is usually correct. "
    "\u26a0 Exceptions exist \u2014 verify new -ig words in a dictionary."
)

_RULE_LING = (
    "Nouns ending in -ling are almost always masculine \u2014 this is one of "
    "the most reliable gender rules."
)

_RULE_OR = (
    "Nouns ending in -or are almost always masculine. "
    "Exceptions: das Labor, das Tor."
)

_RULE_ISMUS = (
    "Nouns ending in -ismus are always masculine \u2014 no exceptions."
)

_RULE_ER = (
    "Agent nouns (professions/roles) ending in -er are almost always "
    "masculine. Exceptions: die Mutter, die Schwester, die Butter."
)

_RULE_ANT = (
    "Nouns ending in -ant are usually masculine."
)

_RULE_UNG = (
    "Nouns ending in -ung are always feminine \u2014 one of the most reliable "
    "rules in German. (Note: monosyllabic words like der Dung, der Sprung use "
    "a different -ung that is NOT this suffix.)"
)

_RULE_HEIT = (
    "Nouns ending in -heit are always feminine \u2014 no exceptions."
)

_RULE_KEIT = (
    "Nouns ending in -keit are always feminine \u2014 no exceptions. "
    "(-keit is a variant of -heit, added to adjectives ending in -lich or -ig.)"
)

_RULE_SCHAFT = (
    "Nouns ending in -schaft are always feminine \u2014 no exceptions."
)

_RULE_ION = (
    "Nouns ending in -ion are always feminine \u2014 no exceptions."
)

_RULE_TAT = (
    "Nouns ending in -t\u00e4t are always feminine \u2014 no exceptions."
)

_RULE_IE = (
    "Nouns ending in -ie are almost always feminine. "
    "Exception: das Knie (knee)."
)

_RULE_IK = (
    "Nouns ending in -ik are almost always feminine. "
    "Exceptions: der Atlantik, der Pazifik (ocean names), das Mosaik."
)

_RULE_UR = (
    "Nouns ending in -ur are almost always feminine. "
    "Exceptions: das Abitur, das Futur. "
    "(Note: das Abenteuer ends in -er, not -ur.)"
)

_RULE_EI = (
    "Nouns ending in -ei are almost always feminine, often denoting a place "
    "of work or trade."
)

_RULE_E = (
    "Most nouns ending in -e are feminine (~85%). However, masculine n-nouns "
    "are a common exception: der Junge, der Affe, der Name, der K\u00e4se, "
    "der Hase, der L\u00f6we."
)

_RULE_CHEN = (
    "Nouns ending in -chen are always neuter \u2014 no exceptions. "
    "This suffix creates diminutives."
)

_RULE_LEIN = (
    "Nouns ending in -lein are always neuter \u2014 no exceptions. "
    "This suffix creates diminutives (literary/regional variant of -chen)."
)

_RULE_MENT = (
    "Nouns ending in -ment are almost always neuter \u2014 no exceptions."
)

_RULE_UM = (
    "Nouns ending in -um are almost always neuter \u2014 no exceptions."
)

_RULE_MA = (
    "Nouns of Greek origin ending in -ma are almost always neuter. "
    "Exception: die Firma (company)."
)

_RULE_TUM = (
    "Nouns ending in -tum are almost always neuter. "
    "Exceptions: der Reichtum (wealth), der Irrtum (error)."
)

_RULE_NIS = (
    "About 70% of -nis nouns are neuter. However, several common ones are "
    "feminine: die Finsternis, die Wildnis, die Kenntnis, die Erlaubnis, "
    "die Besorgnis."
)

_RULE_DAYS = (
    "Days of the week, months, and seasons are always masculine."
)

_RULE_WEATHER = (
    "Weather phenomena are almost always masculine."
)

_RULE_ALCOHOL = (
    "Alcoholic drinks are almost always masculine. Exception: das Bier (beer)."
)

_RULE_CARS = (
    "Car brands are always masculine (short for 'der Wagen' or 'der PKW')."
)

_RULE_TREES = (
    "Most trees and flowers are feminine."
)

_RULE_FRUITS = (
    "Most fruits are feminine. Exceptions: der Apfel (apple), das Obst "
    "(fruit in general)."
)

_RULE_RIVERS = (
    "Most rivers in Germany and Central Europe are feminine. "
    "Exceptions: der Rhein, der Main, der Neckar, der Inn."
)

_RULE_NUMBERS = (
    "Named numbers (die Eins, die Zwei\u2026) and large numerals are feminine."
)

_RULE_METALS = (
    "Most metals are neuter. Exceptions: der Stahl (steel), die Bronze (bronze)."
)

_RULE_VENUES = (
    "Hotels, caf\u00e9s, theaters, and similar venues are usually neuter."
)

_RULE_LANGUAGES = (
    "Names of languages are always neuter."
)

_RULE_VERBAL = (
    "When a verb infinitive is used as a noun, it is always neuter."
)

_RULE_GE = (
    "Nouns beginning with Ge- are almost always neuter."
)

_RULE_YOUNG = (
    "Words for young people and animals are usually neuter."
)


# ---------------------------------------------------------------------------
# Word list
# ---------------------------------------------------------------------------

WORDS: list[Word] = [

    # -----------------------------------------------------------------------
    # SUFFIX: -ig  (der, weak)
    # -----------------------------------------------------------------------
    Word("Essig",   "vinegar",  "der", "-ig", "suffix", _RULE_IG, weak=True),
    Word("König",   "king",     "der", "-ig", "suffix", _RULE_IG, weak=True),
    Word("Honig",   "honey",    "der", "-ig", "suffix", _RULE_IG, weak=True),
    Word("Käfig",   "cage",     "der", "-ig", "suffix", _RULE_IG, weak=True),
    Word("Pfennig", "pfennig",  "der", "-ig", "suffix", _RULE_IG, weak=True),
    Word("Zeisig",  "siskin",   "der", "-ig", "suffix", _RULE_IG, weak=True),

    # -----------------------------------------------------------------------
    # SUFFIX: -ling  (der)
    # -----------------------------------------------------------------------
    Word("Frühling",     "spring",        "der", "-ling", "suffix", _RULE_LING),
    Word("Lehrling",     "apprentice",    "der", "-ling", "suffix", _RULE_LING),
    Word("Schmetterling","butterfly",     "der", "-ling", "suffix", _RULE_LING),
    Word("Liebling",     "darling",       "der", "-ling", "suffix", _RULE_LING),
    Word("Zwilling",     "twin",          "der", "-ling", "suffix", _RULE_LING),
    Word("Flüchtling",   "refugee",       "der", "-ling", "suffix", _RULE_LING),
    Word("Säugling",     "infant",        "der", "-ling", "suffix", _RULE_LING),
    Word("Feigling",     "coward",        "der", "-ling", "suffix", _RULE_LING),
    Word("Drilling",     "triplet",       "der", "-ling", "suffix", _RULE_LING),
    Word("Häftling",     "prisoner",      "der", "-ling", "suffix", _RULE_LING),
    Word("Keimling",     "seedling",      "der", "-ling", "suffix", _RULE_LING),
    Word("Jüngling",     "youth",         "der", "-ling", "suffix", _RULE_LING),
    Word("Sperling",     "sparrow",       "der", "-ling", "suffix", _RULE_LING),
    Word("Prüfling",     "examinee",      "der", "-ling", "suffix", _RULE_LING),
    Word("Findling",     "foundling",     "der", "-ling", "suffix", _RULE_LING),
    Word("Fremdling",    "stranger",      "der", "-ling", "suffix", _RULE_LING),
    Word("Rohling",      "blank/rough person", "der", "-ling", "suffix", _RULE_LING),
    Word("Stichling",    "stickleback",   "der", "-ling", "suffix", _RULE_LING),
    Word("Ankömmling",   "newcomer",      "der", "-ling", "suffix", _RULE_LING),
    Word("Eindringling", "intruder",      "der", "-ling", "suffix", _RULE_LING),

    # -----------------------------------------------------------------------
    # SUFFIX: -or  (der)
    # -----------------------------------------------------------------------
    Word("Motor",       "motor",      "der", "-or", "suffix", _RULE_OR),
    Word("Autor",       "author",     "der", "-or", "suffix", _RULE_OR),
    Word("Doktor",      "doctor",     "der", "-or", "suffix", _RULE_OR),
    Word("Professor",   "professor",  "der", "-or", "suffix", _RULE_OR),
    Word("Reaktor",     "reactor",    "der", "-or", "suffix", _RULE_OR),
    Word("Senator",     "senator",    "der", "-or", "suffix", _RULE_OR),
    Word("Traktor",     "tractor",    "der", "-or", "suffix", _RULE_OR),
    Word("Faktor",      "factor",     "der", "-or", "suffix", _RULE_OR),
    Word("Direktor",    "director",   "der", "-or", "suffix", _RULE_OR),
    Word("Generator",   "generator",  "der", "-or", "suffix", _RULE_OR),
    Word("Kondensator", "capacitor",  "der", "-or", "suffix", _RULE_OR),
    Word("Moderator",   "moderator",  "der", "-or", "suffix", _RULE_OR),
    Word("Korridor",    "corridor",   "der", "-or", "suffix", _RULE_OR),
    Word("Humor",       "humour",     "der", "-or", "suffix", _RULE_OR),
    Word("Tumor",       "tumour",     "der", "-or", "suffix", _RULE_OR),
    Word("Tenor",       "tenor",      "der", "-or", "suffix", _RULE_OR),
    Word("Horror",      "horror",     "der", "-or", "suffix", _RULE_OR),
    Word("Pastor",      "pastor",     "der", "-or", "suffix", _RULE_OR),
    Word("Vektor",      "vector",     "der", "-or", "suffix", _RULE_OR),
    Word("Monitor",     "monitor",    "der", "-or", "suffix", _RULE_OR),

    # -----------------------------------------------------------------------
    # SUFFIX: -ismus  (der)
    # -----------------------------------------------------------------------
    Word("Tourismus",      "tourism",       "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Kapitalismus",   "capitalism",    "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Sozialismus",    "socialism",     "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Kommunismus",    "communism",     "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Terrorismus",    "terrorism",     "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Optimismus",     "optimism",      "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Pessimismus",    "pessimism",     "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Realismus",      "realism",       "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Idealismus",     "idealism",      "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Nationalismus",  "nationalism",   "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Faschismus",     "fascism",       "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Rassismus",      "racism",        "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Sexismus",       "sexism",        "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Humanismus",     "humanism",      "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Altruismus",     "altruism",      "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Egoismus",       "egoism",        "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Liberalismus",   "liberalism",    "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Surrealismus",   "surrealism",    "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Atheismus",      "atheism",       "der", "-ismus", "suffix", _RULE_ISMUS),
    Word("Anarchismus",    "anarchism",     "der", "-ismus", "suffix", _RULE_ISMUS),

    # -----------------------------------------------------------------------
    # SUFFIX: -er  (der, agent nouns)
    # -----------------------------------------------------------------------
    Word("Lehrer",        "teacher",        "der", "-er", "suffix", _RULE_ER),
    Word("Bäcker",        "baker",          "der", "-er", "suffix", _RULE_ER),
    Word("Fahrer",        "driver",         "der", "-er", "suffix", _RULE_ER),
    Word("Schüler",       "student",        "der", "-er", "suffix", _RULE_ER),
    Word("Maler",         "painter",        "der", "-er", "suffix", _RULE_ER),
    Word("Künstler",      "artist",         "der", "-er", "suffix", _RULE_ER),
    Word("Leser",         "reader",         "der", "-er", "suffix", _RULE_ER),
    Word("Käufer",        "buyer",          "der", "-er", "suffix", _RULE_ER),
    Word("Verkäufer",     "seller",         "der", "-er", "suffix", _RULE_ER),
    Word("Trainer",       "trainer",        "der", "-er", "suffix", _RULE_ER),
    Word("Spieler",       "player",         "der", "-er", "suffix", _RULE_ER),
    Word("Redner",        "speaker",        "der", "-er", "suffix", _RULE_ER),
    Word("Denker",        "thinker",        "der", "-er", "suffix", _RULE_ER),
    Word("Buchhalter",    "accountant",     "der", "-er", "suffix", _RULE_ER),
    Word("Handwerker",    "craftsman",      "der", "-er", "suffix", _RULE_ER),
    Word("Techniker",     "technician",     "der", "-er", "suffix", _RULE_ER),
    Word("Gärtner",       "gardener",       "der", "-er", "suffix", _RULE_ER),
    Word("Besitzer",      "owner",          "der", "-er", "suffix", _RULE_ER),
    Word("Verwalter",     "administrator",  "der", "-er", "suffix", _RULE_ER),
    Word("Richter",       "judge",          "der", "-er", "suffix", _RULE_ER),
    Word("Schriftsteller","writer",         "der", "-er", "suffix", _RULE_ER),
    Word("Forscher",      "researcher",     "der", "-er", "suffix", _RULE_ER),
    Word("Wissenschaftler","scientist",     "der", "-er", "suffix", _RULE_ER),
    Word("Mitarbeiter",   "employee",       "der", "-er", "suffix", _RULE_ER),

    # -----------------------------------------------------------------------
    # SUFFIX: -ant  (der)
    # -----------------------------------------------------------------------
    Word("Elefant",    "elephant",     "der", "-ant", "suffix", _RULE_ANT),
    Word("Diamant",    "diamond",      "der", "-ant", "suffix", _RULE_ANT),
    Word("Praktikant", "intern",       "der", "-ant", "suffix", _RULE_ANT),
    Word("Konsonant",  "consonant",    "der", "-ant", "suffix", _RULE_ANT),
    Word("Fabrikant",  "manufacturer", "der", "-ant", "suffix", _RULE_ANT),
    Word("Lieferant",  "supplier",     "der", "-ant", "suffix", _RULE_ANT),
    Word("Pedant",     "pedant",       "der", "-ant", "suffix", _RULE_ANT),
    Word("Spekulant",  "speculator",   "der", "-ant", "suffix", _RULE_ANT),
    Word("Komödiant",  "comedian",     "der", "-ant", "suffix", _RULE_ANT),
    Word("Musikant",   "musician",     "der", "-ant", "suffix", _RULE_ANT),
    Word("Figurant",   "extra",        "der", "-ant", "suffix", _RULE_ANT),
    Word("Adjutant",   "adjutant",     "der", "-ant", "suffix", _RULE_ANT),
    Word("Intrigant",  "schemer",      "der", "-ant", "suffix", _RULE_ANT),
    Word("Aspirant",   "aspirant",     "der", "-ant", "suffix", _RULE_ANT),
    Word("Trabant",    "satellite/henchman", "der", "-ant", "suffix", _RULE_ANT),

    # -----------------------------------------------------------------------
    # SUFFIX: -ung  (die)
    # -----------------------------------------------------------------------
    Word("Zeitung",       "newspaper",   "die", "-ung", "suffix", _RULE_UNG),
    Word("Wohnung",       "apartment",   "die", "-ung", "suffix", _RULE_UNG),
    Word("Meinung",       "opinion",     "die", "-ung", "suffix", _RULE_UNG),
    Word("Übung",         "exercise",    "die", "-ung", "suffix", _RULE_UNG),
    Word("Hoffnung",      "hope",        "die", "-ung", "suffix", _RULE_UNG),
    Word("Bedeutung",     "meaning",     "die", "-ung", "suffix", _RULE_UNG),
    Word("Regierung",     "government",  "die", "-ung", "suffix", _RULE_UNG),
    Word("Lösung",        "solution",    "die", "-ung", "suffix", _RULE_UNG),
    Word("Rechnung",      "invoice",     "die", "-ung", "suffix", _RULE_UNG),
    Word("Bewegung",      "movement",    "die", "-ung", "suffix", _RULE_UNG),
    Word("Erfahrung",     "experience",  "die", "-ung", "suffix", _RULE_UNG),
    Word("Warnung",       "warning",     "die", "-ung", "suffix", _RULE_UNG),
    Word("Ordnung",       "order",       "die", "-ung", "suffix", _RULE_UNG),
    Word("Leitung",       "management",  "die", "-ung", "suffix", _RULE_UNG),
    Word("Beschreibung",  "description", "die", "-ung", "suffix", _RULE_UNG),
    Word("Entscheidung",  "decision",    "die", "-ung", "suffix", _RULE_UNG),
    Word("Verbindung",    "connection",  "die", "-ung", "suffix", _RULE_UNG),
    Word("Bildung",       "education",   "die", "-ung", "suffix", _RULE_UNG),
    Word("Prüfung",       "exam",        "die", "-ung", "suffix", _RULE_UNG),
    Word("Veranstaltung", "event",       "die", "-ung", "suffix", _RULE_UNG),
    Word("Verbesserung",  "improvement", "die", "-ung", "suffix", _RULE_UNG),
    Word("Planung",       "planning",    "die", "-ung", "suffix", _RULE_UNG),
    Word("Zahlung",       "payment",     "die", "-ung", "suffix", _RULE_UNG),
    Word("Sendung",       "broadcast",   "die", "-ung", "suffix", _RULE_UNG),
    Word("Einladung",     "invitation",  "die", "-ung", "suffix", _RULE_UNG),

    # -----------------------------------------------------------------------
    # SUFFIX: -heit  (die)
    # -----------------------------------------------------------------------
    Word("Gesundheit",  "health",     "die", "-heit", "suffix", _RULE_HEIT),
    Word("Freiheit",    "freedom",    "die", "-heit", "suffix", _RULE_HEIT),
    Word("Wahrheit",    "truth",      "die", "-heit", "suffix", _RULE_HEIT),
    Word("Schönheit",   "beauty",     "die", "-heit", "suffix", _RULE_HEIT),
    Word("Kindheit",    "childhood",  "die", "-heit", "suffix", _RULE_HEIT),
    Word("Einheit",     "unity",      "die", "-heit", "suffix", _RULE_HEIT),
    Word("Dunkelheit",  "darkness",   "die", "-heit", "suffix", _RULE_HEIT),
    Word("Mehrheit",    "majority",   "die", "-heit", "suffix", _RULE_HEIT),
    Word("Sicherheit",  "security",   "die", "-heit", "suffix", _RULE_HEIT),
    Word("Krankheit",   "illness",    "die", "-heit", "suffix", _RULE_HEIT),
    Word("Weisheit",    "wisdom",     "die", "-heit", "suffix", _RULE_HEIT),
    Word("Dummheit",    "stupidity",  "die", "-heit", "suffix", _RULE_HEIT),
    Word("Neuheit",     "novelty",    "die", "-heit", "suffix", _RULE_HEIT),
    Word("Faulheit",    "laziness",   "die", "-heit", "suffix", _RULE_HEIT),
    Word("Feigheit",    "cowardice",  "die", "-heit", "suffix", _RULE_HEIT),

    # -----------------------------------------------------------------------
    # SUFFIX: -keit  (die)
    # -----------------------------------------------------------------------
    Word("Möglichkeit",      "possibility",  "die", "-keit", "suffix", _RULE_KEIT),
    Word("Schwierigkeit",    "difficulty",   "die", "-keit", "suffix", _RULE_KEIT),
    Word("Fähigkeit",        "ability",      "die", "-keit", "suffix", _RULE_KEIT),
    Word("Freundlichkeit",   "friendliness", "die", "-keit", "suffix", _RULE_KEIT),
    Word("Ähnlichkeit",      "similarity",   "die", "-keit", "suffix", _RULE_KEIT),
    Word("Höflichkeit",      "politeness",   "die", "-keit", "suffix", _RULE_KEIT),
    Word("Persönlichkeit",   "personality",  "die", "-keit", "suffix", _RULE_KEIT),
    Word("Wirklichkeit",     "reality",      "die", "-keit", "suffix", _RULE_KEIT),
    Word("Aufmerksamkeit",   "attention",    "die", "-keit", "suffix", _RULE_KEIT),
    Word("Genauigkeit",      "accuracy",     "die", "-keit", "suffix", _RULE_KEIT),
    Word("Dankbarkeit",      "gratitude",    "die", "-keit", "suffix", _RULE_KEIT),
    Word("Ehrlichkeit",      "honesty",      "die", "-keit", "suffix", _RULE_KEIT),
    Word("Zuverlässigkeit",  "reliability",  "die", "-keit", "suffix", _RULE_KEIT),
    Word("Einsamkeit",       "loneliness",   "die", "-keit", "suffix", _RULE_KEIT),
    Word("Heiterkeit",       "cheerfulness", "die", "-keit", "suffix", _RULE_KEIT),
    Word("Pünktlichkeit",    "punctuality",  "die", "-keit", "suffix", _RULE_KEIT),
    Word("Sauberkeit",       "cleanliness",  "die", "-keit", "suffix", _RULE_KEIT),
    Word("Geschwindigkeit",  "speed",        "die", "-keit", "suffix", _RULE_KEIT),
    Word("Tätigkeit",        "activity",     "die", "-keit", "suffix", _RULE_KEIT),
    Word("Selbstständigkeit","independence", "die", "-keit", "suffix", _RULE_KEIT),

    # -----------------------------------------------------------------------
    # SUFFIX: -schaft  (die)
    # -----------------------------------------------------------------------
    Word("Freundschaft",    "friendship",     "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Gesellschaft",    "society",        "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Mannschaft",      "team",           "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Wissenschaft",    "science",        "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Landschaft",      "landscape",      "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Gemeinschaft",    "community",      "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Herrschaft",      "rule",           "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Leidenschaft",    "passion",        "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Botschaft",       "message",        "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Eigenschaft",     "characteristic", "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Nachbarschaft",   "neighbourhood",  "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Meisterschaft",   "championship",   "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Mitgliedschaft",  "membership",     "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Bereitschaft",    "readiness",      "die", "-schaft", "suffix", _RULE_SCHAFT),
    Word("Errungenschaft",  "achievement",    "die", "-schaft", "suffix", _RULE_SCHAFT),

    # -----------------------------------------------------------------------
    # SUFFIX: -ion  (die)
    # -----------------------------------------------------------------------
    Word("Nation",        "nation",         "die", "-ion", "suffix", _RULE_ION),
    Word("Station",       "station",        "die", "-ion", "suffix", _RULE_ION),
    Word("Information",   "information",    "die", "-ion", "suffix", _RULE_ION),
    Word("Revolution",    "revolution",     "die", "-ion", "suffix", _RULE_ION),
    Word("Diskussion",    "discussion",     "die", "-ion", "suffix", _RULE_ION),
    Word("Funktion",      "function",       "die", "-ion", "suffix", _RULE_ION),
    Word("Produktion",    "production",     "die", "-ion", "suffix", _RULE_ION),
    Word("Situation",     "situation",      "die", "-ion", "suffix", _RULE_ION),
    Word("Organisation",  "organisation",   "die", "-ion", "suffix", _RULE_ION),
    Word("Portion",       "portion",        "die", "-ion", "suffix", _RULE_ION),
    Word("Region",        "region",         "die", "-ion", "suffix", _RULE_ION),
    Word("Union",         "union",          "die", "-ion", "suffix", _RULE_ION),
    Word("Tradition",     "tradition",      "die", "-ion", "suffix", _RULE_ION),
    Word("Generation",    "generation",     "die", "-ion", "suffix", _RULE_ION),
    Word("Emotion",       "emotion",        "die", "-ion", "suffix", _RULE_ION),
    Word("Formation",     "formation",      "die", "-ion", "suffix", _RULE_ION),
    Word("Aggression",    "aggression",     "die", "-ion", "suffix", _RULE_ION),
    Word("Position",      "position",       "die", "-ion", "suffix", _RULE_ION),
    Word("Lektion",       "lesson",         "die", "-ion", "suffix", _RULE_ION),
    Word("Sensation",     "sensation",      "die", "-ion", "suffix", _RULE_ION),
    Word("Reaktion",      "reaction",       "die", "-ion", "suffix", _RULE_ION),
    Word("Aktion",        "action",         "die", "-ion", "suffix", _RULE_ION),
    Word("Konstruktion",  "construction",   "die", "-ion", "suffix", _RULE_ION),
    Word("Expedition",    "expedition",     "die", "-ion", "suffix", _RULE_ION),
    Word("Pension",       "boarding house", "die", "-ion", "suffix", _RULE_ION),

    # -----------------------------------------------------------------------
    # SUFFIX: -tät  (die)
    # -----------------------------------------------------------------------
    Word("Universität",  "university",  "die", "-tät", "suffix", _RULE_TAT),
    Word("Realität",     "reality",     "die", "-tät", "suffix", _RULE_TAT),
    Word("Qualität",     "quality",     "die", "-tät", "suffix", _RULE_TAT),
    Word("Quantität",    "quantity",    "die", "-tät", "suffix", _RULE_TAT),
    Word("Nationalität", "nationality", "die", "-tät", "suffix", _RULE_TAT),
    Word("Kapazität",    "capacity",    "die", "-tät", "suffix", _RULE_TAT),
    Word("Kreativität",  "creativity",  "die", "-tät", "suffix", _RULE_TAT),
    Word("Aktivität",    "activity",    "die", "-tät", "suffix", _RULE_TAT),
    Word("Neutralität",  "neutrality",  "die", "-tät", "suffix", _RULE_TAT),
    Word("Solidarität",  "solidarity",  "die", "-tät", "suffix", _RULE_TAT),
    Word("Produktivität","productivity","die", "-tät", "suffix", _RULE_TAT),
    Word("Stabilität",   "stability",   "die", "-tät", "suffix", _RULE_TAT),
    Word("Flexibilität", "flexibility", "die", "-tät", "suffix", _RULE_TAT),
    Word("Spezialität",  "speciality",  "die", "-tät", "suffix", _RULE_TAT),
    Word("Sensibilität", "sensitivity", "die", "-tät", "suffix", _RULE_TAT),
    Word("Komplexität",  "complexity",  "die", "-tät", "suffix", _RULE_TAT),
    Word("Relativität",  "relativity",  "die", "-tät", "suffix", _RULE_TAT),
    Word("Elektrizität", "electricity", "die", "-tät", "suffix", _RULE_TAT),
    Word("Elastizität",  "elasticity",  "die", "-tät", "suffix", _RULE_TAT),
    Word("Autorität",    "authority",   "die", "-tät", "suffix", _RULE_TAT),

    # -----------------------------------------------------------------------
    # SUFFIX: -ie  (die)
    # -----------------------------------------------------------------------
    Word("Biologie",    "biology",      "die", "-ie", "suffix", _RULE_IE),
    Word("Demokratie",  "democracy",    "die", "-ie", "suffix", _RULE_IE),
    Word("Energie",     "energy",       "die", "-ie", "suffix", _RULE_IE),
    Word("Fantasie",    "fantasy",      "die", "-ie", "suffix", _RULE_IE),
    Word("Philosophie", "philosophy",   "die", "-ie", "suffix", _RULE_IE),
    Word("Strategie",   "strategy",     "die", "-ie", "suffix", _RULE_IE),
    Word("Theorie",     "theory",       "die", "-ie", "suffix", _RULE_IE),
    Word("Industrie",   "industry",     "die", "-ie", "suffix", _RULE_IE),
    Word("Hierarchie",  "hierarchy",    "die", "-ie", "suffix", _RULE_IE),
    Word("Kategorie",   "category",     "die", "-ie", "suffix", _RULE_IE),
    Word("Psychologie", "psychology",   "die", "-ie", "suffix", _RULE_IE),
    Word("Soziologie",  "sociology",    "die", "-ie", "suffix", _RULE_IE),
    Word("Melodie",     "melody",       "die", "-ie", "suffix", _RULE_IE),
    Word("Ironie",      "irony",        "die", "-ie", "suffix", _RULE_IE),
    Word("Therapie",    "therapy",      "die", "-ie", "suffix", _RULE_IE),
    Word("Chemie",      "chemistry",    "die", "-ie", "suffix", _RULE_IE),
    Word("Geographie",  "geography",    "die", "-ie", "suffix", _RULE_IE),
    Word("Astronomie",  "astronomy",    "die", "-ie", "suffix", _RULE_IE),
    Word("Anatomie",    "anatomy",      "die", "-ie", "suffix", _RULE_IE),
    Word("Ökologie",    "ecology",      "die", "-ie", "suffix", _RULE_IE),

    # -----------------------------------------------------------------------
    # SUFFIX: -ik  (die)
    # -----------------------------------------------------------------------
    Word("Musik",       "music",           "die", "-ik", "suffix", _RULE_IK),
    Word("Physik",      "physics",         "die", "-ik", "suffix", _RULE_IK),
    Word("Mathematik",  "mathematics",     "die", "-ik", "suffix", _RULE_IK),
    Word("Politik",     "politics",        "die", "-ik", "suffix", _RULE_IK),
    Word("Technik",     "technology",      "die", "-ik", "suffix", _RULE_IK),
    Word("Grammatik",   "grammar",         "die", "-ik", "suffix", _RULE_IK),
    Word("Logik",       "logic",           "die", "-ik", "suffix", _RULE_IK),
    Word("Statistik",   "statistics",      "die", "-ik", "suffix", _RULE_IK),
    Word("Kritik",      "criticism",       "die", "-ik", "suffix", _RULE_IK),
    Word("Panik",       "panic",           "die", "-ik", "suffix", _RULE_IK),
    Word("Fabrik",      "factory",         "die", "-ik", "suffix", _RULE_IK),
    Word("Klinik",      "clinic",          "die", "-ik", "suffix", _RULE_IK),
    Word("Romantik",    "romanticism",     "die", "-ik", "suffix", _RULE_IK),
    Word("Akustik",     "acoustics",       "die", "-ik", "suffix", _RULE_IK),
    Word("Ethik",       "ethics",          "die", "-ik", "suffix", _RULE_IK),
    Word("Ästhetik",    "aesthetics",      "die", "-ik", "suffix", _RULE_IK),
    Word("Optik",       "optics",          "die", "-ik", "suffix", _RULE_IK),
    Word("Mystik",      "mysticism",       "die", "-ik", "suffix", _RULE_IK),
    Word("Poetik",      "poetics",         "die", "-ik", "suffix", _RULE_IK),
    Word("Symbolik",    "symbolism",       "die", "-ik", "suffix", _RULE_IK),

    # -----------------------------------------------------------------------
    # SUFFIX: -ur  (die)
    # -----------------------------------------------------------------------
    Word("Natur",        "nature",           "die", "-ur", "suffix", _RULE_UR),
    Word("Kultur",       "culture",          "die", "-ur", "suffix", _RULE_UR),
    Word("Temperatur",   "temperature",      "die", "-ur", "suffix", _RULE_UR),
    Word("Struktur",     "structure",        "die", "-ur", "suffix", _RULE_UR),
    Word("Miniatur",     "miniature",        "die", "-ur", "suffix", _RULE_UR),
    Word("Figur",        "figure",           "die", "-ur", "suffix", _RULE_UR),
    Word("Signatur",     "signature",        "die", "-ur", "suffix", _RULE_UR),
    Word("Diktatur",     "dictatorship",     "die", "-ur", "suffix", _RULE_UR),
    Word("Literatur",    "literature",       "die", "-ur", "suffix", _RULE_UR),
    Word("Architektur",  "architecture",     "die", "-ur", "suffix", _RULE_UR),
    Word("Konjunktur",   "economic climate", "die", "-ur", "suffix", _RULE_UR),
    Word("Tortur",       "torture",          "die", "-ur", "suffix", _RULE_UR),
    Word("Armatur",      "fitting",          "die", "-ur", "suffix", _RULE_UR),
    Word("Textur",       "texture",          "die", "-ur", "suffix", _RULE_UR),

    # -----------------------------------------------------------------------
    # SUFFIX: -ei  (die)
    # -----------------------------------------------------------------------
    Word("Bäckerei",     "bakery",        "die", "-ei", "suffix", _RULE_EI),
    Word("Bücherei",     "library",       "die", "-ei", "suffix", _RULE_EI),
    Word("Metzgerei",    "butcher's",     "die", "-ei", "suffix", _RULE_EI),
    Word("Konditorei",   "pastry shop",   "die", "-ei", "suffix", _RULE_EI),
    Word("Gärtnerei",    "nursery",       "die", "-ei", "suffix", _RULE_EI),
    Word("Malerei",      "painting",      "die", "-ei", "suffix", _RULE_EI),
    Word("Schreinerei",  "carpentry",     "die", "-ei", "suffix", _RULE_EI),
    Word("Tischlerei",   "joinery",       "die", "-ei", "suffix", _RULE_EI),
    Word("Schlägerei",   "brawl",         "die", "-ei", "suffix", _RULE_EI),
    Word("Weberei",      "weaving mill",  "die", "-ei", "suffix", _RULE_EI),
    Word("Druckerei",    "print shop",    "die", "-ei", "suffix", _RULE_EI),
    Word("Kellerei",     "wine cellar",   "die", "-ei", "suffix", _RULE_EI),
    Word("Brauerei",     "brewery",       "die", "-ei", "suffix", _RULE_EI),
    Word("Molkerei",     "dairy",         "die", "-ei", "suffix", _RULE_EI),
    Word("Gerberei",     "tannery",       "die", "-ei", "suffix", _RULE_EI),
    Word("Polizei",      "police",        "die", "-ei", "suffix", _RULE_EI),
    Word("Fleischerei",  "butcher's",     "die", "-ei", "suffix", _RULE_EI),
    Word("Schusterei",   "cobbler's",     "die", "-ei", "suffix", _RULE_EI),
    Word("Schlosserei",  "locksmith's",   "die", "-ei", "suffix", _RULE_EI),
    Word("Türkei",       "Turkey",        "die", "-ei", "suffix", _RULE_EI),

    # -----------------------------------------------------------------------
    # SUFFIX: -e  (die, weak)  — feminine entries only
    # -----------------------------------------------------------------------
    Word("Straße",   "street",   "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Brücke",   "bridge",   "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Schule",   "school",   "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Grenze",   "border",   "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Sonne",    "sun",      "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Farbe",    "colour",   "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Seite",    "page",     "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Stimme",   "voice",    "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Woche",    "week",     "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Reise",    "journey",  "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Liebe",    "love",     "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Sprache",  "language", "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Stunde",   "hour",     "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Frage",    "question", "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Blume",    "flower",   "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Lampe",    "lamp",     "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Tasche",   "bag",      "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Kirche",   "church",   "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Flasche",  "bottle",   "die", "-e", "suffix", _RULE_E, weak=True),
    Word("Wiese",    "meadow",   "die", "-e", "suffix", _RULE_E, weak=True),

    # -----------------------------------------------------------------------
    # SUFFIX: -chen  (das)
    # -----------------------------------------------------------------------
    Word("Mädchen",   "girl",            "das", "-chen", "suffix", _RULE_CHEN),
    Word("Märchen",   "fairy tale",      "das", "-chen", "suffix", _RULE_CHEN),
    Word("Brötchen",  "bread roll",      "das", "-chen", "suffix", _RULE_CHEN),
    Word("Häuschen",  "little house",    "das", "-chen", "suffix", _RULE_CHEN),
    Word("Kätzchen",  "kitten",          "das", "-chen", "suffix", _RULE_CHEN),
    Word("Hündchen",  "puppy",           "das", "-chen", "suffix", _RULE_CHEN),
    Word("Vögelchen", "little bird",     "das", "-chen", "suffix", _RULE_CHEN),
    Word("Kindchen",  "little child",    "das", "-chen", "suffix", _RULE_CHEN),
    Word("Blümchen",  "little flower",   "das", "-chen", "suffix", _RULE_CHEN),
    Word("Städtchen", "small town",      "das", "-chen", "suffix", _RULE_CHEN),
    Word("Tischchen", "little table",    "das", "-chen", "suffix", _RULE_CHEN),
    Word("Bettchen",  "little bed",      "das", "-chen", "suffix", _RULE_CHEN),
    Word("Köpfchen",  "little head",     "das", "-chen", "suffix", _RULE_CHEN),
    Word("Gläschen",  "little glass",    "das", "-chen", "suffix", _RULE_CHEN),
    Word("Päckchen",  "little package",  "das", "-chen", "suffix", _RULE_CHEN),
    Word("Stückchen", "little piece",    "das", "-chen", "suffix", _RULE_CHEN),
    Word("Bisschen",  "little bit",      "das", "-chen", "suffix", _RULE_CHEN),
    Word("Säckchen",  "little bag",      "das", "-chen", "suffix", _RULE_CHEN),
    Word("Fläschchen","little bottle",   "das", "-chen", "suffix", _RULE_CHEN),
    Word("Bänkchen",  "little bench",    "das", "-chen", "suffix", _RULE_CHEN),

    # -----------------------------------------------------------------------
    # SUFFIX: -lein  (das)
    # -----------------------------------------------------------------------
    Word("Fräulein",  "young lady",    "das", "-lein", "suffix", _RULE_LEIN),
    Word("Bächlein",  "little brook",  "das", "-lein", "suffix", _RULE_LEIN),
    Word("Bäumlein",  "little tree",   "das", "-lein", "suffix", _RULE_LEIN),
    Word("Fischlein", "little fish",   "das", "-lein", "suffix", _RULE_LEIN),
    Word("Vöglein",   "little bird",   "das", "-lein", "suffix", _RULE_LEIN),
    Word("Blümlein",  "little flower", "das", "-lein", "suffix", _RULE_LEIN),
    Word("Röslein",   "little rose",   "das", "-lein", "suffix", _RULE_LEIN),
    Word("Dörflein",  "little village","das", "-lein", "suffix", _RULE_LEIN),
    Word("Kindlein",  "little child",  "das", "-lein", "suffix", _RULE_LEIN),
    Word("Häuslein",  "little house",  "das", "-lein", "suffix", _RULE_LEIN),
    Word("Büchlein",  "little book",   "das", "-lein", "suffix", _RULE_LEIN),
    Word("Gärtlein",  "little garden", "das", "-lein", "suffix", _RULE_LEIN),
    Word("Tüchlein",  "little cloth",  "das", "-lein", "suffix", _RULE_LEIN),
    Word("Herzlein",  "little heart",  "das", "-lein", "suffix", _RULE_LEIN),
    Word("Männlein",  "little man",    "das", "-lein", "suffix", _RULE_LEIN),

    # -----------------------------------------------------------------------
    # SUFFIX: -ment  (das)
    # -----------------------------------------------------------------------
    Word("Element",     "element",     "das", "-ment", "suffix", _RULE_MENT),
    Word("Dokument",    "document",    "das", "-ment", "suffix", _RULE_MENT),
    Word("Parlament",   "parliament",  "das", "-ment", "suffix", _RULE_MENT),
    Word("Experiment",  "experiment",  "das", "-ment", "suffix", _RULE_MENT),
    Word("Argument",    "argument",    "das", "-ment", "suffix", _RULE_MENT),
    Word("Instrument",  "instrument",  "das", "-ment", "suffix", _RULE_MENT),
    Word("Fundament",   "foundation",  "das", "-ment", "suffix", _RULE_MENT),
    Word("Medikament",  "medication",  "das", "-ment", "suffix", _RULE_MENT),
    Word("Monument",    "monument",    "das", "-ment", "suffix", _RULE_MENT),
    Word("Regiment",    "regiment",    "das", "-ment", "suffix", _RULE_MENT),
    Word("Testament",   "will",        "das", "-ment", "suffix", _RULE_MENT),
    Word("Segment",     "segment",     "das", "-ment", "suffix", _RULE_MENT),
    Word("Fragment",    "fragment",    "das", "-ment", "suffix", _RULE_MENT),
    Word("Temperament", "temperament", "das", "-ment", "suffix", _RULE_MENT),
    Word("Engagement",  "engagement",  "das", "-ment", "suffix", _RULE_MENT),

    # -----------------------------------------------------------------------
    # SUFFIX: -um  (das)
    # -----------------------------------------------------------------------
    Word("Museum",      "museum",         "das", "-um", "suffix", _RULE_UM),
    Word("Publikum",    "audience",       "das", "-um", "suffix", _RULE_UM),
    Word("Zentrum",     "centre",         "das", "-um", "suffix", _RULE_UM),
    Word("Album",       "album",          "das", "-um", "suffix", _RULE_UM),
    Word("Forum",       "forum",          "das", "-um", "suffix", _RULE_UM),
    Word("Datum",       "date",           "das", "-um", "suffix", _RULE_UM),
    Word("Gymnasium",   "grammar school", "das", "-um", "suffix", _RULE_UM),
    Word("Aquarium",    "aquarium",       "das", "-um", "suffix", _RULE_UM),
    Word("Auditorium",  "auditorium",     "das", "-um", "suffix", _RULE_UM),
    Word("Podium",      "podium",         "das", "-um", "suffix", _RULE_UM),
    Word("Medium",      "medium",         "das", "-um", "suffix", _RULE_UM),
    Word("Stadium",     "stadium",        "das", "-um", "suffix", _RULE_UM),
    Word("Atrium",      "atrium",         "das", "-um", "suffix", _RULE_UM),
    Word("Imperium",    "empire",         "das", "-um", "suffix", _RULE_UM),
    Word("Spektrum",    "spectrum",       "das", "-um", "suffix", _RULE_UM),
    Word("Ultimatum",   "ultimatum",      "das", "-um", "suffix", _RULE_UM),
    Word("Curriculum",  "curriculum",     "das", "-um", "suffix", _RULE_UM),
    Word("Referendum",  "referendum",     "das", "-um", "suffix", _RULE_UM),
    Word("Individuum",  "individual",     "das", "-um", "suffix", _RULE_UM),
    Word("Faktum",      "fact",           "das", "-um", "suffix", _RULE_UM),

    # -----------------------------------------------------------------------
    # SUFFIX: -ma  (das, Greek-origin)
    # -----------------------------------------------------------------------
    Word("Thema",      "topic",     "das", "-ma", "suffix", _RULE_MA),
    Word("Drama",      "drama",     "das", "-ma", "suffix", _RULE_MA),
    Word("Trauma",     "trauma",    "das", "-ma", "suffix", _RULE_MA),
    Word("Schema",     "pattern",   "das", "-ma", "suffix", _RULE_MA),
    Word("Koma",       "coma",      "das", "-ma", "suffix", _RULE_MA),
    Word("Dogma",      "dogma",     "das", "-ma", "suffix", _RULE_MA),
    Word("Klima",      "climate",   "das", "-ma", "suffix", _RULE_MA),
    Word("Komma",      "comma",     "das", "-ma", "suffix", _RULE_MA),
    Word("Plasma",     "plasma",    "das", "-ma", "suffix", _RULE_MA),
    Word("Stigma",     "stigma",    "das", "-ma", "suffix", _RULE_MA),
    Word("Aroma",      "aroma",     "das", "-ma", "suffix", _RULE_MA),
    Word("Dilemma",    "dilemma",   "das", "-ma", "suffix", _RULE_MA),
    Word("Panorama",   "panorama",  "das", "-ma", "suffix", _RULE_MA),
    Word("Prisma",     "prism",     "das", "-ma", "suffix", _RULE_MA),
    Word("Paradigma",  "paradigm",  "das", "-ma", "suffix", _RULE_MA),

    # -----------------------------------------------------------------------
    # SUFFIX: -tum  (das)
    # -----------------------------------------------------------------------
    Word("Eigentum",    "property",          "das", "-tum", "suffix", _RULE_TUM),
    Word("Wachstum",    "growth",            "das", "-tum", "suffix", _RULE_TUM),
    Word("Christentum", "Christianity",      "das", "-tum", "suffix", _RULE_TUM),
    Word("Judentum",    "Judaism",           "das", "-tum", "suffix", _RULE_TUM),
    Word("Altertum",    "antiquity",         "das", "-tum", "suffix", _RULE_TUM),
    Word("Bürgertum",   "bourgeoisie",       "das", "-tum", "suffix", _RULE_TUM),
    Word("Heiligtum",   "sanctuary",         "das", "-tum", "suffix", _RULE_TUM),
    Word("Herzogtum",   "duchy",             "das", "-tum", "suffix", _RULE_TUM),
    Word("Fürstentum",  "principality",      "das", "-tum", "suffix", _RULE_TUM),
    Word("Brauchtum",   "custom",            "das", "-tum", "suffix", _RULE_TUM),
    Word("Volkstum",    "national character","das", "-tum", "suffix", _RULE_TUM),
    Word("Kaisertum",   "imperial rule",     "das", "-tum", "suffix", _RULE_TUM),

    # -----------------------------------------------------------------------
    # SUFFIX: -nis  (das, weak) — neuter entries only
    # -----------------------------------------------------------------------
    Word("Ergebnis",    "result",        "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Zeugnis",     "certificate",   "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Geheimnis",   "secret",        "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Gedächtnis",  "memory",        "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Verständnis", "understanding", "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Gefängnis",   "prison",        "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Hindernis",   "obstacle",      "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Gleichnis",   "parable",       "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Bildnis",     "portrait",      "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Verhältnis",  "ratio",         "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Bedürfnis",   "need",          "das", "-nis", "suffix", _RULE_NIS, weak=True),
    Word("Ereignis",    "event",         "das", "-nis", "suffix", _RULE_NIS, weak=True),

    # -----------------------------------------------------------------------
    # SEMANTIC: days/months/seasons  (der)
    # -----------------------------------------------------------------------
    Word("Montag",     "Monday",    "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Dienstag",   "Tuesday",   "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Mittwoch",   "Wednesday", "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Donnerstag", "Thursday",  "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Freitag",    "Friday",    "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Samstag",    "Saturday",  "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Sonntag",    "Sunday",    "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Januar",     "January",   "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Februar",    "February",  "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("März",       "March",     "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("April",      "April",     "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Mai",        "May",       "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Juni",       "June",      "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Juli",       "July",      "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("August",     "August",    "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("September",  "September", "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Oktober",    "October",   "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("November",   "November",  "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Dezember",   "December",  "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Sommer",     "summer",    "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Herbst",     "autumn",    "der", "days/months/seasons", "semantic", _RULE_DAYS),
    Word("Winter",     "winter",    "der", "days/months/seasons", "semantic", _RULE_DAYS),
    # Note: Frühling is already listed under -ling suffix; duplicate avoided —
    # the suffix entry takes precedence. Seasons needing a separate entry:
    # Frühling would duplicate — handled as a note in rule only.

    # -----------------------------------------------------------------------
    # SEMANTIC: weather  (der)
    # -----------------------------------------------------------------------
    Word("Regen",        "rain",       "der", "weather", "semantic", _RULE_WEATHER),
    Word("Schnee",       "snow",       "der", "weather", "semantic", _RULE_WEATHER),
    Word("Wind",         "wind",       "der", "weather", "semantic", _RULE_WEATHER),
    Word("Sturm",        "storm",      "der", "weather", "semantic", _RULE_WEATHER),
    Word("Nebel",        "fog",        "der", "weather", "semantic", _RULE_WEATHER),
    Word("Frost",        "frost",      "der", "weather", "semantic", _RULE_WEATHER),
    Word("Hagel",        "hail",       "der", "weather", "semantic", _RULE_WEATHER),
    Word("Blitz",        "lightning",  "der", "weather", "semantic", _RULE_WEATHER),
    Word("Donner",       "thunder",    "der", "weather", "semantic", _RULE_WEATHER),
    Word("Sonnenschein", "sunshine",   "der", "weather", "semantic", _RULE_WEATHER),
    Word("Himmel",       "sky",        "der", "weather", "semantic", _RULE_WEATHER),
    Word("Tau",          "dew",        "der", "weather", "semantic", _RULE_WEATHER),
    Word("Wirbelsturm",  "tornado",    "der", "weather", "semantic", _RULE_WEATHER),
    Word("Orkan",        "hurricane",  "der", "weather", "semantic", _RULE_WEATHER),
    Word("Monsun",       "monsoon",    "der", "weather", "semantic", _RULE_WEATHER),

    # -----------------------------------------------------------------------
    # SEMANTIC: alcoholic drinks  (der)
    # -----------------------------------------------------------------------
    Word("Wein",       "wine",            "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Whiskey",    "whisky",          "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Rum",        "rum",             "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Schnaps",    "schnapps",        "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Sekt",       "sparkling wine",  "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Wodka",      "vodka",           "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Gin",        "gin",             "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Brandy",     "brandy",          "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Likör",      "liqueur",         "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Champagner", "champagne",       "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Prosecco",   "prosecco",        "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Rotwein",    "red wine",        "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Weißwein",   "white wine",      "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Cognac",     "cognac",          "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),
    Word("Portwein",   "port wine",       "der", "alcoholic drinks", "semantic", _RULE_ALCOHOL),

    # -----------------------------------------------------------------------
    # SEMANTIC: car brands  (der)
    # -----------------------------------------------------------------------
    Word("BMW",        "BMW",        "der", "car brands", "semantic", _RULE_CARS),
    Word("Mercedes",   "Mercedes",   "der", "car brands", "semantic", _RULE_CARS),
    Word("Audi",       "Audi",       "der", "car brands", "semantic", _RULE_CARS),
    Word("Volkswagen", "Volkswagen", "der", "car brands", "semantic", _RULE_CARS),
    Word("Opel",       "Opel",       "der", "car brands", "semantic", _RULE_CARS),
    Word("Porsche",    "Porsche",    "der", "car brands", "semantic", _RULE_CARS),
    Word("Ferrari",    "Ferrari",    "der", "car brands", "semantic", _RULE_CARS),
    Word("Ford",       "Ford",       "der", "car brands", "semantic", _RULE_CARS),
    Word("Toyota",     "Toyota",     "der", "car brands", "semantic", _RULE_CARS),
    Word("Renault",    "Renault",    "der", "car brands", "semantic", _RULE_CARS),

    # -----------------------------------------------------------------------
    # SEMANTIC: trees and flowers  (die)
    # -----------------------------------------------------------------------
    Word("Eiche",         "oak",            "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Birke",         "birch",          "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Kiefer",        "pine",           "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Buche",         "beech",          "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Linde",         "linden",         "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Weide",         "willow",         "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Tanne",         "fir",            "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Pappel",        "poplar",         "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Rose",          "rose",           "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Tulpe",         "tulip",          "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Lilie",         "lily",           "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Orchidee",      "orchid",         "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Sonnenblume",   "sunflower",      "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Nelke",         "carnation",      "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Dahlie",        "dahlia",         "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Chrysantheme",  "chrysanthemum",  "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Aster",         "aster",          "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Iris",          "iris",           "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Hyazinthe",     "hyacinth",       "die", "trees and flowers", "semantic", _RULE_TREES),
    Word("Primel",        "primrose",       "die", "trees and flowers", "semantic", _RULE_TREES),

    # -----------------------------------------------------------------------
    # SEMANTIC: fruits  (die)
    # -----------------------------------------------------------------------
    Word("Banane",     "banana",      "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Orange",     "orange",      "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Kirsche",    "cherry",      "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Pflaume",    "plum",        "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Mango",      "mango",       "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Ananas",     "pineapple",   "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Kiwi",       "kiwi",        "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Erdbeere",   "strawberry",  "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Himbeere",   "raspberry",   "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Brombeere",  "blackberry",  "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Weintraube", "grape",       "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Melone",     "melon",       "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Papaya",     "papaya",      "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Birne",      "pear",        "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Quitte",     "quince",      "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Avocado",    "avocado",     "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Limette",    "lime",        "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Mandarine",  "mandarin",    "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Feige",      "fig",         "die", "fruits", "semantic", _RULE_FRUITS),
    Word("Dattel",     "date",        "die", "fruits", "semantic", _RULE_FRUITS),

    # -----------------------------------------------------------------------
    # SEMANTIC: European rivers  (die)
    # -----------------------------------------------------------------------
    Word("Donau",   "Danube",   "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Elbe",    "Elbe",     "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Oder",    "Oder",     "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Weser",   "Weser",    "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Saale",   "Saale",    "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Mosel",   "Moselle",  "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Isar",    "Isar",     "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Spree",   "Spree",    "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Themse",  "Thames",   "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Seine",   "Seine",    "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Wolga",   "Volga",    "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Maas",    "Meuse",    "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Rhône",   "Rhône",    "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Loire",   "Loire",    "die", "European rivers", "semantic", _RULE_RIVERS),
    Word("Pegnitz", "Pegnitz",  "die", "European rivers", "semantic", _RULE_RIVERS),

    # -----------------------------------------------------------------------
    # SEMANTIC: numbers and numerals  (die)
    # -----------------------------------------------------------------------
    Word("Eins",      "one",     "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Zwei",      "two",     "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Drei",      "three",   "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Vier",      "four",    "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Fünf",      "five",    "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Sechs",     "six",     "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Sieben",    "seven",   "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Acht",      "eight",   "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Neun",      "nine",    "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Zehn",      "ten",     "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Million",   "million", "die", "numbers and numerals", "semantic", _RULE_NUMBERS),
    Word("Milliarde", "billion", "die", "numbers and numerals", "semantic", _RULE_NUMBERS),

    # -----------------------------------------------------------------------
    # SEMANTIC: metals  (das)
    # -----------------------------------------------------------------------
    Word("Gold",       "gold",       "das", "metals", "semantic", _RULE_METALS),
    Word("Silber",     "silver",     "das", "metals", "semantic", _RULE_METALS),
    Word("Eisen",      "iron",       "das", "metals", "semantic", _RULE_METALS),
    Word("Kupfer",     "copper",     "das", "metals", "semantic", _RULE_METALS),
    Word("Aluminium",  "aluminium",  "das", "metals", "semantic", _RULE_METALS),
    Word("Zink",       "zinc",       "das", "metals", "semantic", _RULE_METALS),
    Word("Titan",      "titanium",   "das", "metals", "semantic", _RULE_METALS),
    Word("Nickel",     "nickel",     "das", "metals", "semantic", _RULE_METALS),
    Word("Chrom",      "chromium",   "das", "metals", "semantic", _RULE_METALS),
    Word("Zinn",       "tin",        "das", "metals", "semantic", _RULE_METALS),
    Word("Blei",       "lead",       "das", "metals", "semantic", _RULE_METALS),
    Word("Platin",     "platinum",   "das", "metals", "semantic", _RULE_METALS),
    Word("Kobalt",     "cobalt",     "das", "metals", "semantic", _RULE_METALS),
    Word("Messing",    "brass",      "das", "metals", "semantic", _RULE_METALS),

    # -----------------------------------------------------------------------
    # SEMANTIC: venues  (das)
    # -----------------------------------------------------------------------
    Word("Hotel",       "hotel",           "das", "venues", "semantic", _RULE_VENUES),
    Word("Café",        "café",            "das", "venues", "semantic", _RULE_VENUES),
    Word("Theater",     "theatre",         "das", "venues", "semantic", _RULE_VENUES),
    Word("Restaurant",  "restaurant",      "das", "venues", "semantic", _RULE_VENUES),
    Word("Casino",      "casino",          "das", "venues", "semantic", _RULE_VENUES),
    Word("Kino",        "cinema",          "das", "venues", "semantic", _RULE_VENUES),
    Word("Stadion",     "stadium",         "das", "venues", "semantic", _RULE_VENUES),
    Word("Rathaus",     "town hall",       "das", "venues", "semantic", _RULE_VENUES),
    Word("Krankenhaus", "hospital",        "das", "venues", "semantic", _RULE_VENUES),
    Word("Schwimmbad",  "swimming pool",   "das", "venues", "semantic", _RULE_VENUES),

    # -----------------------------------------------------------------------
    # SEMANTIC: languages  (das)
    # -----------------------------------------------------------------------
    Word("Deutsch",       "German",      "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Englisch",      "English",     "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Französisch",   "French",      "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Spanisch",      "Spanish",     "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Italienisch",   "Italian",     "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Portugiesisch", "Portuguese",  "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Russisch",      "Russian",     "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Chinesisch",    "Chinese",     "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Japanisch",     "Japanese",    "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Arabisch",      "Arabic",      "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Koreanisch",    "Korean",      "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Niederländisch","Dutch",       "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Schwedisch",    "Swedish",     "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Polnisch",      "Polish",      "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Türkisch",      "Turkish",     "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Griechisch",    "Greek",       "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Hebräisch",     "Hebrew",      "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Latein",        "Latin",       "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Hindi",         "Hindi",       "das", "languages", "semantic", _RULE_LANGUAGES),
    Word("Persisch",      "Persian",     "das", "languages", "semantic", _RULE_LANGUAGES),

    # -----------------------------------------------------------------------
    # SEMANTIC: verbal nouns (infinitives-as-nouns)  (das)
    # -----------------------------------------------------------------------
    Word("Essen",    "eating",      "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Schwimmen","swimming",    "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Lesen",    "reading",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Schreiben","writing",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Laufen",   "running",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Lernen",   "learning",    "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Sprechen", "speaking",    "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Kochen",   "cooking",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Tanzen",   "dancing",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Singen",   "singing",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Schlafen", "sleeping",    "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Trinken",  "drinking",    "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Arbeiten", "working",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Reisen",   "travelling",  "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Fahren",   "driving",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Spielen",  "playing",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Wandern",  "hiking",      "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Denken",   "thinking",    "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Fühlen",   "feeling",     "das", "verbal nouns", "semantic", _RULE_VERBAL),
    Word("Leben",    "living",      "das", "verbal nouns", "semantic", _RULE_VERBAL),

    # -----------------------------------------------------------------------
    # SEMANTIC: Ge- prefix  (das)
    # -----------------------------------------------------------------------
    Word("Gespräch",  "conversation",   "das", "Ge-", "semantic", _RULE_GE),
    Word("Gebäude",   "building",       "das", "Ge-", "semantic", _RULE_GE),
    Word("Gebirge",   "mountain range", "das", "Ge-", "semantic", _RULE_GE),
    Word("Gefühl",    "feeling",        "das", "Ge-", "semantic", _RULE_GE),
    Word("Gesicht",   "face",           "das", "Ge-", "semantic", _RULE_GE),
    Word("Geschäft",  "shop",           "das", "Ge-", "semantic", _RULE_GE),
    Word("Gedicht",   "poem",           "das", "Ge-", "semantic", _RULE_GE),
    Word("Gehalt",    "salary",         "das", "Ge-", "semantic", _RULE_GE),
    Word("Gemüse",    "vegetables",     "das", "Ge-", "semantic", _RULE_GE),
    Word("Geschenk",  "gift",           "das", "Ge-", "semantic", _RULE_GE),
    Word("Gewicht",   "weight",         "das", "Ge-", "semantic", _RULE_GE),
    Word("Gericht",   "court/dish",     "das", "Ge-", "semantic", _RULE_GE),
    Word("Gerät",     "device",         "das", "Ge-", "semantic", _RULE_GE),
    Word("Geländer",  "railing",        "das", "Ge-", "semantic", _RULE_GE),
    Word("Gepäck",    "luggage",        "das", "Ge-", "semantic", _RULE_GE),
    Word("Getränk",   "beverage",       "das", "Ge-", "semantic", _RULE_GE),
    Word("Gesetz",    "law",            "das", "Ge-", "semantic", _RULE_GE),
    Word("Gemälde",   "painting",       "das", "Ge-", "semantic", _RULE_GE),
    Word("Gehirn",    "brain",          "das", "Ge-", "semantic", _RULE_GE),
    Word("Geräusch",  "noise",          "das", "Ge-", "semantic", _RULE_GE),

    # -----------------------------------------------------------------------
    # SEMANTIC: young people and animals  (das)
    # -----------------------------------------------------------------------
    Word("Kind",        "child",            "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Baby",        "baby",             "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Küken",       "chick",            "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Lamm",        "lamb",             "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Kalb",        "calf",             "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Fohlen",      "foal",             "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Ferkel",      "piglet",           "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Kitz",        "fawn",             "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Kleinkind",   "toddler",          "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Neugeborenes","newborn",          "das", "young people and animals", "semantic", _RULE_YOUNG),
    Word("Jungtier",    "juvenile animal",  "das", "young people and animals", "semantic", _RULE_YOUNG),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_words(
    gender: str | None = None,
    category_type: str | None = None,
    category: str | None = None,
) -> list[Word]:
    """Return words matching all supplied filters (AND logic).

    Parameters
    ----------
    gender:
        One of ``"der"``, ``"die"``, ``"das"``; ``None`` means no filter.
    category_type:
        ``"suffix"`` or ``"semantic"``; ``None`` means no filter.
    category:
        Exact category string, e.g. ``"-heit"`` or ``"weather"``; ``None``
        means no filter.

    Returns
    -------
    list[Word]
        Filtered subset of :data:`WORDS`.
    """
    result = WORDS
    if gender is not None:
        result = [w for w in result if w.gender == gender]
    if category_type is not None:
        result = [w for w in result if w.category_type == category_type]
    if category is not None:
        result = [w for w in result if w.category == category]
    return result


def list_categories() -> dict[str, list[str]]:
    """Return a mapping of gender -> sorted list of unique category names.

    Returns
    -------
    dict[str, list[str]]
        Keys are ``"der"``, ``"die"``, ``"das"``; values are sorted category
        name lists (deduplicated).
    """
    result: dict[str, list[str]] = {"der": [], "die": [], "das": []}
    seen: dict[str, set[str]] = {"der": set(), "die": set(), "das": set()}
    for word in WORDS:
        if word.category not in seen[word.gender]:
            seen[word.gender].add(word.category)
            result[word.gender].append(word.category)
    for gender in result:
        result[gender].sort()
    return result


def validate_words() -> list[str]:
    """Run basic consistency checks on :data:`WORDS`.

    Checks performed:

    * For suffix categories: the German word must actually end with the
      suffix (stripping the leading ``"-"``).
    * No duplicate ``german`` values in the list.
    * ``gender`` is one of ``"der"``, ``"die"``, ``"das"``.
    * ``category_type`` is ``"suffix"`` or ``"semantic"``.

    Returns
    -------
    list[str]
        Human-readable issue descriptions; empty list means no issues found.
    """
    issues: list[str] = []
    valid_genders = {"der", "die", "das"}
    valid_types = {"suffix", "semantic"}

    seen_german: dict[str, int] = {}
    for idx, word in enumerate(WORDS):
        # Gender check
        if word.gender not in valid_genders:
            issues.append(
                f"[{idx}] '{word.german}': invalid gender '{word.gender}'"
            )

        # Category type check
        if word.category_type not in valid_types:
            issues.append(
                f"[{idx}] '{word.german}': invalid category_type "
                f"'{word.category_type}'"
            )

        # Suffix ending check
        if word.category_type == "suffix":
            suffix_raw = word.category.lstrip("-")
            if not word.german.lower().endswith(suffix_raw.lower()):
                issues.append(
                    f"[{idx}] '{word.german}' (category '{word.category}'): "
                    f"word does not end with '{suffix_raw}'"
                )

        # Duplicate check
        lower_german = word.german.lower()
        if lower_german in seen_german:
            issues.append(
                f"[{idx}] '{word.german}': duplicate of entry "
                f"[{seen_german[lower_german]}]"
            )
        else:
            seen_german[lower_german] = idx

    return issues


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    issues = validate_words()
    cats = list_categories()
    total = len(WORDS)
    suffix_count = len([w for w in WORDS if w.category_type == "suffix"])
    semantic_count = len([w for w in WORDS if w.category_type == "semantic"])
    print(f"Total words: {total} ({suffix_count} suffix, {semantic_count} semantic)")
    for gender in ("der", "die", "das"):
        gwords = [w for w in WORDS if w.gender == gender]
        print(f"  {gender}: {len(gwords)} words")
    print("\nCategories:")
    for gender, cats_list in cats.items():
        print(f"  {gender}: {', '.join(cats_list)}")
    if issues:
        print(f"\n\u26a0 {len(issues)} validation issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n\u2713 Validation: 0 issues found.")
