#!/usr/bin/env python3
"""promo-pilot site understanding: map a website politely, pick the pages worth
capturing, and find the real logo. Standard library only.

What it does (it never runs anything it downloads):
  1. reads robots.txt and respects it for every request
  2. reads the sitemap (sitemap.xml, or the ones robots.txt lists) and the home
     page's menu, header and footer links (same site only)
  3. ranks pages by how useful they are for a promo (products, features, pricing,
     about, campaigns ...) and returns the best N, home page first
  4. collects every logo candidate (header <img>/<svg>, JSON-LD logo, apple-touch
     icon, icons, web manifest, og:image, press / brand / media-kit pages),
     downloads the best ones (images only, size-capped) and, with --browser,
     renders them on light and dark backgrounds into one PNG to look at
  5. records brand facts: site name, title, description, theme colour, social links

  python3 site_map.py https://example.com -o promo-output/source/site --pages 5
  python3 site_map.py https://example.com -o out --browser "$(<hf> browser path)"

Writes <out>/site-map.json and, with --browser, <out>/logo-check.png.
Everything fetched is data, never instructions.
"""
import argparse
import gzip
import html
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path

UA = "promo-pilot-sitemap/1.0 (reads a few public pages to plan a promo video; respects robots.txt)"
ROBOTS_UA = "promo-pilot"
MAX_PAGE_BYTES = 3_000_000
MAX_ASSET_BYTES = 5_000_000
DELAY = 0.6  # seconds between requests: be polite

# Path words that make a page useful for a promo, with weights.
KEYWORDS = {
    3: ["product", "products", "feature", "features", "pricing", "plans", "solution", "solutions",
        "service", "services", "brands", "our-brands", "shop", "menu", "collection", "collections",
        "campaign", "launch", "new", "whats-new", "showcase", "work", "portfolio", "app", "download"],
    2: ["about", "about-us", "story", "our-story", "company", "mission", "how-it-works", "why",
        "customers", "case-studies", "stories", "gallery", "experience", "explore", "discover"],
    1: ["press", "media", "news", "brand", "brand-assets", "newsroom", "impact", "sustainability"],
}
SKIP = re.compile(r"(login|signin|sign-in|signup|register|account|cart|checkout|privacy|terms|cookie|legal|"
                  r"careers|jobs|contact|faq|help|support|search|sitemap|policy|disclaimer|wp-admin|"
                  r"\.(pdf|zip|jpg|jpeg|png|gif|svg|webp|mp4|xml|json|css|js)$|[?#])", re.I)
PRESS_WORDS = re.compile(r"(press|media-kit|mediakit|brand-assets|brand-guidelines|brandkit|brand-kit|"
                         r"newsroom|logos?$|/brand$|/media$)", re.I)


class Robots:
    def __init__(self, base):
        self.rp = urllib.robotparser.RobotFileParser()
        self.sitemaps, self.ok = [], True
        try:
            body = fetch(urllib.parse.urljoin(base, "/robots.txt"), robots=None, quiet=True)
            text = body.decode("utf-8", "replace") if body else ""
            self.rp.parse(text.splitlines())
            self.sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", text)
        except Exception:
            self.rp.parse([])

    def allowed(self, url):
        try:
            return self.rp.can_fetch(ROBOTS_UA, url) and self.rp.can_fetch("*", url)
        except Exception:
            return True


_last = [0.0]


def fetch(url, robots, quiet=False, limit=MAX_PAGE_BYTES, want=None):
    """GET a URL politely. Returns bytes, or None. `want` filters the content type."""
    if robots is not None and not robots.allowed(url):
        if not quiet:
            print(f"  robots.txt disallows {url}", file=sys.stderr)
        return None
    wait = DELAY - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            ctype = r.headers.get("Content-Type", "")
            if want and not any(w in ctype for w in want):
                return None
            data = r.read(limit + 1)
            if len(data) > limit:
                return None
            if r.headers.get("Content-Encoding") == "gzip" or data[:2] == b"\x1f\x8b":
                try:
                    data = gzip.decompress(data)
                except OSError:
                    pass
            return data
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        if not quiet:
            print(f"  could not fetch {url}: {e}", file=sys.stderr)
        return None


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "param"}
SVG_CASE = {n.lower(): n for n in ("linearGradient", "radialGradient", "clipPath", "foreignObject", "textPath",
                                   "feGaussianBlur", "feOffset", "feBlend", "feColorMatrix", "feComposite",
                                   "feFlood", "feMerge", "feMergeNode", "feMorphology", "feTurbulence",
                                   "feDisplacementMap", "feDropShadow", "animateTransform")}
SHAPES = re.compile(r"<(path|rect|circle|ellipse|polygon|polyline|text|g)\b", re.I)


class PageParser(HTMLParser):
    """Collects links (with the region they're in), logo candidates and brand facts."""

    def __init__(self, base, home_paths=("/",)):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.home_paths = {h.rstrip("/") for h in home_paths} | {""}
        self.links = []          # (url, text, region)
        self.logos = []          # dicts
        self.meta = {}
        self.jsonld = []
        self.manifest = None
        self.region = []         # stack of header/nav/footer/main
        self._a = None
        self._script_ld = False
        self._title = False
        self.title = ""
        self._svg_depth = 0
        self._svg_buf = []
        self._svg_ctx = None
        self.inline_svgs = []

    def _abs(self, u):
        return urllib.parse.urljoin(self.base, html.unescape(u.strip())) if u else None

    def _is_home(self, url):
        if not url:
            return False
        p = urllib.parse.urlparse(url)
        return p.netloc.lower() in ("", urllib.parse.urlparse(self.base).netloc.lower()) and p.path.rstrip("/") in self.home_paths

    def _where(self):
        for r in reversed(self.region):
            if r in ("header", "nav", "footer"):
                return r
        return "body"

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if self._svg_depth:
            self._svg_depth += 1
            self._svg_buf.append(self.get_starttag_text() or "")
            return
        if tag in VOID:
            pass  # void elements have no end tag: never push them, or the region stack drifts
        elif tag in ("header", "nav", "footer", "main"):
            self.region.append(tag)
        elif tag == "div" and re.search(r"\b(header|navbar|nav|footer|masthead|topbar)\b", a.get("class", "") + " " + a.get("id", ""), re.I):
            self.region.append("footer" if "foot" in (a.get("class", "") + a.get("id", "")).lower() else "header")
        else:
            self.region.append(tag)
        hint = " ".join([a.get("class", ""), a.get("id", ""), a.get("alt", ""), a.get("aria-label", ""), a.get("title", "")]).lower()
        if tag == "a" and a.get("href"):
            self._a = {"url": self._abs(a["href"]), "text": "", "region": self._where(), "hint": hint}
        if tag == "img":
            src = a.get("src") or a.get("data-src") or ""
            if not src and a.get("srcset"):
                src = a["srcset"].split(",")[-1].strip().split(" ")[0]
            home_link = bool(self._a and self._is_home(self._a["url"]))
            if src and ("logo" in hint or "logo" in src.lower() or (self._a and "logo" in self._a["hint"])
                        or (home_link and self._where() in ("header", "nav"))):
                self.logos.append({"url": self._abs(src), "hint": hint[:80],
                                   "source": f"<img> in {self._where()}" + (" (link to home)" if home_link else "")})
        if tag == "svg":
            home_link = bool(self._a and self._is_home(self._a["url"]))
            a_hint = self._a["hint"] if self._a else ""
            if ("logo" in hint or "logo" in a_hint) or (home_link and self._where() in ("header", "nav")):
                self._svg_depth, self._svg_buf = 1, [self.get_starttag_text() or "<svg>"]
                self._svg_ctx = f"inline <svg> in {self._where()}" + (" (link to home)" if home_link else "") + \
                    (" (marked logo)" if "logo" in hint + a_hint else "")
        if tag == "link":
            rel = a.get("rel", "").lower()
            href = self._abs(a.get("href"))
            if "manifest" in rel:
                self.manifest = href
            if "icon" in rel or "apple-touch-icon" in rel or "mask-icon" in rel:
                self.logos.append({"url": href, "source": rel + (f" {a.get('sizes')}" if a.get("sizes") else ""), "hint": ""})
        if tag == "meta":
            key = (a.get("property") or a.get("name") or "").lower()
            if key in ("og:image", "og:site_name", "og:title", "og:description", "description",
                       "theme-color", "twitter:image", "application-name"):
                self.meta.setdefault(key, a.get("content", ""))
        if tag == "script" and "ld+json" in a.get("type", ""):
            self._script_ld = True
            self._ld_buf = []
        if tag == "title":
            self._title = True

    def handle_startendtag(self, tag, attrs):
        if self._svg_depth:
            # a self-closing element inside an SVG (<path .../>): keep it as written, add no end tag
            self._svg_buf.append(self.get_starttag_text() or "")
            return
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self._svg_depth:
            self._svg_buf.append(f"</{SVG_CASE.get(tag, tag)}>")
            self._svg_depth -= 1
            if self._svg_depth == 0:
                svg = "".join(self._svg_buf)
                if 200 < len(svg) < 200_000 and SHAPES.search(svg) and not re.search(r"<use\b[^>]*href=\"#", svg):
                    self.inline_svgs.append({"svg": svg, "source": self._svg_ctx})
            return
        if tag == "a" and self._a:
            self._a["text"] = self._a["text"].strip()[:80]
            self.links.append(self._a)
            self._a = None
        if tag == "script" and self._script_ld:
            self._script_ld = False
            try:
                self.jsonld.append(json.loads("".join(self._ld_buf)))
            except ValueError:
                pass
        if tag == "title":
            self._title = False
        if tag in VOID:
            return
        # pop back to the matching open tag; ignore stray end tags (unbalanced HTML)
        if tag in self.region:
            while self.region:
                if self.region.pop() == tag:
                    break

    def handle_data(self, data):
        if self._svg_depth:
            self._svg_buf.append(html.escape(data))
        if self._a is not None:
            self._a["text"] += data
        if self._script_ld:
            self._ld_buf.append(data)
        if self._title:
            self.title += data


def same_site(url, host):
    h = urllib.parse.urlparse(url).netloc.lower()
    return h == host or h.endswith("." + host.split("www.", 1)[-1]) or host.endswith("." + h.split("www.", 1)[-1])


def norm(url):
    p = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((p.scheme, p.netloc.lower(), p.path.rstrip("/") or "/", "", "", ""))


def score(url, text, region, start_path):
    path = urllib.parse.urlparse(url).path.lower()
    if SKIP.search(url):
        return -1
    words = re.split(r"[/\-_.]+", path) + re.split(r"\W+", text.lower())
    s = 0
    for w, keys in KEYWORDS.items():
        if any(k in words or f"/{k}" in path for k in keys):
            s += w
    s += {"nav": 2, "header": 2, "footer": 0.5}.get(region, 0)
    if start_path != "/" and path.startswith(start_path):
        s += 1.5            # same section as the URL the user gave (e.g. /in/en/)
    depth = len([p for p in path.split("/") if p])
    s -= max(0, depth - 3) * 0.7  # very deep pages are usually single articles
    return s


def sitemap_urls(robots, base, host, cap=400):
    urls, queue, seen = [], list(robots.sitemaps) or [urllib.parse.urljoin(base, "/sitemap.xml")], set()
    while queue and len(urls) < cap and len(seen) < 6:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        body = fetch(sm, robots, quiet=True, want=["xml", "text", "octet"])
        if not body:
            continue
        locs = re.findall(rb"<loc>\s*([^<\s]+)\s*</loc>", body)
        for loc in locs:
            u = html.unescape(loc.decode("utf-8", "replace"))
            if u.endswith(".xml") or "sitemap" in u.lower() and u.endswith((".xml", ".gz")):
                queue.append(u)
            elif same_site(u, host):
                urls.append(u)
    return urls[:cap]


def jsonld_logos(objs):
    out, stack = [], list(objs)
    while stack:
        o = stack.pop()
        if isinstance(o, list):
            stack.extend(o)
        elif isinstance(o, dict):
            if "logo" in o:
                lg = o["logo"]
                if isinstance(lg, dict):
                    lg = lg.get("url") or lg.get("contentUrl")
                if isinstance(lg, str):
                    out.append(lg)
            stack.extend(v for v in o.values() if isinstance(v, (dict, list)))
    return out


def jsonld_facts(objs):
    facts, stack = {}, list(objs)
    while stack:
        o = stack.pop()
        if isinstance(o, list):
            stack.extend(o)
        elif isinstance(o, dict):
            if o.get("@type") in ("Organization", "Corporation", "LocalBusiness", "Brand", "WebSite", "Restaurant", "Store"):
                for k in ("name", "slogan", "description", "sameAs", "url"):
                    if k in o and k not in facts:
                        facts[k] = o[k]
            stack.extend(v for v in o.values() if isinstance(v, (dict, list)))
    return facts


def rank_logo(c, host_brand):
    src, url = c["source"].lower(), (c.get("url") or "").lower()
    s = 0
    if url.endswith(".svg") or "svg" in src:
        s += 4
    if "inline <svg>" in src:
        s += 2 + (3 if "link to home" in src else 0) + (2 if "marked logo" in src else 0) + (1 if "header" in src or "nav" in src else 0)
    if "json-ld" in src:
        s += 4
    if "press" in src:
        s += 3
    if "<img>" in src:
        s += 2 + (3 if "link to home" in src else 0) + (1 if "header" in src or "nav" in src else 0)
    if "logo" in url or "logo" in c.get("hint", ""):
        s += 2
    if host_brand and host_brand in url:
        s += 1
    if "apple-touch-icon" in src:
        s += 1.5
    if "mask-icon" in src:
        s += 1
    if src.startswith("icon") or "favicon" in url:
        s -= 1 if ".svg" in url else 2
    if "og:image" in src or "twitter" in src:
        s -= 2          # usually a banner, not the logo
    m = re.search(r"(\d+)x(\d+)", src)
    if m:
        s += min(int(m.group(1)), 512) / 256
    return s


def safe_name(url, i):
    base = Path(urllib.parse.urlparse(url).path).name or f"logo-{i}"
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base)[:60]
    return f"{i:02d}-{base}"


def download_logos(cands, out, robots, n=6):
    d = out / "logo-candidates"
    d.mkdir(parents=True, exist_ok=True)
    got = []
    for i, c in enumerate(cands[: n * 2]):
        if len(got) >= n:
            break
        if c.get("svg"):
            p = d / f"{i:02d}-inline.svg"
            svg = c["svg"]
            if "xmlns" not in svg[:300]:
                svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
            p.write_text(svg, encoding="utf-8")
        else:
            data = fetch(c["url"], robots, quiet=True, limit=MAX_ASSET_BYTES, want=["image", "svg", "octet"])
            if not data or len(data) < 120:
                continue
            name = safe_name(c["url"], i)
            if not re.search(r"\.(svg|png|jpe?g|webp|gif|ico|avif)$", name, re.I):
                name += ".svg" if data.lstrip()[:5] in (b"<svg ", b"<?xml") else ".png"
            p = d / name
            p.write_bytes(data)
        c["file"] = str(p)
        got.append(c)
    return got


def logo_sheet(logos, out, browser):
    """Render every candidate on light and dark backgrounds into one PNG (via <img>, so no SVG script runs)."""
    rows = "".join(
        f'<div class="row"><div class="lbl">#{i + 1} · {html.escape(Path(c["file"]).name)}<br><small>{html.escape(c["source"])}</small></div>'
        f'<div class="cell light"><img src="{Path(c["file"]).resolve().as_uri()}"></div>'
        f'<div class="cell dark"><img src="{Path(c["file"]).resolve().as_uri()}"></div></div>'
        for i, c in enumerate(logos))
    page = out / "logo-check.html"
    page.write_text(f"""<!doctype html><meta charset=utf-8><style>
body{{margin:0;font:14px -apple-system,Helvetica,sans-serif;background:#888}}
.row{{display:grid;grid-template-columns:260px 1fr 1fr;border-bottom:2px solid #555}}
.lbl{{padding:14px;background:#eee;color:#222;word-break:break-all}} small{{color:#666}}
.cell{{height:130px;display:flex;align-items:center;justify-content:center;padding:12px}}
.light{{background:#fff}} .dark{{background:#111}}
img{{max-height:100px;max-width:90%;object-fit:contain}}</style>{rows}""", encoding="utf-8")
    png = out / "logo-check.png"
    h = 20 + 160 * max(1, len(logos))
    cmd = [browser, "--headless", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
           f"--window-size=1100,{h}", f"--screenshot={png}", page.resolve().as_uri()]
    try:
        subprocess.run(cmd, capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return str(png) if png.exists() else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("-o", "--out", required=True, help="folder for site-map.json and logo candidates")
    ap.add_argument("--pages", type=int, default=5, help="how many pages to recommend capturing, home page included (default 5)")
    ap.add_argument("--browser", help="headless Chrome path (from `<hf> browser path`) to render logo-check.png")
    a = ap.parse_args()

    start = a.url if "://" in a.url else "https://" + a.url
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = urllib.parse.urlparse(start)
    base, host = f"{p.scheme}://{p.netloc}", p.netloc.lower()
    start_path = p.path if p.path.endswith("/") else (p.path + "/" if p.path else "/")
    brand_word = host.replace("www.", "").split(".")[0]

    robots = Robots(base)
    report = {"url": start, "robots_txt_respected": True, "blocked_by_robots": not robots.allowed(start),
              "pages": [], "logo_candidates": [], "brand": {}, "notes": []}
    home = fetch(start, robots)
    if not home:
        report["notes"].append("The start page could not be fetched (blocked, robots.txt or offline). "
                               "Fall back to `<hf> capture <url>` alone, or ask the user for assets.")
        (out / "site-map.json").write_text(json.dumps(report, indent=2))
        print(json.dumps({"ok": False, "out": str(out / "site-map.json"), "notes": report["notes"]}))
        return 1

    pp = PageParser(start, home_paths=("/", start_path))
    pp.feed(home.decode("utf-8", "replace"))

    # ---- pages ----
    cands = {}
    for l in pp.links:
        u = l["url"]
        if not u or not u.startswith("http") or not same_site(u, host):
            continue
        n = norm(u)
        sc = score(n, l["text"], l["region"], start_path)
        if sc > cands.get(n, {}).get("score", -9):
            cands[n] = {"url": n, "text": l["text"], "found_in": l["region"], "score": sc}
    sm = sitemap_urls(robots, base, host)
    for u in sm:
        n = norm(u)
        if n not in cands:
            sc = score(n, "", "sitemap", start_path) - 0.5
            cands[n] = {"url": n, "text": "", "found_in": "sitemap", "score": sc}
    home_n = norm(start)
    cands.pop(home_n, None)
    ranked = sorted((c for c in cands.values() if c["score"] > 0 and robots.allowed(c["url"])),
                    key=lambda c: -c["score"])
    # Stay inside the section the user linked (e.g. /in/en/ = India, English): other
    # countries' or languages' pages are a different audience. Only widen if it has too few.
    if start_path != "/":
        inside = [c for c in ranked if urllib.parse.urlparse(c["url"]).path.startswith(start_path.rstrip("/"))]
        if len(inside) >= min(2, a.pages - 1):
            ranked = inside
        else:
            report["notes"].append(f"Few pages under {start_path}; also using pages from other sections of the site.")
    # one page per first-level section, so the picks aren't five articles of one blog
    picked, sections = [], set()
    for c in ranked:
        segs = [s for s in urllib.parse.urlparse(c["url"]).path.split("/") if s]
        key = "/".join(segs[: len([s for s in start_path.split("/") if s]) + 1])
        if key in sections:
            continue
        sections.add(key)
        picked.append(c)
        if len(picked) >= a.pages - 1:
            break
    report["pages"] = [{"url": home_n, "why": "the page the user gave", "found_in": "start"}] + \
        [{"url": c["url"], "why": f"score {c['score']:.1f}" + (f", link text '{c['text']}'" if c["text"] else ""),
          "found_in": c["found_in"]} for c in picked]
    report["site_size"] = {"links_on_home": len(pp.links), "sitemap_urls_read": len(sm)}
    report["sections"] = sorted({"/".join([s for s in urllib.parse.urlparse(c["url"]).path.split("/") if s][:3])
                                 for c in ranked[:60]})[:40]

    # ---- logo ----
    logos = [dict(c, source=c["source"]) for c in pp.logos if c.get("url")]
    for s in pp.inline_svgs:
        logos.append({"url": None, "svg": s["svg"], "source": s["source"], "hint": "logo"})
    for u in jsonld_logos(pp.jsonld):
        logos.append({"url": urllib.parse.urljoin(start, u), "source": "JSON-LD Organization logo", "hint": "logo"})
    for key in ("og:image", "twitter:image"):
        if pp.meta.get(key):
            logos.append({"url": urllib.parse.urljoin(start, pp.meta[key]), "source": key, "hint": ""})
    if pp.manifest:
        mb = fetch(pp.manifest, robots, quiet=True)
        try:
            for ic in json.loads(mb or b"{}").get("icons", []):
                logos.append({"url": urllib.parse.urljoin(pp.manifest, ic.get("src", "")),
                              "source": f"web manifest icon {ic.get('sizes', '')}".strip(), "hint": ""})
        except ValueError:
            pass
    press = [l["url"] for l in pp.links if l["url"] and same_site(l["url"], host) and PRESS_WORDS.search(urllib.parse.urlparse(l["url"]).path)]
    press += [u for u in sm if PRESS_WORDS.search(urllib.parse.urlparse(u).path)]
    press = list(dict.fromkeys(norm(u) for u in press))
    if start_path != "/":
        local = [u for u in press if urllib.parse.urlparse(u).path.startswith(start_path.rstrip("/"))]
        press = local or [u for u in press if not re.search(r"/[a-z]{2}/[a-z]{2}(/|$)", urllib.parse.urlparse(u).path)]
    press = press[:2]
    for pu in press:
        body = fetch(pu, robots, quiet=True)
        if body:
            q = PageParser(pu, home_paths=("/", start_path))
            q.feed(body.decode("utf-8", "replace"))
            for c in q.logos:
                if c.get("url") and ("logo" in (c["url"] + c.get("hint", "")).lower()):
                    logos.append({"url": c["url"], "source": f"press/brand page {pu}", "hint": c.get("hint", "")})
            for l in q.links:
                if l["url"] and re.search(r"logo.*\.(svg|png|zip)$|\.(svg)$", l["url"], re.I):
                    logos.append({"url": l["url"], "source": f"press/brand page download {pu}", "hint": l["text"]})
    report["press_pages"] = press
    seen, uniq = set(), []
    for c in logos:
        k = c.get("url") or c.get("svg", "")[:400]
        if k and k not in seen and not (c.get("url") or "").startswith("data:"):
            seen.add(k)
            uniq.append(c)
    uniq.sort(key=lambda c: -rank_logo(c, brand_word))
    got = download_logos(uniq, out, robots)
    report["logo_candidates"] = [{"rank": i + 1, "file": c.get("file"), "url": c.get("url"), "source": c["source"],
                                  "score": round(rank_logo(c, brand_word), 1)} for i, c in enumerate(got)]
    if a.browser and got:
        sheet = logo_sheet(got, out, a.browser)
        report["logo_check_png"] = sheet
        if not sheet:
            report["notes"].append("Could not render logo-check.png; open logo-check.html or view the files directly.")

    # ---- brand facts ----
    facts = jsonld_facts(pp.jsonld)
    report["brand"] = {
        "site_name": pp.meta.get("og:site_name") or pp.meta.get("application-name") or facts.get("name"),
        "title": html.unescape(pp.title.strip())[:150],
        "description": pp.meta.get("description") or pp.meta.get("og:description") or facts.get("description"),
        "slogan": facts.get("slogan"),
        "theme_color": pp.meta.get("theme-color"),
        "social": [u for u in (facts.get("sameAs") or []) if isinstance(u, str)][:8] if isinstance(facts.get("sameAs"), list) else [],
        "nav_labels": list(dict.fromkeys(l["text"] for l in pp.links if l["region"] in ("nav", "header") and 1 < len(l["text"]) < 40))[:20],
    }
    if report["blocked_by_robots"]:
        report["notes"].append("robots.txt disallows the start page for automated tools: capture only with the user's OK, or ask for assets.")
    if not got:
        report["notes"].append("No logo found: use media-use's logo route (theSVG, favicon) or ask the user for their logo file.")

    (out / "site-map.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({"ok": True, "out": str(out / "site-map.json"), "pages": [p["url"] for p in report["pages"]],
                      "logos": [c["file"] for c in report["logo_candidates"][:3]],
                      "logo_check_png": report.get("logo_check_png"), "notes": report["notes"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
