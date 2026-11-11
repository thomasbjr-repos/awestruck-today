"""Render Awestruck Today social assets from one entry JSON (Brand Guide: "Illuminated").

Usage: python3 render.py entry.json outdir
Produces carousel slides (1080x1350) and a lock screen (1080x1920) as PNG.
Fonts: uses Instrument Serif / Inter if installed; falls back to a local serif.
"""
import json, sys, pathlib
from playwright.sync_api import sync_playwright

NIGHT, PANEL, LINE, IVORY, MIST, SLATE, GOLD = "#0B0F14", "#121821", "#222B38", "#F1EEE8", "#C4C9D2", "#8A93A3", "#E9C77B"
SERIF = "'Instrument Serif', 'Liberation Serif', serif"
SANS = "'Inter', sans-serif"
BASE = pathlib.Path(".")

def motif_svg(color, w=920, h=560):
    # Wed motif: a music staff with a rising melody (line drawing, never presented as history)
    lines = "".join(f'<line x1="60" x2="{w-60}" y1="{200+i*36}" y2="{200+i*36}" stroke="{color}" stroke-width="2" opacity=".55"/>' for i in range(5))
    pts = [(140, 330), (260, 310), (380, 290), (500, 250), (620, 230), (740, 190)]
    notes = "".join(f'<ellipse cx="{x}" cy="{y}" rx="16" ry="11" transform="rotate(-20 {x} {y})" fill="none" stroke="{color}" stroke-width="3"/><line x1="{x+15}" x2="{x+15}" y1="{y}" y2="{y-90}" stroke="{color}" stroke-width="3"/>' for x, y in pts)
    path = " ".join(f"{x},{y}" for x, y in pts)
    return f'<svg width="100%" height="100%" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet"><polyline points="{path}" fill="none" stroke="{color}" stroke-width="1.5" stroke-dasharray="4 8" opacity=".6"/>{lines}{notes}</svg>'

def frame_inner(path, c, base):
    f = (base / path) if path else None
    if f and f.exists():
        return f'<img src="{f.resolve().as_uri()}" style="width:100%;height:100%;object-fit:cover;display:block">'
    return motif_svg(c)

FONT_DIR = pathlib.Path(__file__).resolve().parent.parent / "fonts"

def font_faces():
    css = ""
    for fam, fname, style in [("Instrument Serif", "InstrumentSerif-Regular.ttf", "normal"),
                              ("Instrument Serif", "InstrumentSerif-Italic.ttf", "italic")]:
        f = FONT_DIR / fname
        if f.exists():
            css += f"@font-face{{font-family:'{fam}';src:url('{f.as_uri()}');font-style:{style}}}"
    return css

def base_css(c):
    return font_faces() + f"""
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{width:1080px;height:1350px;background:{NIGHT};color:{IVORY};font-family:{SANS};position:relative;overflow:hidden}}
    .top{{position:absolute;top:72px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center}}
    .label{{font:500 24px {SANS};letter-spacing:.14em;color:{c}}}
    .mark{{font:400 36px {SERIF};color:{IVORY}}} .mark i{{color:{GOLD}}}
    .serif{{font-family:{SERIF}}} em{{font-style:italic;color:{c}}}
    .footer{{position:absolute;left:80px;right:80px;bottom:64px;border-top:1px solid {LINE};padding-top:22px;display:flex;justify-content:space-between;font:400 22px {SANS};color:{SLATE}}}
    """

def top(label, c):
    return f'<div class="top"><div class="label">{label}</div><div class="mark">Awestruck <i>Today</i></div></div>'

def page(css, body, h=1350):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{css} body{{height:{h}px}}</style></head><body>{body}</body></html>"

def cover(e):
    c = e["theme_color"]
    css = base_css(c) + f"""
    .frame{{position:absolute;top:150px;left:80px;right:80px;height:560px;background:{PANEL};border:1px solid {LINE}}}
    .credit{{position:absolute;top:718px;left:80px;font:400 18px {SANS};color:{SLATE}}}
    .hook{{position:absolute;top:770px;left:80px;right:80px;font:400 74px/1.06 {SERIF}}}
    .date{{position:absolute;top:1135px;left:80px;display:flex;align-items:center;gap:20px;font:400 26px {SANS};color:{MIST}}}
    .rule{{width:56px;height:2px;background:{c}}}
    """
    body = (top(e["theme"], c) + f'<div class="frame">{frame_inner(e.get("cover_image"), c, BASE)}</div><div class="credit">{e["image_label"]}</div>'
            f'<div class="hook">{e["hook_lead"]} <em>{e["hook_payoff"]}</em></div>'
            f'<div class="date"><div class="rule"></div>{e["date_line"]}</div>'
            f'<div class="footer"><span>{e["scripture_ref"]}</span><span>Swipe for the full story →</span></div>')
    return page(css, body)

def slide(e, s, n, total):
    c = e["theme_color"]
    css = base_css(c) + f"""
    .center{{position:absolute;left:80px;right:80px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center}}
    .body{{font:400 72px/1.12 {SERIF}}}
    .q{{font:400 56px/1.2 {SERIF}}} .q div:last-child{{color:{c};font-style:italic}}
    .credit{{margin-top:40px;font:400 26px {SANS};color:{MIST}}}
    .qual{{font:italic 400 64px {SERIF};color:{IVORY}}}
    .num{{font:400 300px/0.95 {SERIF};color:{c}}}
    .meaning{{font:400 56px/1.15 {SERIF};margin-top:24px;max-width:880px}}
    .cmp{{font:400 28px {SANS};color:{MIST};margin-top:28px}}
    .pre{{font:400 28px {SANS};color:{MIST};margin-bottom:28px}}
    .verse{{font:italic 400 88px/1.08 {SERIF};color:{c}}}
    .ref{{font:500 24px {SANS};letter-spacing:.14em;color:{IVORY};margin-top:32px}}
    .lm{{font:400 34px {SANS};color:{GOLD};margin-top:60px}}
    .head{{font:400 26px/1.4 {SANS};color:{MIST};margin-top:24px;max-width:800px}}
    """
    k, label, foot = s["kind"], e["theme"], f'<span>{n} / {total}</span><span>awestrucktoday.com</span>'
    if k == "image":
        inner = (f'<div style="height:520px;background:{PANEL};border:1px solid {LINE}">{frame_inner(s.get("image"), c, BASE)}</div>'
                 f'<div style="font:400 18px {SANS};color:{SLATE};margin:10px 0 36px">{s["image_label"]}</div>'
                 f'<div class="body" style="font-size:60px">{s["body"]}</div>')
    elif k == "text":
        inner = f'<div class="body">{s["body"]}</div>'
    elif k == "stat":
        label = "BY THE NUMBERS"
        inner = (f'<div class="qual">{s["qualifier"]}</div><div class="num">{s["numeral"]}</div>'
                 f'<div class="meaning">{s["meaning"]}</div><div class="cmp">{s["comparison"]}</div>')
        foot = f'<span>{s["source"]}</span><span>{n} / {total}</span>'
    elif k == "quote":
        inner = '<div class="q">' + "".join(f"<div>{l}</div>" for l in s["lines"]) + f'</div><div class="credit">{s["credit"]}</div>'
    elif k == "verse":
        inner = f'<div class="pre">{s["pre"]}</div><div class="verse">{s["text"]}</div><div class="ref">{s["ref"].upper()}</div>'
    else:  # end / Learn More slide
        inner = (f'<div class="body">{s["prompt"]}</div><div class="lm">Learn more at awestrucktoday.com</div>'
                 f'<div class="head">Every day, a true story of what God did through ordinary, flawed people to shape the world.</div>')
        foot = '<span>Comment below ↓</span><span>Share this story</span>'
    return page(css, top(label, c) + f'<div class="center">{inner}</div><div class="footer">{foot}</div>')

def lock(e):
    c = e["theme_color"]
    css = base_css(c) + f"""
    .wrap{{position:absolute;left:90px;right:90px;top:760px}}
    .q{{font:400 70px/1.2 {SERIF}}} .q div:last-child{{font-style:italic;color:{c}}}
    .credit{{margin-top:40px;font:400 28px {SANS};color:{MIST}}}
    .m{{position:absolute;left:90px;right:90px;bottom:120px;display:flex;justify-content:space-between;font:400 24px {SANS};color:{SLATE}}}
    .motif{{position:absolute;left:0;right:0;top:1380px;height:300px;opacity:.6}}
    """
    body = (f'<div class="wrap"><div class="q">' + "".join(f"<div>{l}</div>" for l in e["lock_quote"]) +
            f'</div><div class="credit">{e["lock_credit"]}</div></div><div class="motif">{motif_svg(c, 1080, 300)}</div>'
            f'<div class="m"><span class="mark" style="font-size:30px">Awestruck <i>Today</i></span><span>awestrucktoday.com</span></div>')
    return page(css, body, 1920)

def apply_credits(e):
    """When cleared images exist, replace the placeholder labels with real credit lines."""
    cred = BASE.parent / "assets" / e["id"] / "credits.json"
    if not cred.exists():
        return
    by_role = {c["role"]: c for c in json.loads(cred.read_text())}
    line = lambda c: f'{c.get("caption","")} · {c.get("credit","")}, {c.get("license","")}'.strip(" ·,")
    if "cover" in by_role:
        e["image_label"] = line(by_role["cover"])
    for s in e["slides"]:
        if s.get("kind") == "image" and "card" in by_role:
            s["image_label"] = line(by_role["card"])

def main(src, out):
    global BASE
    BASE = pathlib.Path(src).resolve().parent
    e = json.loads(pathlib.Path(src).read_text())
    apply_credits(e)
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    jobs = [("01-cover", cover(e), 1350)]
    total = len(e["slides"]) + 1
    for i, s in enumerate(e["slides"], start=2):
        jobs.append((f"{i:02d}-{s['kind']}", slide(e, s, i, total), 1350))
    jobs.append(("lockscreen", lock(e), 1920))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for name, html, h in jobs:
            pg = b.new_page(viewport={"width": 1080, "height": h})
            pg.set_content(html); pg.wait_for_timeout(150)
            pg.screenshot(path=str(out / f"{e['id']}_{name}.png")); pg.close()
        b.close()
    print("\n".join(sorted(str(f) for f in out.glob("*.png"))))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
