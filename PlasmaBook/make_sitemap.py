#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Генерує ../sitemap.xml і ../robots.txt для GitHub Pages.

Запуск (після публікації online/):  python -I make_sitemap.py
Сторінки беруться з диска: корінь сайту, online/chN.html, симуляції PlasmaBook/sims/*.html.
Службові файли (shared/, копії з підкресленням в кінці імені, main-html.html) пропускаються.
"""
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SITE = "https://sergiokapone.github.io/plasma-physics/"


def chapter_key(p: Path) -> int:
    m = re.search(r"ch(\d+)\.html$", p.name)
    return int(m.group(1)) if m else 0


def collect() -> list[str]:
    urls = [SITE, SITE + "simulations.html", SITE + "online/"]
    online = ROOT / "online"
    for p in sorted(online.glob("ch*.html"), key=chapter_key):
        urls.append(SITE + "online/" + p.name)
    sims = HERE / "sims"
    for p in sorted(sims.glob("*.html")):
        if p.stem.endswith("_"):          # робочі копії
            continue
        urls.append(SITE + "PlasmaBook/sims/" + p.name)
    return urls


def main() -> None:
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    urls = collect()
    for u in urls:
        lines += ["  <url>", "    <loc>%s</loc>" % u,
                  "    <lastmod>%s</lastmod>" % today, "  </url>"]
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % SITE, encoding="utf-8")
    print("sitemap.xml: %d URL, robots.txt записано в %s" % (len(urls), ROOT))


if __name__ == "__main__":
    main()
