# Stacks guide

Each stack lists when to use it, the project layout, how to run and deploy it, and the
lessons from real games built with it. Choose one per game; do not mix engines.

## 2D web (canvas + HTML UI)
- **Use for**: dress-up, visual novel, puzzle, card, idle, 2D arcade, cozy sim.
- **Layout**: `dist/index.html`, `dist/style.css`, `dist/app.js` (ES module: state, UI, saving), `dist/art.js` (drawing and sprite compositing), `dist/assets/`. No build step.
- **Run**: `python3 -m http.server 5174 --directory dist`. **Deploy**: GitHub Pages workflow uploading `dist/`.
- **Lessons** (from an anime styling game): render every view (stage, thumbnails, export) through one `renderDoll(state)` function; cache the expensive render and redraw only when the state key changes; animate the whole figure with CSS (`sway`, `breathe`) rather than moving layers separately, which leaves seams; keep UI controls clear of the character's face; second characters can share the renderer with a separate saved state.

## Three.js first person (single HTML file)
- **Use for**: walkable 3D spaces, horror crawlers, museums, liminal spaces, exploration.
- **Layout**: one `index.html` with an import map pinning `three` from a CDN (exact version), plus `assets/` for `.glb` models, textures and sounds. Serve over HTTP because models and audio stream.
- **Core**: `PointerLockControls` for mouse look, WASD with simple AABB collision against a wall grid, fog and a few point lights for mood, a lantern light parented to the camera, instanced meshes for repeated geometry (carpet tiles, ceiling lights).
- **Mood tricks**: flickering lights on random timers, ambient drone generated with Web Audio (no audio files needed), random blackouts, NPCs that react when you linger.
- **Touch**: drag to look and a hold-to-walk button.
- **Lessons** (from a Backrooms crawler and a haunted hotel): procedural levels beat hand-placed ones for endless spaces; keep draw calls low with instancing and merged geometry; credit CC models and lore sources in the README.

## A-Frame third-person world (single HTML file)
- **Use for**: Roblox-style explorable campuses or towns, educational worlds, VR-friendly scenes.
- **Layout**: one `index.html`; generate pixel-art textures and building layouts with a Python script (`gen_textures.py`, `build_*.py`) that bakes them into the HTML as data URIs and JSON.
- **Core**: third-person camera rig, WASD movement, trigger zones that open info cards, collectibles and a progress meter, NPC dialogue on proximity, a finishing celebration.
- **Lessons** (from a campus world based on a book): teach content by placing it in the world (walk up to a signboard to learn one idea); keep a public progress log and ROADMAP.

## Unity (C#)
- **Use for**: third-person action, physics-heavy games, anything needing an editor, animation rigs or a console-like feel.
- **Layout**: standard Unity project (`Assets/Scripts`, `Assets/Scenes`, `Packages/manifest.json`, `ProjectSettings`), Git LFS for models, a `.gitignore` for `Library/`, `Temp/`, `Logs/`, `UserSettings/`.
- **Core architecture** (from a Norse survival-horror game): small `MonoBehaviour`s wired in the scene and no god-object manager; one scene singleton only for score; Input System action maps; Cinemachine third-person camera; `CharacterController` movement with a ground raycast; enemies that chase and steer around obstacles with `SphereCast` probes; trigger volumes that spawn waves scaled by score; an endless-terrain treadmill that recycles tiles; health bar and score HUD.
- **Deploy**: GameCI GitHub Actions workflow builds WebGL on every push (it also proves the project compiles) and deploys `main` to GitHub Pages. Needs `UNITY_LICENSE`/`UNITY_EMAIL`/`UNITY_PASSWORD` secrets, which the user adds themselves.
- **Limits**: you cannot open the Unity editor. Write scripts, prefabs-as-code where possible, and exact editor steps for the user (which object, which component, which field). Document tuning numbers in a README table.

## Online multiplayer (Next.js + Cloudflare D1)
- **Use for**: social deduction (werewolf), murder mystery, negotiation and betrayal games, party games for 2-12 players on separate devices.
- **Layout**: Next.js app (`app/`, `components/`, `lib/` for pure rules), Drizzle ORM schema (`db/`, `drizzle/` migrations), deployed to Cloudflare (Workers + D1) with `wrangler`.
- **Core rules**: server-authoritative state; clients only send actions and poll (about every 1.2 s) or subscribe; optimistic concurrency with a version number on the room; five-character room codes and invite links; no login, a nickname and one seat per browser tab; refresh restores the same seat.
- **Privacy**: the server returns private information (roles, night actions, whispers) only to the players allowed to see it, including after the game ends where the rules say so.
- **Bots**: fill empty seats with rule-based AI that sees only what a human in that seat would see; label them clearly; no LLM or API key required.
- **Extras**: bilingual UI chosen per player (English, Chinese, Japanese), host settings (setup size, timers, AI speed), spectators for late joiners, a round-by-round recap and awards.
- **Tests**: `tests/game.mjs` for pure rules (night resolution, win conditions), `tests/api.mjs` for the room flow, `tests/i18n.mjs` for missing translation keys.

## Terminal game (Rust + ratatui)
- **Use for**: life sims, roguelikes, idle games, cozy creature games that live in a terminal.
- **Layout**: Cargo project; `ratatui` + `crossterm` for the native TUI, `rand` for the world; behind `cfg(target_arch = "wasm32")`, `wasm-bindgen` builds the same simulation for a `web/` page.
- **Core**: fixed-tick simulation separate from drawing; seeded RNG (`--seed`) for reproducible worlds; themes; an inspector panel that shows one creature's state and memories; emergent systems (ideas spreading between creatures, scarcity pressure) rather than scripted events.
- **Run**: `cargo run --release`; tests with `cargo test`; record a demo GIF for the README.

## NPC AI (finite-state machines)
- **Use for**: guards, enemies and squads in any engine.
- **Core**: states PATROL, CHASE, ATTACK, SEARCH, RETURN with explicit transition conditions; keep the FSM deterministic and engine-independent behind a small `world` adapter (perception, navigation, animation, damage live in the host); squad alerts are a host feature (radio within range).
- **Test**: a mock world and a terminal demo that prints state transitions.
