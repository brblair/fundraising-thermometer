#!/usr/bin/env python3
import json, pathlib

# Inputs / outputs
DATA = pathlib.Path("data/funds.json")
OUT  = pathlib.Path("thermometer.svg")

# Layout constants
COLS = 10
SEG_GOAL = 1_000_000

# Base canvas; will auto-expand if needed when labels are shown
BASE_W, H = 1240, 460  # W may grow; H has extra room for top labels

# Label behavior
EXPAND_ALL_LABELS = False   # <-- set True to show right-side labels on every thermometer
LABEL_EVERY = 100_000       # label increment
SHOW_MINOR_50K_TICKS = True # keep minor tick lines at 50k

# Spacing / sizing
PAD_X = 24
PAD_Y = 24
TITLE_Y_OFFSET = 8
BAR_W = 52
BASE_GAP = 20               # gap between thermometers (no labels)
TOP_LABEL_GAP = 18          # space above bars for $1M…$10M
BULB_SPACE = 56             # space for rounded bulb below bars

# Right-side label block geometry (text area to the right of a thermometer)
LABEL_TEXT_OFFSET = 10      # pixels from tube edge to label text
LABEL_BLOCK = 66            # reserved width for label text block
LABEL_SPACER = 6            # small extra gap after a label block (before next tube)
RIGHT_MARGIN_LAST = 16      # right margin after the last column if it has labels

def fmt_currency_full(n): return f"${n:,.0f}"

def build_ticks(bar_y, bar_h):
    """Return list of (value, y, is_major). Major: every 100k; minor: 50k."""
    ticks, majors = [], set()
    v = 0
    while v <= SEG_GOAL:
        rel = v / SEG_GOAL
        y = bar_y + (bar_h - int(bar_h * rel))
        majors.add(v)
        ticks.append((v, y, True))
        v += 100_000

    if SHOW_MINOR_50K_TICKS:
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
    if v >= 1_000_000: return "$1M"
    if v == 0:         return "$0"
    return f"${v//1000}k"

def main():
    d = json.loads(DATA.read_text())
    goal  = int(d.get("goal", 10_000_000))
    label = d.get("label", "Fundraising")
    segs  = [max(0, min(int(x), SEG_GOAL)) for x in d.get("segments", [0]*COLS)]
    if len(segs) < COLS: segs += [0]*(COLS - len(segs))
    if len(segs) > COLS: segs  = segs[:COLS]

    total = sum(segs)
    pct_total = max(0.0, min(1.0, total/goal))

    # Compute dynamic positions with extra space wherever labels are shown
    # Compact: labels only on LAST thermometer
    def labels_here(i: int) -> bool:
        return EXPAND_ALL_LABELS or (i == COLS - 1)

    # Bar band height and top position
    bar_h = H - PAD_Y*2 - 90 - BULB_SPACE
    bar_y = PAD_Y + 28 + TOP_LABEL_GAP

    # Compute total width needed
    sum_bars = COLS * BAR_W
    sum_base_gaps = (COLS - 1) * BASE_GAP
    sum_label_blocks_between = sum((LABEL_BLOCK + LABEL_SPACER) for i in range(COLS - 1) if labels_here(i))
    right_block_last = (LABEL_BLOCK + RIGHT_MARGIN_LAST) if labels_here(COLS - 1) else 0
    total_cols_w = sum_bars + sum_base_gaps + sum_label_blocks_between + right_block_last

    # Final canvas width (auto-expand if needed)
    W = max(BASE_W, total_cols_w + PAD_X*2)

    # Build x positions
    x_positions = []
    x = (W - total_cols_w) // 2
    for i in range(COLS):
        x_positions.append(x)
        if i < COLS - 1:
            x += BAR_W + BASE_GAP + ((LABEL_BLOCK + LABEL_SPACER) if labels_here(i) else 0)
        else:
            # last column; extend for right-side labels (for centering & not cutting off)
            x += BAR_W + (LABEL_BLOCK if labels_here(i) else 0)

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
        f'''<text x="{PAD_X}" y="{PAD_Y + TITLE_Y_OFFSET}" class="title">{label} — Capital Commitments</text>''',
        f'''<text x="{W - PAD_X}" y="{PAD_Y + TITLE_Y_OFFSET}" class="value" text-anchor="end">{fmt_currency_full(total)} / {fmt_currency_full(goal)} ({int(round(pct_total*100))}%)</text>'''
    ]

    ticks = build_ticks(bar_y, bar_h)

    for i, seg_val in enumerate(segs):
        bar_x = x_positions[i]
        pct = seg_val / SEG_GOAL
        fill_h = int(bar_h * pct)
        fill_y = bar_y + (bar_h - fill_h)
        color = "#e02020"

        # Top label above each bar: $1M ... $10M
        top_text = f"${i+1}M"
        svg.append(f'''<text x="{bar_x+BAR_W/2}" y="{bar_y-TOP_LABEL_GAP+2}" class="topLbl" text-anchor="middle">{top_text}</text>''')

        # Tube body (white base)
        svg.append(f'''<rect x="{bar_x}" y="{bar_y}" rx="12" ry="12" width="{BAR_W}" height="{bar_h}" class="tube"/>''')

        # Column fill (red, clipped to current level)
        svg.append(f'''<clipPath id="clipFill{i}"><rect x="{bar_x}" y="{fill_y}" width="{BAR_W}" height="{fill_h}" rx="12" ry="12"/></clipPath>''')
        svg.append(f'''<rect x="{bar_x}" y="{bar_y}" rx="12" ry="12" width="{BAR_W}" height="{bar_h}" fill="{color}" clip-path="url(#clipFill{i})"/>''')

        # Bulb: red iff seg_val > 0; fill first then outline (avoid white ring)
        bulb_r = BAR_W * 0.65
        bulb_cx = bar_x + BAR_W/2
        bulb_cy = bar_y + bar_h + bulb_r*0.55
        bulb_inner = color if seg_val > 0 else "#ffffff"
        svg.append(f'''<circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r-1}" style="fill:{bulb_inner}"/>''')
        svg.append(f'''<circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r}" fill="none" stroke="#ccc" stroke-width="1"/>''')

        # Tick lines (always draw, both major and optional minor)
        for val, y, is_major in ticks:
            x1 = bar_x + BAR_W
            x2 = x1 + (8 if is_major else 5)
            cls = "tickMajor" if is_major else "tickMinor"
            sw = "2" if is_major else "1"
            svg.append(f'''<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="{cls}" stroke-width="{sw}"/>''')

        # Right-side tick labels (every $100k): only on last col in compact mode
        show_labels = EXPAND_ALL_LABELS or (i == COLS - 1)
        if show_labels:
            lbl_x = bar_x + BAR_W + LABEL_TEXT_OFFSET
            v = 0
            while v <= SEG_GOAL:
                y = bar_y + (bar_h - int(bar_h * (v/SEG_GOAL)))
                svg.append(f'''<text x="{lbl_x}" y="{y}" class="tickLbl" dominant-baseline="middle">{fmt_100k_label(v)}</text>''')
                v += LABEL_EVERY

        # Committed value below bulb
        svg.append(f'''<text x="{bar_x+BAR_W/2}" y="{bulb_cy+bulb_r+18}" class="segLbl" text-anchor="middle">{fmt_currency_full(seg_val)}</text>''')

    footer = "10 thermometers × $1M each · Major ticks $100k (minor $50k) · $100k labels (compact: last column only)"
    svg.append(f'''<text x="{W/2}" y="{H-14}" class="segLbl" text-anchor="middle">{footer}</text>''')
    svg.append('''</svg>''')

    OUT.write_text("\n".join(svg))

if __name__ == "__main__":
    main()
