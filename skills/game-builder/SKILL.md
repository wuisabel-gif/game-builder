---
name: game-builder
description: Game-building helper. Plans, builds, art-directs, tests and ships small browser games of any kind — dress-up/styling, visual novel, platformer/arcade, puzzle, cozy sim/management, rhythm, card/deck, idle, or local multiplayer — as a no-build static site deployable to GitHub Pages. Writes layout-exact ChatGPT image prompts for sprites and atlases. Use when the user wants to make, prototype, extend or polish a game, asks "can we make a game where…", names a genre, or invokes /game-builder.
---

# Game Builder

Build a small, finished, good-looking browser game, not a tech demo. Default stack:
plain `index.html` + `style.css` + `app.js` (ES module) + `art.js` in `dist/`, no build
step, canvas for the play area and real HTML for the UI, served by any static server and
published by GitHub Pages. Only reach for a library when the genre clearly needs it
(physics, audio sequencing) and load it from a pinned CDN URL.

## 1. Pitch (one message, then build)

Pin down, defaulting anything the user does not say:
- **Genre and core loop**: what the player does every 10 seconds, and what makes them do it again. See [genres.md](references/genres.md) for the loop, systems and pitfalls of each genre.
- **Fantasy and tone**: setting, characters, references ("like NANA", "like Stardew").
- **Session length and win/lose**: a 2-minute arcade run or a 30-minute story.
- **Platform**: desktop + phone by default; touch controls if there is real-time input.
- **Art plan**: generated sprites (ChatGPT prompts below), CSS/SVG shapes, or emoji placeholders first.

Reply with a short pitch: title, one-line hook, core loop, 3–5 features for v1, and what is deliberately left for later. If the user already gave enough, skip asking and build.

## 2. Build order

1. **Playable loop first** with placeholder art: input → state change → render → feedback. Ugly but fun beats pretty but inert.
2. **Single state object** that is plain JSON. It drives render, save, undo, share links and tests. Validate anything loaded from storage or a URL before using it; migrate old saves with `{...initial, ...saved}`.
3. **Juice**: easing, a short pop/scale on change, screen shake or hit-stop for action games, toast messages, sound only if asked. Respect `prefers-reduced-motion`.
4. **Progression**: goals, stars, unlocks, chapters, a high score or a daily challenge. Reuse one completion list rather than inventing parallel progress systems.
5. **Persistence**: `localStorage` wrapped in try/catch, with a visible fallback message. Never require an account or a backend unless the user asks for multiplayer.
6. **UI polish**: a clear title screen or studio header, readable at 375px wide, no horizontal scroll, focus-visible outlines, keyboard controls listed in a help dialog.

Keep code compact and boring. One data array per content type (levels, outfits, chapters, enemies) so adding content is adding a row.

## 3. Art direction with ChatGPT image prompts

When the game needs illustrated art, write prompts the user pastes into ChatGPT, then wire the returned PNGs in. Every prompt must state:
- Exact canvas size in px, transparent background, PNG.
- Grid: number of columns/rows and each cell's size, in order, with what each cell contains.
- Anchor rules: same head/feet position, scale and angle in every cell, so frames line up.
- What must stay identical to an attached reference, and what alone should change.
- Style: line weight, palette, lighting, "no text, no frame, no background".

When extending existing art, always attach the current sheet and ask for a pixel-for-pixel layout match. Expect a few pixels of drift; correct it in code with per-cell offsets rather than re-prompting forever. Check sizes with `sips -g pixelWidth -g pixelHeight file.png` (macOS) before wiring.

Prefer layered sprites (body, outfit, hair, face, accessories drawn in order) over baking every combination. Tint by recoloring masked pixels instead of drawing color variants.

## 4. Test it like a player

- Expose `window.render_game_to_text()` returning the state as JSON and `window.advanceTime(ms)` stepping the simulation, so the game can be checked without screenshots.
- Run it in the browser: `python3 -m http.server 5174 --directory dist`. Hidden or background browser panes may pause `requestAnimationFrame`; if frames never fire, shim it with `setTimeout` to test the loop. Bust stale CSS/JS with `fetch(file,{cache:'reload'})` before reloading.
- Play the full loop once, win and lose, reload to confirm saving, then check 1440×900, 768×1024 and 375×812 for overlap and overflow. Read console errors.
- Inspect generated art up close (draw an enlarged crop onto an overlay canvas) — seams, doubled features and misaligned layers hide at normal size.

## 5. Ship

- Add a README: what it is, how to play, how to run locally, screenshots, credits. For fan games, add a short "unofficial fan homage, not affiliated" note and keep all text and art original.
- GitHub Pages: a workflow that uploads `dist/` on push to `main`; keep every asset path relative.
- Keep a `progress.md` log of what changed and what was verified, so the next session can pick up.
- Commit only when the user asks.

## Output style

Lead with the playable result. After each build step, show it running (screenshot or browser pane) and say in one or two lines what changed and what is next. Offer the next most fun feature, not a list of ten.
