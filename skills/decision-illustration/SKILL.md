---
name: decision-illustration
description: Add a side-by-side illustration to every decision in a decisions file (for example the output of the decision-debate skill). Each illustration is 1200×600, SVG + PNG - the rejected option on the left in a red dashed frame with ✕, the chosen option on the right in a solid green frame with ✓, under a 4–6 word title that states the rule. Use when the user wants decisions visualized, illustrated or turned into images or slides.
---

# Decision illustration

Add such an illustration to every decision. Input: a file of decisions shaped like "We decided X instead of Y, because Z" (the output of **decision-debate**), or decisions the user lists. If a decision has no rejected option, take the strongest alternative from the source doc or the debate.

## The spec
Decision illustration, 1200×600, SVG + PNG.
Title on top: the rule in 4–6 words.
Two side-by-side scenes, nothing else:
- **Left:** the rejected option. Red dashed frame, ✕.
- **Right:** the chosen option. Solid green frame, ✓.

Each scene shows:
- one concrete artifact (URL bar, invoice, member list, run log…)
- one real monospace technical line from the source doc (query / URL / role binding)
- a 2–4 word consequence label

Show the dilemma itself, not characters arguing. One idea per illustration, ~2 elements and ~2 words per side. No dialogue, paragraphs or side notes. Min font 20px.

## Step 1: plan every illustration before drawing
For each decision write one row:

| ID | Title (4–6 words) | Artifact | Left line | Left label | Right line | Right label |
|---|---|---|---|---|---|---|
| D1 | One subdomain per clinic | URL bar | `Set-Cookie: sid=9f2; Path=/` | Cookie shared | `Set-Cookie: __Host-sid=9f2; Path=/` | Cookie isolated |

- **Same artifact on both sides**, so the eye compares only what changed.
- **The technical line is real**: copied from the decisions file, the debate or the user's docs. If none exists, write the line the chosen option would really produce. Never pseudo-code.
- **The title is the rule**, not the topic: "One subdomain per clinic", not "Tenant isolation".
- **The label is the consequence**, not the option name: "Cookie shared", not "Path prefix".

## Step 2: draw the SVG
Use this layout. Fixed coordinates keep every illustration in a set consistent.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600">
  <rect width="1200" height="600" fill="#ffffff"/>
  <!-- title: 40px bold, centered -->
  <text x="600" y="72" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="40" font-weight="700" fill="#1a1a1a">TITLE</text>

  <!-- left scene: rejected -->
  <rect x="40" y="120" width="540" height="440" rx="18" fill="#fff5f5" stroke="#d32f2f" stroke-width="5" stroke-dasharray="18 12"/>
  <circle cx="80" cy="160" r="24" fill="#d32f2f"/>
  <text x="80" y="170" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="30" font-weight="700" fill="#fff">✕</text>
  <!-- artifact: y 200–340 · tech line strip: y 370–420 · label: y 500 -->

  <!-- right scene: chosen -->
  <rect x="620" y="120" width="540" height="440" rx="18" fill="#f3faf3" stroke="#2e7d32" stroke-width="5"/>
  <circle cx="660" cy="160" r="24" fill="#2e7d32"/>
  <text x="660" y="170" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="30" font-weight="700" fill="#fff">✓</text>
</svg>
```

Inside each scene (inner width ~480px, starting 30px from the frame):
- **Artifact**, y 200–340: draw it as the real thing in miniature: a browser bar with the URL, an invoice with one line and a total, a member list with 2–3 rows, a terminal with one log line. Text inside it 22–26px.
- **Technical line**, y 370–420: a dark strip (`#1e1e1e`, rx 8) with the line in monospace 20–22px, light text. At 22px a line fits ~32 characters; at the 20px minimum ~36. Use the same size on both sides. If it's longer, cut the irrelevant part, never shrink below 20px.
- **Consequence label**, baseline y 500: 32px bold, red `#c62828` on the left, green `#2e7d32` on the right.

Write text as real `<text>` (no outlined paths), escape `&` and `<`, and never let text cross a frame.

## Step 3: render the PNG
Render each SVG at 1200×600. Use what's available, in this order:
1. `rsvg-convert -w 1200 -h 600 D1.svg -o D1.png`
2. Headless Chromium / Playwright: open the SVG, set the viewport to 1200×600, screenshot.
3. `magick D1.svg D1.png` (ImageMagick; check that fonts and ✕ ✓ rendered).

Open the PNG and look at it. Fix overflow, clipped glyphs or missing ✕/✓ before moving on.

## Step 4: attach to the decisions
Save as `illustrations/D1-one-subdomain-per-clinic.svg` and `.png` next to the decisions file, and add the image right under its decision:

```markdown
**D1.** We decided each clinic gets its own subdomain instead of a path prefix, because a login at one clinic must never be valid at another.

![One subdomain per clinic](illustrations/D1-one-subdomain-per-clinic.png)
```

## Checklist per illustration
- 1200×600, both SVG and PNG exist.
- Title is 4–6 words and states the rule.
- Left: red dashed frame + ✕. Right: solid green frame + ✓.
- Each side: one artifact, one real monospace line, one 2–4 word label. Nothing else.
- No people, speech bubbles, arrows between sides, legends, footnotes or paragraphs.
- No text under 20px.
