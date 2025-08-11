#!/usr/bin/env python3
import json, pathlib
DATA = pathlib.Path("data/funds.json"); OUT = pathlib.Path("thermometer.svg")
COLS=10; SEG_GOAL=1_000_000; W,H=1240,420
def fmt_currency_full(n): return f"${n:,.0f}"
def lerp(a,b,t): return a+(b-a)*t
def hsl_to_rgb(h, s, l):
    c=(1-abs(2*l-1))*s; x=c*(1-abs(((h/60)%2)-1)); m=l-c/2
    if   0<=h<60:   r,g,b=c,x,0
    elif 60<=h<120: r,g,b=x,c,0
    elif 120<=h<180:r,g,b=0,c,x
    elif 180<=h<240:r,g,b=0,x,c
    elif 240<=h<300:r,g,b=x,0,c
    else:           r,g,b=c,0,x
    return int((r+m)*255),int((g+m)*255),int((b+m)*255)
def rgb_hex(rgb): return "#%02x%02x%02x"%rgb
def progress_color(p):
    h=lerp(0,120,p); r,g,b=hsl_to_rgb(h,0.75,0.5); return rgb_hex((r,g,b))
def build_ticks(bar_y, bar_h):
    ticks=[]; majors=set(); v=0
    while v<=SEG_GOAL:
        rel=v/SEG_GOAL; y=bar_y+(bar_h-int(bar_h*rel)); majors.add(v); ticks.append((v,y,True)); v+=100_000
    v=50_000
    while v<SEG_GOAL:
        if v not in majors:
            rel=v/SEG_GOAL; y=bar_y+(bar_h-int(bar_h*rel)); ticks.append((v,y,False))
        v+=50_000
    if all(val!=SEG_GOAL for val,_,_ in ticks): ticks.append((SEG_GOAL, bar_y, True))
    return ticks
def main():
    d=json.loads(DATA.read_text()); goal=int(d.get("goal",10_000_000)); currency=d.get("currency","USD"); label=d.get("label","Fundraising")
    segs=[max(0,min(int(x),SEG_GOAL)) for x in d.get("segments",[0]*10)]
    total=sum(segs); pct_total=max(0.0,min(1.0,total/goal))
    pad_x=24; pad_y=24; title_y=pad_y+8; bar_w=52; gap=20; bulb_space=56
    bar_h=H-pad_y*2-70-bulb_space; bar_y=pad_y+28
    total_cols_w=COLS*bar_w+(COLS-1)*gap; start_x=(W-total_cols_w)//2
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs><style>.title{font:700 20px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}.label{font:600 13px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#222}.value{font:700 16px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#111}.tickMajor{stroke:#555}.tickMinor{stroke:#888}.tube{fill:#ffffff;stroke:#ccc}.segLbl{font:600 12px system-ui,-apple-system,Segoe UI,Roboto,sans-serif;fill:#666}</style></defs>',
         f'<text x="{pad_x}" y="{title_y}" class="title">{label} — Capital Commitments</text>',
         f'<text x="{W - pad_x}" y="{title_y}" class="value" text-anchor="end">{fmt_currency_full(total)} / {fmt_currency_full(goal)} ({int(round(pct_total*100))}%)</text>']
    for i, seg_val in enumerate(segs):
        bar_x=start_x+i*(bar_w+gap); pct=seg_val/SEG_GOAL; fill_h=int(bar_h*pct); fill_y=bar_y+(bar_h-fill_h)
        color="#e02020"
        svg.append(f'<rect x="{bar_x}" y="{bar_y}" rx="12" ry="12" width="{bar_w}" height="{bar_h}" class="tube"/>' )
        svg.append(f'<clipPath id="clipFill{i}"><rect x="{bar_x}" y="{fill_y}" width="{bar_w}" height="{fill_h}" rx="12" ry="12"/></clipPath>')
        svg.append(f'<rect x="{bar_x}" y="{bar_y}" rx="12" ry="12" width="{bar_w}" height="{bar_h}" fill="{color}" clip-path="url(#clipFill{i})"/>' )
        bulb_r=bar_w*0.65; bulb_cx=bar_x+bar_w/2; bulb_cy=bar_y+bar_h+bulb_r*0.55
        svg.append(f'<circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r}" class="tube"/>' )
        bulb_inner = color if seg_val>0 else "#ffffff"
        svg.append(f'<circle cx="{bulb_cx}" cy="{bulb_cy}" r="{bulb_r-4}" fill="{bulb_inner}"/>' )
        for val,y,is_major in build_ticks(bar_y, bar_h):
            if is_major: svg.append(f'<line x1="{bar_x+bar_w}" y1="{y}" x2="{bar_x+bar_w+8}" y2="{y}" class="tickMajor" stroke-width="2"/>')
            else:        svg.append(f'<line x1="{bar_x+bar_w}" y1="{y}" x2="{bar_x+bar_w+5}" y2="{y}" class="tickMinor" stroke-width="1"/>')
        svg.append(f'<text x="{bar_x+bar_w/2}" y="{bulb_cy+bulb_r+18}" class="segLbl" text-anchor="middle">{fmt_currency_full(seg_val)}</text>')
    footer="10 thermometers × $1M each · Major ticks $100k · Minor ticks $50k · Tracking capital commitments"
    svg.append(f'<text x="{W/2}" y="{H-14}" class="segLbl" text-anchor="middle">{footer}</text>'); svg.append('</svg>')
    OUT.write_text("\\n".join(svg))
if __name__=="__main__": main()
