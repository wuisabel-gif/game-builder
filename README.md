# Game Builder

A Claude Code helper for making small, finished browser games — dress-up, visual novel, platformer, puzzle, cozy sim, rhythm, card, idle and local multiplayer. It turns "can we make a game where…" into a playable static site, writes layout-exact ChatGPT image prompts for sprite sheets, tests the game like a player, and ships it to GitHub Pages.

Built from what we learned making [AFTER SCHOOL](https://github.com/wuisabel-gif/after-school), an anime styling game ([play it](https://wuisabel-gif.github.io/after-school/)).

## Install

In Claude Code:

```
/plugin marketplace add wuisabel-gif/game-builder
/plugin install game-builder@game-builder
```

Or copy `skills/game-builder` into `~/.claude/skills/`.

## Use

```
/game-builder a cozy café game where you style the barista for each customer
```

Or just describe a game; Claude picks the skill up on its own.

## What it does

1. **Pitch** — genre, core loop, v1 features and what waits for later.
2. **Build** — a no-build static site (`index.html`, `style.css`, `app.js`, `art.js`): playable loop first, then juice, progression, saving and UI polish.
3. **Art** — ChatGPT prompts with exact canvas size, grid, anchors and style, so generated sprites line up; then wires the PNGs in.
4. **Test** — `render_game_to_text()` / `advanceTime()` hooks, desktop, tablet and phone checks, close-up art inspection.
5. **Ship** — README, GitHub Pages workflow and a progress log.

Genre playbooks (loop, systems, data shape, pitfalls) live in [`skills/game-builder/references/genres.md`](skills/game-builder/references/genres.md).

## License

MIT
