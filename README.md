# MuggleNet HBO Harry Potter TV Series — RSS Feed

This repo automatically generates a free, always-updating RSS feed from:
https://mugglenet.com/harry-potter-tv-series/

It re-scrapes the page every 4 hours (via GitHub Actions, free for public repos)
and publishes an `feed.xml` file via GitHub Pages. There's no expiration —
it will keep running for as long as the repo exists and GitHub Actions/Pages
remain free (they currently are, for public repos).

## One-time setup (about 5 minutes)

1. **Create a new GitHub repo** (public), e.g. `mugglenet-rss`.
   - github.com → "New repository" → name it → Create.

2. **Upload these files** to the repo, keeping the folder structure:
   ```
   build_feed.py
   README.md
   .github/workflows/update-feed.yml
   ```
   Easiest way: on the repo page, click "Add file" → "Upload files", drag
   in everything (make sure `.github/workflows/update-feed.yml` ends up in
   that exact nested path).

3. **Enable GitHub Pages**:
   - Repo → Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main`, folder: `/docs`
   - Save.
   - GitHub will show you a URL like:
     `https://yourusername.github.io/mugglenet-rss/`

4. **Update `SELF_URL` in `build_feed.py`** to:
   `https://yourusername.github.io/mugglenet-rss/feed.xml`
   (Edit the file directly in GitHub's web editor, commit the change.)

5. **Run the workflow once manually** to generate the first feed.xml:
   - Repo → Actions tab → "Update RSS Feed" workflow → "Run workflow" button.
   - Wait ~30 seconds, then check the `docs/` folder — `feed.xml` should appear.

6. **Your feed URL** is now:
   `https://yourusername.github.io/mugglenet-rss/feed.xml`

   Paste that into any RSS reader (Feedly, Inoreader, NetNewsWire, etc.).

## Notes

- The scraper pulls the headline list from the "Latest HBO TV Series News"
  section of the page. If MuggleNet redesigns that page, the script's
  `fetch_articles()` function may need a small tweak (selector update).
- Adjust update frequency by editing the `cron` line in
  `.github/workflows/update-feed.yml`.
- Everything here runs on GitHub's free tier — no cost, no expiry date.
