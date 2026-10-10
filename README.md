# The Inner Circle Podcast website

The files for theinnercirclepodcast.co.uk. Cloudflare publishes this site automatically whenever the files here change (project `theinnercirclepodcast-site`, account theinnercirclepodcast.official@gmail.com).

To change the site, ask Claude. Do not edit wrangler.jsonc.

## Adding an episode

1. Add the episode to `tools/episodes.json` (newest first is not required; pages are sorted by number).
2. Run `python3 tools/build_episodes.py` from the repo root. It rewrites `episodes/`, the homepage grid and `sitemap.xml`.
3. Commit and push. Cloudflare redeploys in under a minute.

Google Search Console is verified for the domain (TXT record in Cloudflare DNS) and `sitemap.xml` is submitted.
