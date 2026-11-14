"""Render Awestruck Today social assets from one entry JSON (Brand Guide: "Illuminated").

Usage: python3 render.py content/entries/YYYY-MM-DD-slug.json outdir
Reads the entry format in content/entries/README.md. Produces a cover, stat, quote,
verse and Learn More slide (1080x1350) and a lock screen (1080x1920) as PNG.
Fonts: uses Instrument Serif / Inter if installed; falls back to a local serif.
"""
import json, sys, os, re, html, pathlib, base64, mimetypes
from playwright.sync_api import sync_playwright

NIGHT, PANEL, LINE, IVORY, MIST, SLATE, GOLD = "#0B0F14", "#121821", "#222B38", "#F1EEE8", "#C4C9D2", "#8A93A3", "#E9C77B"
SERIF = "'Instrument Serif', 'Liberation Serif', serif"
SANS = "'Inter', sans-serif"
REPO = pathlib.Path(__file__).resolve().parent.parent
BASE = REPO

# Dark-mode theme colors, same as [data-day] in src/styles/site.css.
THEME_COLOR = {
    "Preachers & Sermons": "#F2994A", "Missions & Movements": "#3FB6A8", "Books & Writings": "#E06C74",
    "Music & Hymns": "#A48CF0", "Arts & Film": "#5B8DEF", "Science, Education & Thinkers": "#8FD6E8",
    "Entrepreneurs & Builders": "#9DBF5A",
}

def esc(t):
    """Escape text, then turn *asterisks* into italics (the entry format's only markup)."""
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", html.escape(str(t or ""), quote=False))

def plain(t):
    return re.sub(r"\*(.+?)\*", r"\1", str(t or ""))

def wrap_lines(text, width=26):
    """Break a quote into short lines for the quote card and lock screen."""
    lines, cur = [], ""
    for w in plain(text).split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur] if cur else lines

def motif_svg(color, w=920, h=560):
    # Wed motif: a music staff with a rising melody (line drawing, never presented as history)
    lines = "".join(f'<line x1="60" x2="{w-60}" y1="{200+i*36}" y2="{200+i*36}" stroke="{color}" stroke-width="2" opacity=".55"/>' for i in range(5))
    pts = [(140, 330), (260, 310), (380, 290), (500, 250), (620, 230), (740, 190)]
    notes = "".join(f'<ellipse cx="{x}" cy="{y}" rx="16" ry="11" transform="rotate(-20 {x} {y})" fill="none" stroke="{color}" stroke-width="3"/><line x1="{x+15}" x2="{x+15}" y1="{y}" y2="{y-90}" stroke="{color}" stroke-width="3"/>' for x, y in pts)
    path = " ".join(f"{x},{y}" for x, y in pts)
    return f'<svg width="100%" height="100%" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet"><polyline points="{path}" fill="none" stroke="{color}" stroke-width="1.5" stroke-dasharray="4 8" opacity=".6"/>{lines}{notes}</svg>'

def data_uri(f):
    """Inline a local file so Chrome loads it (set_content pages can't read file:// URLs)."""
    mime = mimetypes.guess_type(str(f))[0] or ("font/ttf" if str(f).endswith(".ttf") else "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(pathlib.Path(f).read_bytes()).decode()

def frame_inner(path, c, base):
    f = (base / path) if path else None
    if f and f.exists():
        return f'<img src="{data_uri(f)}" style="width:100%;height:100%;object-fit:cover;display:block">'
    return motif_svg(c)

FONT_DIR = pathlib.Path(__file__).resolve().parent.parent / "fonts"

def font_faces():
    css = ""
    for fam, fname, style in [("Instrument Serif", "InstrumentSerif-Regular.ttf", "normal"),
                              ("Instrument Serif", "InstrumentSerif-Italic.ttf", "italic")]:
        f = FONT_DIR / fname
        if f.exists():
            css += f"@font-face{{font-family:'{fam}';src:url('{data_uri(f)}');font-style:{style}}}"
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

def entry_id(e):
    return f"{e['date']}-{e['slug']}"

def local_image(e):
    """The lead image file in the repo (fetch_media.py saves it under assets/<id>/), if it exists."""
    src = (e.get("lead_image") or {}).get("src", "")
    f = REPO / src.lstrip("/") if src else None
    return str(f.relative_to(REPO)) if f and f.exists() else None

def find_quote(e):
    q = e.get("quote")
    if q and q.get("text"):
        return q["text"], q.get("source", "")
    for item in e.get("story", []):
        if isinstance(item, dict) and item.get("quote"):
            return item["quote"], item.get("cite", "")
    return None, ""

def cover(e):
    c = THEME_COLOR[e["theme"]]
    li = e.get("lead_image") or {}
    hook = esc(e.get("hook") or e["title"]).replace("<i>", "<em>").replace("</i>", "</em>")
    css = base_css(c) + f"""
    .frame{{position:absolute;top:150px;left:80px;right:80px;height:560px;background:{PANEL};border:1px solid {LINE}}}
    .credit{{position:absolute;top:718px;left:80px;right:80px;font:400 18px {SANS};color:{SLATE}}}
    .hook{{position:absolute;top:770px;left:80px;right:80px;font:400 66px/1.08 {SERIF}}}
    .date{{position:absolute;top:1135px;left:80px;right:80px;display:flex;align-items:center;gap:20px;font:400 26px {SANS};color:{MIST}}}
    .rule{{flex:none;width:56px;height:2px;background:{c}}}
    .stamp{{font:500 24px {SANS};letter-spacing:.14em;color:{c}}}
    """
    stamp = ("THIS WEEK" if e.get("window") else "ON THIS DAY") + " · " + date_label(e)
    body = (top(stamp, c) + f'<div class="frame">{frame_inner(local_image(e), c, REPO)}</div><div class="credit">{esc(li.get("credit", ""))}</div>'
            f'<div class="hook">{hook}</div>'
            f'<div class="date"><div class="rule"></div>{esc(e.get("dateline", e["person"]))}</div>'
            f'<div class="footer"><span>{esc((e.get("scripture") or {}).get("ref", ""))}</span><span>Swipe for the full story →</span></div>')
    return page(css, body)

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

def date_label(e):
    d = e.get("event_date") or e["date"]
    return f"{MONTHS[int(d[5:7]) - 1]} {int(d[8:10])}"

def slide_css(c):
    return base_css(c) + f"""
    .center{{position:absolute;left:80px;right:80px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center}}
    .body{{font:400 72px/1.12 {SERIF}}}
    .q{{font:400 56px/1.2 {SERIF}}} .q div:last-child{{color:{c};font-style:italic}}
    .credit{{margin-top:40px;font:400 26px {SANS};color:{MIST}}}
    .qual{{font:italic 400 64px {SERIF};color:{IVORY}}}
    .num{{font:400 300px/0.95 {SERIF};color:{c}}}
    .meaning{{font:400 56px/1.15 {SERIF};margin-top:24px;max-width:880px}}
    .cmp{{font:400 28px {SANS};color:{MIST};margin-top:28px}}
    .pre{{font:400 28px {SANS};color:{MIST};margin-bottom:28px}}
    .verse{{font:italic 400 64px/1.12 {SERIF};color:{c}}}
    .ref{{font:500 24px {SANS};letter-spacing:.14em;color:{IVORY};margin-top:32px}}
    .lm{{font:400 34px {SANS};color:{GOLD};margin-top:60px}}
    .head{{font:400 26px/1.4 {SANS};color:{MIST};margin-top:24px;max-width:800px}}
    """

def build_slides(e):
    """(name, html, height) for each card the entry has material for."""
    c, label = THEME_COLOR[e["theme"]], e.get("holy_day") or e["theme"]
    css = slide_css(c)
    stamp = ("THIS WEEK" if e.get("window") else "ON THIS DAY") + " · " + date_label(e)
    cards = []
    nums = e.get("numbers") or []
    if nums:
        n = nums[0]
        note = [f"as of {n['as_of']}"] if n.get("as_of") else []
        note += ["reported figure"] if n.get("reported") else []
        note += [f"Tier {n['tier']}"] if n.get("tier") else []
        inner = (f'<div class="qual">{esc(n.get("prefix", ""))}</div><div class="num">{esc(n["value"])}</div>'
                 f'<div class="meaning">{esc(n["meaning"])}</div><div class="cmp">{" · ".join(note)}</div>')
        foot = f'<span>{esc(n.get("source_short", ""))}</span><span>{{n}} / {{total}}</span>'
        cards.append(("stat", "BY THE NUMBERS", inner, foot))
    qt, qsrc = find_quote(e)
    if qt:
        inner = '<div class="q">' + "".join(f"<div>{html.escape(l)}</div>" for l in wrap_lines(qt)) + f'</div><div class="credit">{esc(qsrc)}</div>'
        cards.append(("quote", stamp, inner, '<span>{n} / {total}</span><span>awestrucktoday.org</span>'))
    sc = e.get("scripture")
    if sc and sc.get("text"):
        inner = (f'<div class="pre">{esc(sc.get("note", ""))}</div><div class="verse">{esc(sc["text"])}</div>'
                 f'<div class="ref">{esc(sc["ref"].upper())} · {esc(sc.get("translation", ""))}</div>')
        cards.append(("verse", "SCRIPTURE", inner, '<span>{n} / {total}</span><span>awestrucktoday.org</span>'))
    inner = (f'<div class="body">{esc(e.get("prompt", ""))}</div><div class="lm">Learn more at awestrucktoday.org</div>'
             f'<div class="head">Every day, a true story of what God did through ordinary, flawed people to shape the world.</div>')
    cards.append(("end", label, inner, '<span>Comment below ↓</span><span>Share this story</span>'))
    total = len(cards) + 1
    out = []
    for i, (kind, lab, inner, foot) in enumerate(cards, start=2):
        foot = foot.replace("{n}", str(i)).replace("{total}", str(total))
        out.append((f"{i:02d}-{kind}", page(css, top(lab, c) + f'<div class="center">{inner}</div><div class="footer">{foot}</div>'), 1350))
    return out

def lock(e):
    c = THEME_COLOR[e["theme"]]
    qt, qsrc = find_quote(e)
    css = base_css(c) + f"""
    .wrap{{position:absolute;left:90px;right:90px;top:760px}}
    .q{{font:400 70px/1.2 {SERIF}}} .q div:last-child{{font-style:italic;color:{c}}}
    .credit{{margin-top:40px;font:400 28px {SANS};color:{MIST}}}
    .m{{position:absolute;left:90px;right:90px;bottom:120px;display:flex;justify-content:space-between;font:400 24px {SANS};color:{SLATE}}}
    .motif{{position:absolute;left:0;right:0;top:1380px;height:300px;opacity:.6}}
    """
    body = (f'<div class="wrap"><div class="q">' + "".join(f"<div>{html.escape(l)}</div>" for l in wrap_lines(qt or e["title"], 22)) +
            f'</div><div class="credit">{esc(qsrc or e["person"])}</div></div><div class="motif">{motif_svg(c, 1080, 300)}</div>'
            f'<div class="m"><span class="mark" style="font-size:30px">Awestruck <i>Today</i></span><span>awestrucktoday.org</span></div>')
    return page(css, body, 1920)

def main(src, out):
    e = json.loads(pathlib.Path(src).read_text())
    if e.get("status") not in ("Verified", "Produced", "Scheduled", "Published"):
        print(f"skip {src}: status is {e.get('status')!r}"); return
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    jobs = [("01-cover", cover(e), 1350)] + build_slides(e) + [("lockscreen", lock(e), 1920)]
    launch = {"args": ["--no-sandbox"]}
    if os.environ.get("CHROME_PATH"):
        launch["executable_path"] = os.environ["CHROME_PATH"]
    with sync_playwright() as p:
        b = p.chromium.launch(**launch)
        for name, html_, h in jobs:
            pg = b.new_page(viewport={"width": 1080, "height": h})
            pg.set_content(html_); pg.wait_for_timeout(150)
            pg.screenshot(path=str(out / f"{entry_id(e)}_{name}.png")); pg.close()
        b.close()
    print("\n".join(sorted(str(f) for f in out.glob(f"{entry_id(e)}_*.png"))))

if __name__ == "__main__":
    for path in sys.argv[1:-1]:
        main(path, sys.argv[-1])
