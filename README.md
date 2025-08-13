<p align="center">
  <img src="assets/logo.jpg?v=INIT" alt="Company logo" height="150">
</p>

# Capital Commitment Tracker

**Campaign:** Quansight Initiate Fund III, L.P.  
**Goal:** $10,000,000 USD
<br>
![Capital Commitments Thermometers](./thermometer.svg?v=20250811154832-16885081679-1)

## What this shows
- **10 mini thermometers** side by side, each representing **$1,000,000** of the $10M goal.
- **Solid red fill** grows upward as capital commitments increase.
- **Bulb:** white at $0; turns **red** once the segment > $0.
- **Tube:** white background, light gray outline.
- **Ticks:** Major every **$100k**, minor every **$50k**.
- Tracks **capital commitments** (not cash collections).

## Viewing your index.html page
If you are trying to view your index.html file inside GitHub’s repo UI, GitHub does not render HTML there; it shows the source. To see the page rendered, use one of the options below.

A) Publish the page via GitHub Pages (recommended)
In your repo: Settings → Pages
Build and deployment → Source: “Deploy from a branch”
Branch: main • Folder: / (root) • Save

Your site will be at:
https://<your-username>.github.io/<your-repo>

Now your index.html (logo + title + thermometer) will render at that URL.

B) Show it directly in the README (so it appears on the repo page)

Add this html to README.md so the logo and chart display on the repo homepage:

```
<p align="center">
  <img src="assets/logo.jpg?v=INIT" alt="Company logo" height="72">
</p>

Capital Commitments Progress
![Capital Commitments Thermometers](./thermometer.svg?v=INIT)
(Your workflow can auto-bump ?v=; if you added the sed lines it’ll stay fresh.)
```
C) Preview locally
Just open index.html in your browser (double-click), or run a quick server:

bash
python -m http.server 8080
then visit http://localhost:8080/

If the page is not displaying properly, you may need to clear your cache.

## Clearing Cache
Sometimes your browser or the CDN caches an older HTML file. Use one of these methods to force a refresh:

A) Open your GitHub Pages URL (not the repo view):
https://<your-username>.github.io/<your-repo>/
(If you use a custom domain, use that instead.)

B) Add a cache-buster to the page URL:
Append ?v=now to force a fresh fetch of index.html.
Example: https://<your-username>.github.io/<your-repo>/?v=now

C) Hard refresh the page:

Windows/Linux: Ctrl + F5 or Ctrl + Shift + R

macOS: Cmd + Shift + R

If images still look stale:
Many sites add a ?v= number to image URLs (e.g., thermometer.svg?v=123…, assets/logo.svg?v=123…).

Check the page source and confirm the image URLs include ?v= so the browser pulls fresh copies.

## Why this works
Adding ?v=now makes the page URL unique, so the browser/CDN won’t reuse a cached HTML response.

If your build also appends ?v= to image URLs, the new HTML will point to new image URLs, which forces fresh images too.

## Finding your GitHub Pages URL
In your repo: Settings → Pages → under GitHub Pages, use the “Visit site” link (or note the listed URL).

Make sure Pages is set to Deploy from a branch and points to the folder where index.html lives (often main / (root)).

More information about GitHub Pages and Publishing Sources: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages

## How to update numbers
Edit `data/funds.json` and set the 10 values in `"segments"` (dollars). Example:
```json
{
  "goal": 10000000,
  "currency": "USD",
  "label": "Quansight Initiate Fund III, L.P.",
  "segments": [1000000, 1000000, 750000, 0, 0, 0, 0, 0, 0, 0]
}
```

## License
© 2025 Bradden Blair, Ph.D. Licensed under the Apache License, Version 2.0.  
See `LICENSE` and `NOTICE` for details. Please preserve copyright and license notices.  
Brand assets in `/assets` are not covered by the code license (see `/assets/LICENSE`).
