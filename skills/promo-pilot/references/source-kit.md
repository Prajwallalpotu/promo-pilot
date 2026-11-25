# The source kit: give brag a real project

brag makes great videos because it animates **real material**: a product's actual UI, copy, colours, fonts and images. Its only limit is that it expects a project folder. promo-pilot removes that limit by building one: a **source kit** in `promo-output/source/`, full of real material, from whatever the user gave. brag then works on the kit the way it works on any project.

A video can only be as good as its source. A thin kit gives a clip-art video, no matter how good the animation is. That's why this step has a gate.

## What goes in the kit

```
promo-output/source/
├── index.html          a real, designed one-page site for the subject (brag reads this like a project's main page)
├── styles.css          the brand system: exact colours, fonts (@font-face to files in fonts/), radii, spacing
├── fonts/              the brand's own font files (or a chosen pair, for text-only input)
├── assets/             real images, logo (SVG preferred), product shots, cutouts, video clips
├── ASSETS.md           one line per asset: file · what it shows · where it came from · rights note
├── COPY.md             the real copy to use: headline, tagline, claims, CTA (each with its source)
├── BRAND.md            (URL input) the brand brief: what they sell, products, real lines, voice, colours, fonts, logo
├── site/               (URL input) site-map.json, logo-candidates/, logo-check.png from site_map.py
└── capture/            (URL input) one `hyperframes capture` per chosen page: capture/home, capture/<page>, …
```

## Building it, by input

### A website URL: understand the site, not just one page

The home page is mostly marketing. The real products, the story and the best images are often one click away. So map the site first, capture a few chosen pages, and find the logo properly. **Don't crawl the whole site:** a 25-second video needs 6–10 great assets, not thousands of pages. Crawling is slow, noisy, and many sites forbid it.

1. **Map the site** (about 10–20 seconds; it respects robots.txt, waits between requests, and runs nothing it downloads):
   ```bash
   python3 <skill-dir>/scripts/site_map.py <url> -o promo-output/source/site --pages <N> --browser "$(<hf> browser path)"
   ```
   `<N>` comes from the tier (tiers.md): 2 on min, 3 on mid, 5 on max. It writes `site/site-map.json` with:
   - `pages`: the user's page first, then the most useful pages (products, features, pricing, about, campaigns), ranked from the menu, footer and sitemap. They stay inside the section the user linked (for example `/in/en/` stays India and English).
   - `logo_candidates`: every real logo it found (header logo, structured-data logo, press or brand page downloads, app icons, manifest icons), downloaded to `site/logo-candidates/`.
   - `logo_check_png`: every candidate drawn on **light and dark** backgrounds on one sheet.
   - `brand`: site name, title, description, slogan, theme colour, menu labels, social links.
   - `notes`: blocked pages, robots.txt limits, missing logo.
2. **Pick the logo by looking, not by name.** Open `site/logo-check.png`. Choose the **brand's own primary mark** (not a parent company, sub-brand, partner or customer logo), preferring SVG. If it disappears on one background, it's single-colour (often `currentColor`): set its fill to the brand's ink for that background, or use the light or dark variant the site also ships. Copy it to `assets/logo.svg` (plus `logo-on-dark.svg` if needed). If no candidate is right, use media-use's logo route (theSVG, favicon), or ask the user for the file. **Never redraw it.**
3. **Capture the chosen pages**, the user's page in full and the others lighter:
   ```bash
   <hf> capture <page 1 url> -o promo-output/source/capture/home --json
   <hf> capture <page N url> -o promo-output/source/capture/<short-name> --max-screenshots 6 --json
   ```
   Each gives screenshots, downloaded images and SVGs, markup with `@font-face` rules (`extracted/page.html`), colour tokens (`extracted/tokens.json`), visible text (`extracted/visible-text.txt`) and animations. Read hyperframes `references/film.md` → *From a website* for brand tokens, fonts and thin captures. Skip a page `site-map.json` marks as disallowed, and keep the total to the tier's page count.
4. **Write `BRAND.md`, the brand brief,** from all of it: what they sell, the 3–5 key products or offers, their real headline and tagline (word for word, with the page it came from), their voice (playful, premium, technical…), the colours (the accent is the colour that recurs across the most roles, per film.md), the fonts, and the chosen logo. brag's plan builds on this brief, so the video tells the brand's real story.
5. **Pick the material.** From every capture, choose the hero or campaign visual, product shots, lifestyle photos and anything from the logo step, and copy them into `assets/` with clear names. Write `ASSETS.md`. Look at each candidate image; filenames lie.
6. **Take the real copy** into `COPY.md`: headlines, taglines, product names and claims from the `visible-text.txt` files, word for word, each with its page. For a real brand, use **its** lines, never invented ones.
7. **Brand system:** the exact colours from `tokens.json`, and the fonts with their `@font-face` rules. Write `styles.css`.
8. **Videos on the site** are often the best footage: `<hf> capture --video promo-output/source/capture/<page> --list`, then `--index N`.
9. **Write `index.html`:** a clean page that uses these assets and copy in the site's own style. brag reuses its markup and styles.
10. **Thin or blocked:** if site_map can't fetch the page, robots.txt forbids it, or a capture is thin (no assets, "very little text content", a bot wall), tell the user in one line and ask for 3–6 images and the logo, or offer the HeyGen route below. Don't continue on drawings, and don't try to get around a block.

### A project folder

This is brag's home ground: the folder already *is* the kit. If the project has a live site, also capture it for marketing images. Skip the rest of this file.

### Text only (a description, no site)

The kit has to be gathered. In order of quality:
1. **The user's own files**: logo, product photos, screenshots, shop photos, clips. Always the best source. The storyboard message invites them in one line.
2. **HeyGen asset search** (free with a HeyGen sign-in, 75k+ images) through media-use: real photos for each scene's subject (food, a café, a team, a city). Search per storyboard beat, and pick photos that match each other in light and colour.
3. **Generated images or shots** through media-use `generate` (HeyGen credits; only when the user agrees to spend them), for a specific product image nobody has a photo of.
4. **Local FLUX** (`mflux`), if installed.
5. **Nothing visual available:** design a **typography-led** film. Make the brand's words the visual, with bold type, colour fields, brand shapes and registry blocks. Tell the user once that photos or a free HeyGen sign-in would make it much stronger.

Then write `COPY.md` from the user's words (never invent facts, per the ground rules), choose a brand system that fits the tone, and build `index.html` as a real landing page for the subject.

## Logos

Use the brand's own file, chosen by looking at it: from `site/logo-check.png` for a website, then media-use's logo route (theSVG, favicon, GitHub avatar), then the user. **Never redraw a logo** or set the brand name in a similar font as a stand-in. Check the final pick on the video's actual background colour.

## Cutouts

To make a product or person move on its own layer (a bottle sliding in, a dish rising, a person in front of type), cut it out of a real photo with `<hf> remove-background <in> -o assets/<name>-cutout.png`. This is how real material becomes motion design, instead of drawing the object.

## Gate: don't plan until this passes

- [ ] (URL) `site-map.json` exists, the tier's pages are captured, `BRAND.md` is written, and the logo was picked from `logo-check.png`.
- [ ] Every storyboard beat has real material to show: a real image, footage, the real UI or logo, or (typography-led only) the real copy.
- [ ] No beat depends on drawing a real-world object (product, packaging, food, person, device, building) with CSS or SVG shapes.
- [ ] `COPY.md` holds the real lines, each with its source.
- [ ] The fonts and colours are the brand's own, or a chosen system for text-only input.
- [ ] `ASSETS.md` notes rights: the user's own, captured from their site, HeyGen licensed, or someone else's brand (then permission, or a visible "spec ad / not official" label).

If a beat has no real material, change the beat. Don't draw the object.
