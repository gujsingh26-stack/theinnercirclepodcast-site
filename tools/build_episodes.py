#!/usr/bin/env python3
"""Builds the episode pages for theinnercirclepodcast.co.uk.

Reads tools/episodes.json and writes:
  episodes/<slug>.html   one page per episode
  episodes/index.html    the list of every episode
  sitemap.xml            every page on the site
and refreshes the episode grid on the homepage between the
<!-- EPISODES:START --> and <!-- EPISODES:END --> markers.

Run from the repo root:  python3 tools/build_episodes.py
"""
import html
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "tools", "episodes.json")
OUT = os.path.join(ROOT, "episodes")
SITE = "https://theinnercirclepodcast.co.uk"
LOGO = "https://ugc.production.linktr.ee/766bd147-d7c8-4290-9f76-fc83cc9f6202_IMG-6929.jpeg"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400'
    '&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">'
)

MARK_SVG = (
    '<svg viewBox="0 0 32 32" fill="none" aria-hidden="true">'
    '<circle cx="16" cy="16" r="13" stroke="#C9A24A" stroke-width="1.5"/>'
    '<circle cx="16" cy="16" r="7" stroke="#C9A24A" stroke-width="1.5"/>'
    '<circle cx="16" cy="16" r="2" fill="#C9A24A"/></svg>'
)


def esc(s):
    return html.escape(str(s), quote=True)


def nice_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return date(y, m, d).strftime("%-d %B %Y")


def thumb(vid):
    return f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg"


def header(current, up):
    """Site header. `current` is one of episodes/clips/blog/sponsor. `up` is '../' or ''."""
    def item(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<li><a href="{href}"{cur}>{label}</a></li>'
    return f"""<header class="site">
  <div class="wrap nav">
    <a class="mark" href="{up}index.html" aria-label="The Inner Circle Podcast home">
      {MARK_SVG}
      <span>The Inner Circle</span>
    </a>
    <ul>
      {item(up + 'episodes/', 'Episodes', 'episodes')}
      {item(up + 'index.html#clips', 'Clips', 'clips')}
      {item(up + 'blog/', 'Blog', 'blog')}
      <li><a class="cta" href="{up}sponsor.html">Sponsor the show</a></li>
    </ul>
  </div>
</header>"""


def footer(up):
    return f"""<footer class="wrap site">
  <span>© <span id="yr">2026</span> The Inner Circle Podcast. Produced by Framora.</span>
  <span>
    <a href="https://www.youtube.com/@TheInnerCirclePodcastOfficial" target="_blank" rel="noopener">YouTube</a> ·
    <a href="https://www.instagram.com/theinnercirclepodcast.official" target="_blank" rel="noopener">Instagram</a> ·
    <a href="https://www.tiktok.com/@theinnercirclepodcast.official" target="_blank" rel="noopener">TikTok</a> ·
    <a href="https://www.facebook.com/profile.php?id=61565287599182" target="_blank" rel="noopener">Facebook</a> ·
    <a href="{up}episodes/">Episodes</a> ·
    <a href="{up}blog/">Blog</a> ·
    <a href="{up}sponsor.html">Sponsor</a>
  </span>
</footer>

<script>document.getElementById('yr').textContent=new Date().getFullYear();</script>"""


def card(ep, up):
    """Episode card used on the homepage and the episodes index."""
    vid = ep["id"]
    return f"""        <li><a class="card" href="{up}episodes/{ep['slug']}.html">
          <span class="thumb"><span class="ph" aria-hidden="true">{MARK_SVG}<b>Episode {ep['n']}</b><small>Watch the episode</small></span><img src="{thumb(vid)}" alt="" loading="lazy" data-fb="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" onerror="if(this.dataset.fb){{this.src=this.dataset.fb;this.removeAttribute('data-fb')}}else{{this.style.display='none'}}"><span class="play" aria-hidden="true"></span></span>
          <h3>{esc(ep['guest'])}</h3>
          <p class="meta">Episode {ep['n']} · {nice_date(ep['date'])}</p>
          <p class="desc">{esc(ep['h1'])}</p>
        </a></li>"""


def episode_page(ep, prev_ep, next_ep):
    vid = ep["id"]
    url = f"{SITE}/episodes/{ep['slug']}.html"
    yt = f"https://www.youtube.com/watch?v={vid}"
    title = ep["seo_title"]
    paras = "\n".join(f"      <p>{esc(p)}</p>" for p in ep["summary"])
    points = "\n".join(f"        <li>{esc(p)}</li>" for p in ep["points"])
    links = ""
    if ep["links"]:
        lis = "\n".join(
            f'        <li><a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["label"])}</a></li>'
            for l in ep["links"]
        )
        links = f"\n      <ul>\n{lis}\n      </ul>"
    keywords = ", ".join([ep["guest"], "The Inner Circle Podcast", "DJ Haashim"] + ep["topics"])

    nav_items = []
    if next_ep:
        nav_items.append(
            f'<a class="ep-nav-link" href="{next_ep["slug"]}.html"><small>Next episode</small><b>Episode {next_ep["n"]}: {esc(next_ep["guest"])}</b></a>'
        )
    if prev_ep:
        nav_items.append(
            f'<a class="ep-nav-link" href="{prev_ep["slug"]}.html"><small>Previous episode</small><b>Episode {prev_ep["n"]}: {esc(prev_ep["guest"])}</b></a>'
        )
    ep_nav = "\n      ".join(nav_items)

    ld = {
        "@context": "https://schema.org",
        "@type": "PodcastEpisode",
        "name": ep["h1"],
        "episodeNumber": ep["n"],
        "url": url,
        "datePublished": ep["date"],
        "description": ep["meta"],
        "inLanguage": "en-GB",
        "image": thumb(vid),
        "partOfSeries": {
            "@type": "PodcastSeries",
            "name": "The Inner Circle Podcast",
            "url": SITE + "/",
        },
        "author": {"@type": "Person", "name": "DJ Haashim"},
        "associatedMedia": {
            "@type": "VideoObject",
            "name": ep["h1"],
            "description": ep["meta"],
            "thumbnailUrl": [thumb(vid), f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"],
            "uploadDate": ep["date"],
            "embedUrl": f"https://www.youtube.com/embed/{vid}",
            "contentUrl": yt,
        },
    }

    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(ep['meta'])}">
<meta name="keywords" content="{esc(keywords)}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="The Inner Circle Podcast">
<meta property="og:title" content="{esc(ep['h1'])}">
<meta property="og:description" content="{esc(ep['meta'])}">
<meta property="og:type" content="video.episode">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{thumb(vid)}">
<meta property="og:video" content="https://www.youtube.com/embed/{vid}">
<meta name="twitter:card" content="summary_large_image">
{FONTS}
<link rel="stylesheet" href="../styles.css">
<script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
</script>
</head>
<body>

{header('episodes', '../')}

<main>
  <article class="wrap article episode">
    <a class="crumb" href="./">&larr; All episodes</a>
    <p class="kicker">Episode {ep['n']}</p>
    <h1>{esc(ep['h1'])}</h1>
    <p class="meta">{nice_date(ep['date'])} · Hosted by DJ Haashim · Filmed in London</p>

    <div class="player yt" id="player">
      <a class="yt-poster" href="{yt}" target="_blank" rel="noopener" data-id="{vid}" aria-label="Play episode {ep['n']} with {esc(ep['guest'])}">
        <img src="{thumb(vid)}" alt="Episode {ep['n']} of The Inner Circle Podcast with {esc(ep['guest'])}" data-fb="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" onerror="if(this.dataset.fb){{this.src=this.dataset.fb;this.removeAttribute('data-fb')}}">
        <span class="play" aria-hidden="true"></span>
      </a>
    </div>

    <div class="body">
{paras}

      <h2>In this episode</h2>
      <ul>
{points}
      </ul>

      <h2>About {esc(ep['guest'])}</h2>
      <p>{esc(ep['about'])}</p>{links}

      <h2>Watch and listen</h2>
      <p>Watch the full episode above or <a href="{yt}" target="_blank" rel="noopener">on YouTube</a>. Listen on Spotify through <a href="https://linktr.ee/theinnercirclepodcast.official" target="_blank" rel="noopener">our links page</a>, and catch the best moments as clips on <a href="https://www.instagram.com/theinnercirclepodcast.official" target="_blank" rel="noopener">Instagram</a> and <a href="https://www.tiktok.com/@theinnercirclepodcast.official" target="_blank" rel="noopener">TikTok</a>.</p>
      <p>The Inner Circle Podcast is hosted by DJ Haashim and filmed at London Media Lounge. Real conversations with founders, creators and innovators on business, mindset and entertainment.</p>
    </div>

    <nav class="ep-nav" aria-label="More episodes">
      {ep_nav}
    </nav>

    <div class="end">
      <a class="btn" href="{yt}" target="_blank" rel="noopener">Watch on YouTube</a>
      <a class="btn ghost" href="./">All episodes</a>
      <a class="btn ghost" href="../sponsor.html">Sponsor the show</a>
    </div>
  </article>
</main>

{footer('../')}
<script>
(function(){{
  var p = document.querySelector('.yt-poster');
  if(!p) return;
  p.addEventListener('click', function(e){{
    e.preventDefault();
    var id = p.getAttribute('data-id');
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube.com/embed/' + id + '?autoplay=1&rel=0&color=white';
    f.title = document.title;
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.allowFullscreen = true;
    p.parentNode.replaceChild(f, p);
  }});
}})();
</script>
</body>
</html>
"""


def index_page(eps):
    cards = "\n".join(card(e, "../") for e in eps)
    ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "The Inner Circle Podcast episodes",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/episodes/{e['slug']}.html", "name": e["h1"]}
            for i, e in enumerate(eps)
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>All episodes | The Inner Circle Podcast</title>
<meta name="description" content="Every episode of The Inner Circle Podcast with DJ Haashim. Long form conversations with founders, creators and innovators on business, mindset and entertainment, filmed in London.">
<link rel="canonical" href="{SITE}/episodes/">
<meta property="og:site_name" content="The Inner Circle Podcast">
<meta property="og:title" content="All episodes | The Inner Circle Podcast">
<meta property="og:description" content="Every episode of The Inner Circle Podcast with DJ Haashim.">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/episodes/">
<meta property="og:image" content="{LOGO}">
<meta name="twitter:card" content="summary_large_image">
{FONTS}
<link rel="stylesheet" href="../styles.css">
<script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
</script>
</head>
<body>

{header('episodes', '../')}

<main>
  <section style="border-top:0">
    <div class="wrap">
      <div class="sec-head">
        <div>
          <h1 style="font-size:clamp(34px,5vw,56px)">All episodes</h1>
          <p class="sub">Every full conversation, newest first. Hosted by DJ Haashim and filmed in London.</p>
        </div>
        <a class="more" href="https://www.youtube.com/@TheInnerCirclePodcastOfficial/videos" target="_blank" rel="noopener">Open the channel on YouTube</a>
      </div>
      <ul class="grid">
{cards}
      </ul>
    </div>
  </section>
</main>

{footer('../')}
</body>
</html>
"""


def update_home(eps):
    path = os.path.join(ROOT, "index.html")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    start, end = "<!-- EPISODES:START -->", "<!-- EPISODES:END -->"
    if start not in src or end not in src:
        raise SystemExit("index.html is missing the EPISODES markers")
    cards = "\n".join(card(e, "") for e in eps[:6])
    block = f"{start}\n      <ul class=\"grid\">\n{cards}\n      </ul>\n      {end}"
    new = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: block, src, flags=re.S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)


def sitemap(eps):
    today = date.today().isoformat()
    pages = [
        ("/", today, "weekly", "1.0"),
        ("/episodes/", today, "weekly", "0.9"),
        ("/sponsor.html", "2026-10-10", "monthly", "0.7"),
        ("/blog/", "2026-10-10", "weekly", "0.6"),
        ("/blog/welcome-to-the-inner-circle.html", "2026-10-01", "yearly", "0.5"),
    ] + [(f"/episodes/{e['slug']}.html", today, "monthly", "0.8") for e in eps]
    items = "\n".join(
        f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{c}</changefreq>\n    <priority>{pr}</priority>\n  </url>"
        for p, d, c, pr in pages
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n'


def main():
    with open(DATA, encoding="utf-8") as f:
        eps = json.load(f)["episodes"]
    eps.sort(key=lambda e: e["n"], reverse=True)
    os.makedirs(OUT, exist_ok=True)
    by_n = {e["n"]: e for e in eps}
    for e in eps:
        prev_ep = by_n.get(e["n"] - 1)
        next_ep = by_n.get(e["n"] + 1)
        with open(os.path.join(OUT, e["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(episode_page(e, prev_ep, next_ep))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(eps))
    update_home(eps)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap(eps))
    print(f"Built {len(eps)} episode pages, episodes/index.html, sitemap.xml and the homepage grid.")


if __name__ == "__main__":
    main()
