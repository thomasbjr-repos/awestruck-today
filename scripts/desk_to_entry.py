"""Turn one Verified Review Desk entry into a website entry file, word for word.

Usage:
  python scripts/desk_to_entry.py desk-entry.json [--review review.json] [--write]

desk-entry.json is the entry document exactly as the Review Desk stores it
(entries/<ID>). review.json is its reviews/<ID> document. Without --write the
script only prints what it would write and the checks it ran.

Rules (Concept Brief, "Three approval gates"):
- Only entries Thomas set to Verified on the Desk are written.
- Text is copied, never reworded. The only changes are mechanical: footnote
  superscripts are removed from the story, and the hook's payoff gets its *italics*.
- An existing file for the same date is never overwritten.
- Anything that looks like a review note in a public field (⚠, "to confirm", image
  sizes, instructions) stops the entry: it is reported, not published.

Exit codes: 0 written (or would write), 2 blocked by a check, 3 already in the repo.
"""
import json, re, sys, pathlib, datetime

THEMES = {
    "sun": "Preachers & Sermons", "mon": "Missions & Movements", "tue": "Books & Writings",
    "wed": "Music & Hymns", "thu": "Arts & Film", "fri": "Science, Education & Thinkers",
    "sat": "Entrepreneurs & Builders",
}
# Full credit lines for copyrighted translations (Concept Brief, "Bible translations").
CREDITS = {
    "NIV": "Scripture quotations taken from The Holy Bible, New International Version® NIV®. Copyright © 1973, 1978, 1984, 2011 by Biblica, Inc.™ Used by permission. All rights reserved worldwide.",
    "ESV": "Scripture quotations are from the ESV® Bible (The Holy Bible, English Standard Version®), © 2001 by Crossway, a publishing ministry of Good News Publishers. ESV Text Edition: 2025. The ESV text may not be quoted in any publication made available to the public by a Creative Commons license. The ESV may not be translated in whole or in part into any other language. Used by permission. All rights reserved.",
    "CSB": "Christian Standard Bible®, Copyright © 2017 by Holman Bible Publishers. Used with permission. All rights reserved worldwide.",
    "NKJV": "Scripture taken from the New King James Version®. Copyright © 1982 by Thomas Nelson. Used by permission. All rights reserved.",
}
MONTHS = {m: i for i, m in enumerate(["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"], 1)}
SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹˒"
# Review notes that must never reach the public site.
RED_FLAGS = [r"⚠", r"\bto confirm\b", r"\bnot yet\b", r"\bTODO\b", r"\bunconfirmed\b", r"\b\d{3,5}\s?px\b",
             r"\brendition\b", r"full/max", r"\bdrafter\b", r"\bchecker\b", r"\bClaude\b", r"\bThomas\b",
             r"\bDesk\b", r"\bplaceholder\b"]


def plain_tier(t):
    m = re.match(r"\s*([ABC])", str(t or ""))
    return m.group(1) if m else ""


def strip_notes(s):
    return re.sub(f"[{SUPERSCRIPTS}]+", "", s).replace("  ", " ").strip()


def hook_with_italics(h):
    text, payoff = (h or {}).get("text", ""), (h or {}).get("payoff", "")
    if payoff and payoff in text:
        i = text.rfind(payoff)
        return text[:i] + "*" + payoff + "*" + text[i + len(payoff):]
    return text


def parse_source(line):
    """'3. Title — https://a · also https://b' -> {text, url}."""
    s = re.sub(r"^\s*\d+\.\s*", "", line).strip()
    urls = re.findall(r"https?://\S+", s)
    text = re.split(r"\s+—\s+https?://", s, maxsplit=1)[0]
    text = re.sub(r"\s*·\s*$", "", re.sub(r"https?://\S+", "", text)).strip(" ·—")
    out = {"text": text}
    if urls:
        out["url"] = urls[0].rstrip(").,;")
    return out


def window_fields(e):
    label = (e.get("stampLabel") or "").upper()
    if not label.startswith("THIS WEEK"):
        return {}
    m = re.search(r"([A-Z]{3})\s+(\d{1,2})", label)
    pub = datetime.date.fromisoformat(e["publishDate"])
    if not m:
        return {"window": True}
    best = None
    for y in (pub.year - 1, pub.year, pub.year + 1):
        try:
            d = datetime.date(y, MONTHS[m.group(1)], int(m.group(2)))
        except (KeyError, ValueError):
            continue
        if best is None or abs((d - pub).days) < abs((best - pub).days):
            best = d
    return {"window": True, "event_date": best.isoformat()} if best else {"window": True}


def lead_license(e):
    for im in e.get("images") or []:
        if str(im.get("use", "")).lower().startswith("lead"):
            return im.get("license", ""), im.get("status")
    return "", None


def convert(e):
    date = e["publishDate"]
    slug = (e.get("webUrl") or "").rstrip("/").split("/")[-1]
    stem = f"{date}-{slug}"
    lic, lead_status = lead_license(e)
    lead = e.get("lead") or {}
    out = {
        "date": date,
        "slug": slug,
        "title": e.get("title") or e["person"],
        "person": e["person"],
        "theme": THEMES[e["themeKey"]],
        "status": "Verified",
        "hook": hook_with_italics(e.get("hook")),
        "dateline": e.get("dateLine", ""),
        "summary": e.get("summary") or e.get("dateLine", ""),
    }
    if e.get("holyDay"):
        out["holy_day"] = e["holyDay"]
    out.update(window_fields(e))
    out["lead_image"] = {
        "src": f"/assets/{stem}/lead-800.jpg",
        "srcset": f"/assets/{stem}/lead-800.jpg 800w",
        "alt": lead.get("alt") or lead.get("title", ""),
        "credit": lead.get("credit", ""),
        "focus": lead.get("focus", "50% 30%"),
        # Read by scripts/fetch_media.py (GitHub Action), which downloads the file
        # only if the license is on the free-to-use list.
        "fetch": {"url": e.get("leadPage") or lead.get("url", ""), "file_url": lead.get("url", ""), "license": lic},
    }
    nums = []
    for n in e.get("numbers") or []:
        tier = plain_tier(n.get("tier"))
        item = {"value": n.get("figure", ""), "meaning": n.get("measures", ""), "as_of": n.get("asOf", ""),
                "tier": tier, "source_short": n.get("source", "")}
        if "reported" in str(n.get("tier", "")).lower() or tier == "C":
            item["reported"] = True
        nums.append(item)
    nums.sort(key=lambda x: x["tier"] == "C")  # never a Tier C figure first
    if nums:
        out["numbers"] = nums
    out["story"] = [strip_notes(p) for p in e.get("story") or []]
    q = e.get("quote") or {}
    if q.get("text"):
        out["quote"] = {"text": q["text"], "source": q.get("source", ""), "tier": plain_tier(q.get("tier"))}
    s = e.get("scripture") or {}
    if s.get("text"):
        out["scripture"] = {"text": s["text"], "ref": s.get("ref", ""), "translation": s.get("translation", ""),
                            "note": s.get("reason", "")}
        tr = (s.get("translation") or "").upper()
        if tr in CREDITS:
            out["scripture_credits"] = [CREDITS[tr]]
    extras = []
    for im in e.get("images") or []:
        use = str(im.get("use", "")).lower()
        if use.startswith("lead") or im.get("status") == "warn" or not im.get("url"):
            continue
        if use.startswith("gallery") or use.startswith("see"):
            extras.append({"type": "gallery", "title": im.get("image", ""), "url": im["url"], "credit": im.get("license", "")})
    if extras:
        out["extras"] = extras[:3]
    out["why"] = e.get("why", "")
    out["prompt"] = e.get("prompt", "")
    out["ask_yourself"] = e.get("prompt", "")
    if e.get("whyReel"):
        out["why_reel_line"] = e["whyReel"]
    srcs = []
    for line in e.get("sources") or []:
        if re.match(r"^\s*(note|further reading)", line, re.I):
            continue
        srcs.append(parse_source(line))
    out["sources"] = srcs
    if e.get("confidence"):
        out["confidence"] = e["confidence"]
    return stem, out, lead_status


PUBLIC_TEXT = ["title", "hook", "dateline", "summary", "why", "prompt", "why_reel_line"]


def checks(e, review, out, lead_status):
    problems = []
    if not review or review.get("status") != "Verified":
        problems.append(f"not Verified on the Desk (status: {(review or {}).get('status', 'none')})")
    for k, ed in ((review or {}).get("edits") or {}).items():
        if ed.get("status") not in ("applied",) and not (ed.get("status") == "proposed" and ed.get("accepted")):
            problems.append(f"edit '{k}' is still {ed.get('status')}: run the Desk sync first")
    if e.get("archived"):
        problems.append("entry is archived")
    if e.get("sample"):
        problems.append("sample entry")
    for k in ("date", "slug", "title", "person", "theme", "hook", "dateline", "why"):
        if not out.get(k):
            problems.append(f"missing {k}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", out.get("slug", "")):
        problems.append(f"bad slug {out.get('slug')!r}")
    if not out["story"]:
        problems.append("missing story")
    if lead_status == "warn":
        problems.append("lead image license still marked ⚠ on the Desk")
    if not out["lead_image"]["fetch"]["url"] or not out["lead_image"]["fetch"]["license"]:
        problems.append("lead image has no source URL or license")
    # Review notes leaking into public text
    fields = {k: out.get(k, "") for k in PUBLIC_TEXT}
    fields["lead credit"] = out["lead_image"]["credit"]
    fields["lead alt"] = out["lead_image"]["alt"]
    for i, p in enumerate(out["story"]):
        fields[f"story ¶{i + 1}"] = p
    for k in ("quote", "scripture"):
        for kk, v in (out.get(k) or {}).items():
            fields[f"{k}.{kk}"] = v
    for i, n in enumerate(out.get("numbers", [])):
        for kk in ("value", "meaning", "source_short"):
            fields[f"number {i + 1} {kk}"] = n.get(kk, "")
    for i, s in enumerate(out["sources"]):
        fields[f"source {i + 1}"] = s.get("text", "")
    for i, x in enumerate(out.get("extras", [])):
        fields[f"extra {i + 1}"] = f"{x.get('title', '')} {x.get('credit', '')}"
    for name, val in fields.items():
        for pat in RED_FLAGS:
            if re.search(pat, str(val), re.I):
                problems.append(f"{name}: looks like a review note ({pat!r}): {str(val)[:120]}")
                break
    # Confidence may carry ⚠ (it's the public confidence note) but never instructions.
    for pat in RED_FLAGS[1:]:
        if re.search(pat, out.get("confidence", ""), re.I):
            problems.append(f"confidence: looks like a review note ({pat!r})")
            break
    return problems


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    e = json.loads(pathlib.Path(args[0]).read_text())
    review = None
    if "--review" in args:
        review = json.loads(pathlib.Path(args[args.index("--review") + 1]).read_text())
    stem, out, lead_status = convert(e)
    target = pathlib.Path("content/entries") / f"{stem}.json"
    existing = list(pathlib.Path("content/entries").glob(f"{out['date']}-*.json"))
    if existing:
        print(f"ALREADY IN REPO: {existing[0]} (not overwritten)")
        return 3
    problems = checks(e, review, out, lead_status)
    if problems:
        print(f"BLOCKED: {stem}")
        for p in problems:
            print(f"  - {p}")
        return 2
    if "--write" in args:
        target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
        print(f"WROTE {target}")
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        print(f"OK (dry run): would write {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
