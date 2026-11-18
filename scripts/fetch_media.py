"""Download cleared media for an entry, checking each license first.

Usage: python scripts/fetch_media.py content/entries/YYYY-MM-DD-short-name.json

For each item in the entry's "media" list:
- Wikimedia Commons file pages: the license is read from the Commons API (extmetadata).
- Any other URL: the item must carry its own "license" field.
Only licenses on the auto-OK list are downloaded. Everything else is skipped and
reported, so it shows up as a ⚠ for Thomas. Credits are written to assets/<ID>/credits.json.
"""
import json, re, sys, pathlib, urllib.parse, urllib.request

UA = "AwestruckTodayBot/1.0 (https://awestrucktoday.org; media pipeline)"
ALLOWED = [r"^cc0", r"^public domain", r"^pdm", r"^no known restrictions",
           r"^cc[ -]by(-sa)?[ -]?\d", r"^cc[ -]by(-sa)?$"]
BLOCKED = [r"\bnc\b", r"\bnd\b", r"non-?commercial", r"no ?deriv", r"editorial", r"fair use"]

def ok_license(name: str) -> bool:
    n = name.strip().lower()
    if any(re.search(b, n) for b in BLOCKED):
        return False
    return any(re.search(a, n) for a in ALLOWED)

def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else json.loads(data)

def commons_info(page_url):
    title = urllib.parse.unquote(page_url.split("/wiki/", 1)[1])
    api = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo"
           "&iiprop=url|extmetadata&iiurlwidth=2400&titles=" + urllib.parse.quote(title))
    page = next(iter(get(api)["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    meta = ii.get("extmetadata", {})
    strip = lambda s: re.sub("<[^>]+>", "", s or "").strip()
    return {
        "download": ii.get("thumburl") or ii["url"],
        "license": strip(meta.get("LicenseShortName", {}).get("value")),
        "artist": strip(meta.get("Artist", {}).get("value")),
        "license_url": meta.get("LicenseUrl", {}).get("value", ""),
    }

def fetch_web_lead(entry_path, entry):
    """Website-format entries: download lead_image.fetch to the lead_image.src path, once.

    Written by scripts/desk_to_entry.py. The file is fetched only if it isn't in the
    repo yet and its license is on the auto-OK list; it is resized to 800 px wide.
    """
    lead = entry.get("lead_image") or {}
    f = lead.get("fetch") or {}
    src = lead.get("src", "")
    if not f or not src.startswith("/assets/"):
        print(f"– {entry_path}: no lead image to fetch")
        return
    dest = pathlib.Path("public") / src.lstrip("/")
    if dest.exists():
        print(f"– {entry_path}: lead image already in the repo")
        return
    page = f.get("url", "")
    if "commons.wikimedia.org/wiki/File:" in page:
        info = commons_info(page)
        download, lic = info["download"], info["license"]
    else:
        download, lic = f.get("file_url") or page, f.get("license", "")
    if not ok_license(lic):
        print(f"⚠ {entry_path}: lead license '{lic or 'unknown'}' is not auto-OK; not downloaded")
        return
    data = get(download, binary=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(data)).convert("RGB")
        if im.width > 800:
            im = im.resize((800, round(im.height * 800 / im.width)), Image.LANCZOS)
        im.save(dest, "JPEG", quality=85, optimize=True, progressive=True)
    except ImportError:
        dest.write_bytes(data)
    print(f"✓ {entry_path}: lead image saved to {dest} ({lic})")


def main(entry_path):
    entry = json.loads(pathlib.Path(entry_path).read_text())
    if "id" not in entry:
        fetch_web_lead(entry_path, entry)
        return
    out = pathlib.Path("assets") / entry["id"]
    out.mkdir(parents=True, exist_ok=True)
    credits, problems = [], []
    for m in entry.get("media", []):
        if m.get("status") in ("needs_permission", "pending") or not m.get("source"):
            problems.append(f"{m.get('role')}: {m.get('status', 'no source')} — {m.get('note', '')}")
            continue
        src = m["source"]
        if "commons.wikimedia.org/wiki/File:" in src:
            info = commons_info(src)
        else:
            info = {"download": src, "license": m.get("license", ""), "artist": m.get("credit", ""), "license_url": ""}
        if not ok_license(info["license"]):
            problems.append(f"{m['role']}: license '{info['license'] or 'unknown'}' is not auto-OK — {src}")
            continue
        (out / m["file"]).write_bytes(get(info["download"], binary=True))
        credits.append({"role": m["role"], "file": m["file"], "source": src,
                        "credit": info["artist"], "license": info["license"],
                        "license_url": info["license_url"], "caption": m.get("caption", "")})
        print(f"✓ {m['role']}: {info['license']} — {info['artist']}")
    (out / "credits.json").write_text(json.dumps(credits, indent=2, ensure_ascii=False))
    for p in problems:
        print(f"⚠ {p}")

if __name__ == "__main__":
    for path in sys.argv[1:]:
        main(path)
