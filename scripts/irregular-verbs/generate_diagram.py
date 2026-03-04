#!/usr/bin/env python3
"""Generate an SVG diagram clustering verbs around their mnemonic groups."""

import math
from pathlib import Path
from german_common import parse_markdown, MNEMONIC_PATTERNS

# Hex colors for SVG (matching the ANSI terminal colors)
MNEMONIC_HEX = {
    "inka":     {"bg": "#B22222", "fg": "#FFFFFF", "light": "#F5D0D0", "line": "#D45C5C"},
    "barrel":   {"bg": "#228B22", "fg": "#FFFFFF", "light": "#D0F0D0", "line": "#5CB85C"},
    "saudi":    {"bg": "#DAA520", "fg": "#FFFFFF", "light": "#FFF3D0", "line": "#E8C84A"},
    "usa":      {"bg": "#1E5AA8", "fg": "#FFFFFF", "light": "#D0E0F5", "line": "#5B8FD0"},
    "lasso":    {"bg": "#D2691E", "fg": "#FFFFFF", "light": "#F5E0D0", "line": "#E09050"},
    "polo":     {"bg": "#008080", "fg": "#FFFFFF", "light": "#D0F0F0", "line": "#40B0B0"},
    "wind":     {"bg": "#4682B4", "fg": "#FFFFFF", "light": "#D8E8F5", "line": "#78AAD0"},
    "anaconda": {"bg": "#800080", "fg": "#FFFFFF", "light": "#F0D0F0", "line": "#B050B0"},
}


def generate_cluster_svg(verbs_by_mnemonic: dict) -> str:
    """Generate SVG with verb clusters around each mnemonic."""

    # Layout: 4x2 grid of clusters
    grid = [
        ["inka", "barrel", "saudi", "usa"],
        ["lasso", "polo", "wind", "anaconda"],
    ]

    cell_w = 420
    cell_h = 520
    margin = 30
    canvas_w = cell_w * 4 + margin * 2
    canvas_h = cell_h * 2 + margin * 2 + 80  # extra for title

    svg_parts = []

    # SVG header
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w} {canvas_h}" width="{canvas_w}" height="{canvas_h}">
<defs>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&amp;display=swap');
    text {{ font-family: 'Inter', 'Segoe UI', Arial, sans-serif; }}
    .title {{ font-size: 28px; font-weight: 700; fill: #1a1a2e; }}
    .subtitle {{ font-size: 14px; fill: #666; }}
    .mnemonic-name {{ font-size: 18px; font-weight: 700; }}
    .mnemonic-pattern {{ font-size: 11px; font-weight: 600; }}
    .verb-text {{ font-size: 11px; font-weight: 600; fill: #2a2a3e; }}
    .verb-english {{ font-size: 9px; fill: #888; }}
    .verb-forms {{ font-size: 9px; fill: #555; font-style: italic; }}
    .freq-star {{ font-size: 9px; }}
  </style>
  <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
    <feDropShadow dx="1" dy="2" stdDeviation="3" flood-opacity="0.15"/>
  </filter>
</defs>

<!-- Background -->
<rect width="{canvas_w}" height="{canvas_h}" fill="#FAFBFE" rx="12"/>
''')

    # Title
    svg_parts.append(f'''<text x="{canvas_w/2}" y="40" text-anchor="middle" class="title">German Irregular Verbs — Mnemonic Clusters</text>
<text x="{canvas_w/2}" y="62" text-anchor="middle" class="subtitle">81 verbs organized by vowel-change pattern · Verbs radiate from their mnemonic hub</text>
''')

    title_offset = 80

    for row_idx, row in enumerate(grid):
        for col_idx, mnemonic in enumerate(row):
            if mnemonic not in verbs_by_mnemonic:
                continue

            verbs = verbs_by_mnemonic[mnemonic]
            colors = MNEMONIC_HEX[mnemonic]
            pattern = MNEMONIC_PATTERNS[mnemonic]

            # Center of this cell
            cx = margin + col_idx * cell_w + cell_w / 2
            cy = title_offset + margin + row_idx * cell_h + cell_h / 2

            n = len(verbs)

            # Adaptive radius based on verb count
            if n <= 7:
                radius = 140
            elif n <= 10:
                radius = 155
            elif n <= 14:
                radius = 170
            else:
                radius = 190

            hub_r = 38

            # Light background circle for the cluster
            svg_parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius + 45}" '
                f'fill="{colors["light"]}" opacity="0.4"/>'
            )

            # Draw connection lines and verb nodes
            for i, verb in enumerate(verbs):
                angle = (2 * math.pi * i / n) - math.pi / 2
                vx = cx + radius * math.cos(angle)
                vy = cy + radius * math.sin(angle)

                # Connection line
                svg_parts.append(
                    f'<line x1="{cx}" y1="{cy}" x2="{vx}" y2="{vy}" '
                    f'stroke="{colors["line"]}" stroke-width="1.5" opacity="0.5"/>'
                )

                # Verb bubble
                bubble_w = 72
                bubble_h = 42
                svg_parts.append(
                    f'<rect x="{vx - bubble_w/2}" y="{vy - bubble_h/2}" '
                    f'width="{bubble_w}" height="{bubble_h}" rx="8" '
                    f'fill="white" stroke="{colors["line"]}" stroke-width="1.2" '
                    f'filter="url(#shadow)"/>'
                )

                # Frequency indicator
                freq = verb.frequency
                stars = "★" * freq + "☆" * (3 - freq)
                star_color = "#DAA520" if freq >= 2 else "#CCC"

                # Verb name
                svg_parts.append(
                    f'<text x="{vx}" y="{vy - 8}" text-anchor="middle" '
                    f'class="verb-text">{verb.infinitive}</text>'
                )
                # English + forms
                svg_parts.append(
                    f'<text x="{vx}" y="{vy + 4}" text-anchor="middle" '
                    f'class="verb-english">{verb.english}</text>'
                )
                svg_parts.append(
                    f'<text x="{vx}" y="{vy + 15}" text-anchor="middle" '
                    f'class="verb-forms">{verb.praeteritum} · {verb.perfect}</text>'
                )

            # Central hub
            svg_parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{hub_r}" '
                f'fill="{colors["bg"]}" filter="url(#shadow)"/>'
            )
            svg_parts.append(
                f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" '
                f'class="mnemonic-name" fill="{colors["fg"]}">'
                f'{mnemonic.upper()}</text>'
            )
            svg_parts.append(
                f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" '
                f'class="mnemonic-pattern" fill="{colors["fg"]}" opacity="0.85">'
                f'{pattern}</text>'
            )

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


def main():
    script_dir = Path(__file__).parent
    md_file = script_dir / "irregular-perfect.md"
    output_file = script_dir / "verb-clusters.svg"

    verbs = parse_markdown(md_file)
    print(f"Parsed {len(verbs)} verbs")

    # Group by mnemonic
    verbs_by_mnemonic: dict[str, list] = {}
    for v in verbs:
        verbs_by_mnemonic.setdefault(v.mnemonic, []).append(v)

    for mnemonic, group in verbs_by_mnemonic.items():
        print(f"  {mnemonic.upper():10} : {len(group)} verbs")

    svg = generate_cluster_svg(verbs_by_mnemonic)
    output_file.write_text(svg, encoding='utf-8')
    print(f"\nDiagram saved to {output_file}")


if __name__ == "__main__":
    main()
