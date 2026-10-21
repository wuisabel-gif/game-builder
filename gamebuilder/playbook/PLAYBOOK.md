# Game Builder playbook

Build a small, finished, good-looking game, not a tech demo. Pick the stack that fits
the game (see the stacks guide), start from a playable loop, then polish.

## 1. Pitch (one message, then build)

Pin down, defaulting anything the user does not say:
- **Genre and core loop**: what the player does every 10 seconds, and why they do it again. The genre guide lists the loop, systems and pitfalls of each genre.
- **Stack**: 2D web, Three.js first person, A-Frame world, Unity, online multiplayer, terminal, or NPC AI library. Default to the lightest stack that can deliver the game.
- **Fantasy and tone**: setting, characters, references ("like NANA", "like the Backrooms").
- **Session length and win/lose**: a 2-minute arcade run or a 45-minute mystery.
- **Platform**: desktop and phone by default; touch controls for real-time input.
- **Art plan**: generated images (prompts below), procedural shapes and textures, free models, or placeholders first.

Reply with a short pitch: title, one-line hook, core loop, stack, 3-5 features for v1, and what waits for later. If the user already gave enough, skip asking and build.

## 2. Build order

1. **Playable loop first** with placeholder art: input, state change, render, feedback. Ugly but fun beats pretty but inert.
2. **One plain state object** (JSON-serializable) drives render, save, undo, share links and tests. Validate anything loaded from storage, a URL or the network; migrate old saves with `{...initial, ...saved}`.
3. **Juice**: easing, a short pop on change, screen shake or hit-stop in action games, toasts, ambient sound when it fits. Respect `prefers-reduced-motion`.
4. **Progression**: goals, stars, unlocks, chapters, a high score or a daily challenge. Reuse one completion list instead of parallel progress systems.
5. **Persistence**: `localStorage` wrapped in try/catch for single-player web games, with a visible fallback message. No accounts or backend unless the game is online multiplayer.
6. **UI polish**: a clear title or lobby screen, readable at 375 px wide, no horizontal scroll, visible keyboard focus, controls listed in a help dialog.

Keep code compact and boring. One data array per content type (levels, outfits, chapters, enemies, roles) so adding content means adding a row.

## 3. Art direction with image prompts

When the game needs illustrated art, write prompts the user pastes into an image model (ChatGPT, Midjourney and so on), then wire the returned files in. Every prompt states:
- Exact canvas size in px, transparent background, PNG.
- Grid: columns and rows, each cell's size, and what each cell contains, in order.
- Anchors: same head and feet position, scale and angle in every cell, so frames line up.
- What must match an attached reference exactly, and the one thing that changes.
- Style: line weight, palette, lighting, and "no text, no frame, no background".

When extending existing art, ask the user to attach the current sheet and request a pixel-for-pixel layout match. Expect a few pixels of drift and correct it in code with per-cell offsets. Check image sizes before wiring them in (`sips -g pixelWidth -g pixelHeight` on macOS, `file` or Python elsewhere).

Prefer layered sprites (body, outfit, hair, face, accessories) over baking every combination. Recolor by tinting masked pixels instead of drawing color variants. For 3D, prefer procedural geometry and generated textures, or CC0 `.glb` models with credits.

## 4. Test it

- Web games expose `window.render_game_to_text()` (state as JSON) and `window.advanceTime(ms)` so logic can be checked without a screen.
- Keep rules in pure functions and add a small runnable check (a `node tests/game.mjs`, `cargo test`, or Python asserts) for scoring, win/lose and any rule with branches.
- Syntax-check what you wrote (`node --check file.js`, `python3 -m py_compile`, `cargo check`, `dotnet build` where available).
- You cannot see the screen. After each milestone, tell the user exactly how to run it (`/serve` in this tool serves the project) and what to look at, and ask them to report what they see.
- Read console errors and logs the user pastes back, and fix the root cause.

## 5. Ship

- README: what it is, how to play, how to run locally, screenshots, credits. Fan games get a short "unofficial fan homage, not affiliated" note, with all text and art original.
- Static games: a GitHub Pages workflow that uploads the game folder on push to `main`; keep asset paths relative.
- Keep a `progress.md` log of what changed and what was verified, so the next session can continue.
- Never commit, push or publish unless the user asks.

## Working style

Lead with the playable result. After each step, say in one or two lines what changed, how to see it, and what is next. Offer the next most fun feature, not a list of ten. Ask before adding paid services, accounts, servers or large dependencies.
