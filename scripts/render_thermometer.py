#!/usr/bin/env python3
import json, pathlib

DATA = pathlib.Path("data/funds.json")
OUT  = pathlib.Path("thermometer.svg")

COLS = 10
SEG_GOAL = 1_000_000
W, H = 1240, 460  # a bit taller to make room for top labels
COMPACT_LABELS = True  # <-- set False to show right-side labels on every column

def fmt_currency_full(n): return f"${n:,.0f}"

def build_ticks(bar_y, bar_h):
    """Return list of (value, y, is_major) from $0..$1M.
       Major every $100k; minor every $50k (no labels on 50k)."""
    ticks = []
    majors = set()
    v = 0
    while v <= SEG_GOAL:
        rel = v / SEG_GOAL
        y = bar_y + (bar_h - int(bar_h * rel))
        majors.add(v)
        ticks.append((v, y, True))
        v += 100_000

    v = 50_000
    while v < SEG_GOAL:
        if v not in majors:
            rel = v / SEG_GOAL
            y = bar_y + (bar_h - int(bar_h * rel))
            ticks.append((v, y, False))
        v += 50_000

    if all(val != SEG_GOAL for val, _, _ in ticks):
        ticks.append((SEG_GOAL, bar_y, True))
    return ticks

def fmt_100k_label(v: int) -> str:
    """$0, $100k, ..., $1M."""
    if v >= 1_000_000:
        return "$1M"
    elif v == 0:
        return "$0"
    else:
        return f"${v//1000}k"

def main():
    d = json.loads(DATA.read_text())
    goal = int(d.get("goal", 10_000_000))
    label = d.get("label", "Fundraising")
    segs = [max(0, min(int(x), SEG_GOAL)) for x in d.get("segments", [0]*COLS)]
    if len(segs) < COLS:
        segs += [0]*(COLS-len(segs))
    elif len(segs) > COLS:
        segs = segs[:COLS]

    total = sum(segs)
    pct_total = max(0.0, min(1.0, total/goal))

    # Layout
    pad_x = 24; pad_y = 24; title_y = pad_y + 8
    bar_w = 52; gap = 20; top_label_gap = 18; bulb_space = 56
    bar_h = H - pad_y*2 - 90 - bulb_space
    bar_y = pad_y + 28 + top_label_gap
    total_cols_w = COLS*bar_w + (COLS-1)*gap
    start_x = (W - total_cols_w)//2

    svg = [
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">''',
        '''<defs><style>
            .title{font:700 24px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}
            .label{font:600 16px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#222}
            .value{font:700 18px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}
            .tickMajor{stroke:#555}
            .tickMinor{stroke:#888}
            .tube{fill:#ffffff;stroke:#ccc}
            .segLbl{font:600 16px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#444}
            .topLbl{font:700 16px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#333}
            .tickLbl{font:600 16px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#555}
        </style></defs>''',
        f'''<text x="{pad_x}" y="{title_y}" class="title">{label} — Capital Commitments</text>''',
        f'''<text x="{W - pad_x}" y="{title_y}" class="value" text-anchor="end">{fmt_currency_full(total)} / {fmt_currency_full(goal)} ({int(round(pct_total*100))}%)</text>'''
    ]

    for i, seg_val in enumerate(segs):
        bar_x = start_x + i*(bar_w + gap)
        pct = seg_val / SEG_GOAL
        fill_h = int(bar_h * pct)
        fill_y = bar_y + (bar_h - fill_h)
        color = "#e02020"

        # Top label: $1M ... $10M
        top_text = f"${i+1}M"
        svg.append(f'''<text x="{bar_x+bar_w/2}" y="{bar_y-top_label_gap+2}" class="topLbl" text-anchor="middle">{top_text}</text>''')

        # Tube body (white base)
        svg.append(f'''<rect x="{bar_x}" y="{bar_y}" rx="12" ry="12" width="{bar_w}" height="{bar_h}" class="tube"/>''')

        # Column fill (red, clipped to current level)
        svg.append(f'''<clipPath id="clipFill{i}"><rect x="{bar_x}" y="{fill_y}" width="{bar_w}" height="{fill_h}" rx="12" ry="12"/></clipPath>''')
        svg.append(f'''<rect x="{bar_x}" y="{bar_y}" rx="12" ry="12" width="{bar_w}" height="{bar_h}" fill="{color}" clip-path="url(#clipFill{i})"/>''')

        # Bulb: red iff seg_val > 0; draw fill first then outline (no white ring)
        bulb_r = bar_w * 0.65
        bulb_cx = bar_x + bar_w/2
        bulb_cy = bar_y + bar_h + bulb_r*0.55
        bulb_inner = color if seg_val > 0 else "#ffffff"
        svg.append(f'''<circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r-1}" style="fill:{bulb_inner}"/>''')
        svg.append(f'''<circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r}" fill="none" stroke="#ccc" stroke-width="1"/>''')

        # Tick lines
        for val, y, is_major in build_ticks(bar_y, bar_h):
            x1 = bar_x + bar_w; x2 = x1 + (8 if is_major else 5)
            cls = "tickMajor" if is_major else "tickMinor"
            sw = "2" if is_major else "1"
            svg.append(f'''<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="{cls}" stroke-width="{sw}"/>''')

        # Tick labels: only $100k increments; only on first & last when COMPACT_LABELS is True
        draw_labels_here = (not COMPACT_LABELS) or (i == 0) or (i == COLS - 1)
        if draw_labels_here:
            lbl_x = bar_x + bar_w + 12
            v = 0
            while v <= SEG_GOAL:
                # Only label 100k increments
                y = bar_y + (bar_h - int(bar_h * (v/SEG_GOAL)))
                svg.append(f'''<text x="{lbl_x}" y="{y}" class="tickLbl" dominant-baseline="middle">{fmt_100k_label(v)}</text>''')
                v += 100_000

        # Segment committed value below bulb
        svg.append(f'''<text x="{bar_x+bar_w/2}" y="{bulb_cy+bulb_r+18}" class="segLbl" text-anchor="middle">{fmt_currency_full(seg_val)}</text>''')

    footer = "10 thermometers × $1M each · Major ticks $100k (minor $50k) · Labels every $100k (compact on ends)"
    svg.append(f'''<text x="{W/2}" y="{H-14}" class="segLbl" text-anchor="middle">{footer}</text>''')
    svg.append('''</svg>''')

    OUT.write_text("\n".join(svg))

if __name__ == "__main__":
    main()
