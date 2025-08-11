#!/usr/bin/env python3
"""
Render 10 side-by-side $1M thermometers as an SVG.

- Tracks capital commitments toward a $10M goal.
- Each thermometer = $1,000,000.
- White interior by default; solid red fill grows upward as funding increases.
- Rounded bulb; outline has subtle inner shadow + glow.
- Major ticks $100k, minor ticks $50k.
- Title shows "<label> — Capital Commitments" and total committed / goal.
"""

import json, pathlib

DATA = pathlib.Path("data/funds.json")
OUT  = pathlib.Path("thermometer.svg")

COLS = 10
SEG_GOAL = 1_000_000
W, H = 1240, 420

# Bright red for the fill
FILL_COLOR = "#e02020"

def fmt_currency_full(n: int) -> str:
    return f"${n:,.0f}"

def build_ticks(bar_y: int, bar_h: int):
    """Return list of (value, y, is_major) for 0..$1M."""
    ticks = []
    majors = set()
    v = 0
    # Major every $100k
    while v <= SEG_GOAL:
        rel = v / SEG_GOAL
        y = bar_y + (bar_h - int(bar_h * rel))
        majors.add(v)
        ticks.append((v, y, True))
        v += 100_000
    # Minor every $50k (skip where a major already exists)
    v = 50_000
    while v < SEG_GOAL:
        if v not in majors:
            rel = v / SEG_GOAL
            y = bar_y + (bar_h - int(bar_h * rel))
            ticks.append((v, y, False))
        v += 50_000
    # Ensure top tick
    if all(val != SEG_GOAL for val, _, _ in ticks):
        ticks.append((SEG_GOAL, bar_y, True))
    return ticks

def main():
    d = json.loads(DATA.read_text())
    goal = int(d.get("goal", 10_000_000))
    currency = d.get("currency", "USD")
    label = d.get("label", "Fundraising")
    segments = d.get("segments", [0] * COLS)

    # Normalize to exactly COLS numbers, clamped to [0, SEG_GOAL]
    segs = [max(0, min(int(x), SEG_GOAL)) for x in segments]
    if len(segs) < COLS:
        segs += [0] * (COLS - len(segs))
    elif len(segs) > COLS:
        segs = segs[:COLS]

    total = sum(segs)
    pct_total = max(0.0, min(1.0, total / goal))

    # Layout
    pad_x = 24
    pad_y = 24
    title_y = pad_y + 8
    bar_w = 52
    gap = 20
    bulb_space = 56
    bar_h = H - pad_y * 2 - 70 - bulb_space
    bar_y = pad_y + 28

    total_cols_w = COLS * bar_w + (COLS - 1) * gap
    start_x = (W - total_cols_w) // 2

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    svg.append('<defs>')
    svg.append(
        '<style>'
        '.title{font:700 20px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}'
        '.label{font:600 13px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#222}'
        '.value{font:700 16px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}'
        '.tickMajor{stroke:#555}'
        '.tickMinor{stroke:#888}'
        '.tube{fill:none;stroke:#666;stroke-width:1.3}'
        '.segLbl{font:600 12px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#666}'
        '</style>'
    )
    # Subtle inner shadow + glow to make outline pop
    svg.append(
        '<filter id="tubeFX" x="-25%" y="-25%" width="150%" height="150%" color-interpolation-filters="sRGB">'
        '  <feGaussianBlur in="SourceAlpha" stdDeviation="1.0" result="blur"/>'
        '  <feOffset dy="0.5" result="offsetBlur"/>'
        '  <feComposite in="offsetBlur" in2="SourceAlpha" operator="arithmetic" k2="-1" k3="1" result="innerShadow"/>'
        '  <feColorMatrix in="innerShadow" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.30 0" result="innerShadowColor"/>'
        '  <feComposite in="SourceGraphic" in2="innerShadowColor" operator="over" result="withInner"/>'
        '  <feGaussianBlur in="withInner" stdDeviation="0.35" result="glow"/>'
        '  <feMerge><feMergeNode in="glow"/><feMergeNode in="withInner"/></feMerge>'
        '</filter>'
    )
    svg.append('</defs>')

    # Header
    svg.append(
        f'<text x="{pad_x}" y="{title_y}" class="title">{label} — Capital Commitments</text>'
    )
    svg.append(
        f'<text x="{W - pad_x}" y="{title_y}" class="value" text-anchor="end">'
        f'{fmt_currency_full(total)} / {fmt_currency_full(goal)} ({int(round(pct_total * 100))}%)'
        f'</text>'
    )

    # Columns
    for i, seg_val in enumerate(segs):
        bar_x = start_x + i * (bar_w + gap)
        pct = seg_val / SEG_GOAL

        # Geometry
        rect_x, rect_y, rect_w, rect_h = bar_x, bar_y, bar_w, bar_h
        bulb_r = bar_w * 0.65
        bulb_cx = bar_x + bar_w / 2
        bulb_cy = bar_y + bar_h + bulb_r * 0.55

        bulb_bottom = bulb_cy + bulb_r
        shape_top = bar_y
        shape_bottom = bulb_bottom
        shape_h = shape_bottom - shape_top

        # Level clip across the full tube+bulb height
        level_h = int(shape_h * pct)
        level_y = shape_bottom - level_h

        # IMPORTANT: Make level clip as wide as the bulb (bulb is wider than the tube)
        level_x = int(bulb_cx - bulb_r - 1)
        level_w = int(2 * bulb_r + 2)

        # Unified shape clip (tube + bulb)
        svg.append(
            f'<clipPath id="clipShape{i}" clipPathUnits="userSpaceOnUse">'
            f'  <rect x="{rect_x}" y="{rect_y}" rx="12" ry="12" width="{rect_w}" height="{rect_h}"/>'
            f'  <circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r}"/>'
            f'</clipPath>'
        )

        # 1) Base interior: white
        svg.append(
            f'<g clip-path="url(#clipShape{i})">'
            f'  <rect x="{rect_x}" y="{shape_top}" width="{rect_w}" height="{shape_h}" fill="#ffffff"/>'
            f'</g>'
        )

        # 2) Solid red fill revealed from bottom up (replaces white visually)
        svg.append(
            f'<clipPath id="clipLevel{i}" clipPathUnits="userSpaceOnUse">'
            f'  <rect x="{level_x}" y="{level_y}" width="{level_w}" height="{level_h}"/>'
            f'</clipPath>'
        )
        svg.append(
            f'<g clip-path="url(#clipShape{i})">'
            f'  <rect x="{rect_x}" y="{shape_top}" width="{rect_w}" height="{shape_h}" fill="{FILL_COLOR}" clip-path="url(#clipLevel{i})"/>'
            f'</g>'
        )

        # 3) Outline on top with depth (single, unified look)
        svg.append(
            f'<g filter="url(#tubeFX)">'
            f'  <rect x="{rect_x}" y="{rect_y}" rx="12" ry="12" width="{rect_w}" height="{rect_h}" class="tube"/>'
            f'  <circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r}" class="tube"/>'
            f'</g>'
        )

        # Ticks (right edge of tube)
        for _, y, is_major in build_ticks(bar_y, bar_h):
            if is_major:
                svg.append(
                    f'<line x1="{bar_x + bar_w}" y1="{y}" x2="{bar_x + bar_w + 8}" y2="{y}" class="tickMajor" stroke-width="2"/>'
                )
            else:
                svg.append(
                    f'<line x1="{bar_x + bar_w}" y1="{y}" x2="{bar_x + bar_w + 5}" y2="{y}" class="tickMinor" stroke-width="1"/>'
                )

        # Per-segment committed label
        svg.append(
            f'<text x="{bar_x + bar_w / 2}" y="{bulb_bottom + 18}" class="segLbl" text-anchor="middle">{fmt_currency_full(seg_val)}</text>'
        )

    # Footer note
    footer = "10 thermometers × $1M each · Major ticks $100k · Minor ticks $50k · White base with solid red fill growing upward"
    svg.append(f'<text x="{W/2}" y="{H - 14}" class="segLbl" text-anchor="middle">{footer}</text>')

    svg.append('</svg>')
    OUT.write_text("\n".join(svg))

if __name__ == "__main__":
    main()
