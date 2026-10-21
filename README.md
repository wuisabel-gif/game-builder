# Game Builder

An MCP server that helps any coding agent build games. Plug it into Claude Code, Codex, Cursor, Windsurf, Gemini CLI or any other MCP client, then say "make me a game where…". Your agent does the thinking and writing with its own model; Game Builder gives it the game know-how and tools. No API key needed.

It is built from real games: an anime styling game, a Backrooms crawler, a haunted hotel, a Roblox-style campus, a Unity survival-horror game, online werewolf and murder-mystery games, and a Rust terminal life sim.

## What your agent gets

| Tool | What it does |
|---|---|
| `plan_game` | Picks a stack for the idea and returns the playbook plus the matching stack and genre guides, so the agent can pitch before building. |
| `get_guide` | Any stack or genre on demand: "unity", "three.js", "werewolf", "murder mystery", "platformer"… |
| `scaffold_game` | Writes a playable starter (2D web, Three.js first person, A-Frame world) with a GitHub Pages workflow; returns setup steps for Unity, online multiplayer, Rust terminal and NPC AI projects. Never overwrites a folder. |
| `image_prompt` | Writes a layout-exact prompt for ChatGPT or another image model, so generated sprite sheets line up with the code. |
| `check_game` | Finds missing asset files, JavaScript syntax errors and PNG sizes. |
| `serve_game` | Serves the game at http://127.0.0.1 so you can play it. |

It also offers the guides as resources (`gamebuilder://playbook`, `gamebuilder://stacks`, `gamebuilder://genres`) and a `new_game` prompt.

| Stack | Good for |
|---|---|
| 2D web (canvas + HTML) | dress-up, visual novel, puzzle, card, idle, 2D arcade |
| Three.js, single HTML file | first-person exploration and horror |
| A-Frame, single HTML file | third-person explorable worlds, VR |
| Unity (C#) + GameCI WebGL deploy | third-person action, physics games |
| Next.js + Cloudflare D1 | online multiplayer: werewolf, murder mystery, betrayal games |
| Rust + ratatui | terminal life sims and roguelikes |
| Finite-state-machine NPC AI | guards, enemies and squads in any engine |

The genre guide covers 15 genres, from dress-up and platformers to social deduction, murder mystery and creature life sims.

## Install

Needs [uv](https://docs.astral.sh/uv/) (or Python 3.10+ with pipx). The server runs with:

```
uvx --from git+https://github.com/wuisabel-gif/game-builder game-builder
```

Add it to your agent:

**Claude Code**
```
claude mcp add game-builder -- uvx --from git+https://github.com/wuisabel-gif/game-builder game-builder
```

**Codex** (`~/.codex/config.toml`)
```toml
[mcp_servers.game-builder]
command = "uvx"
args = ["--from", "git+https://github.com/wuisabel-gif/game-builder", "game-builder"]
```

**Cursor** (`.cursor/mcp.json`), **Windsurf**, **Claude Desktop** and most other clients use the same JSON shape:
```json
{
  "mcpServers": {
    "game-builder": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/wuisabel-gif/game-builder", "game-builder"]
    }
  }
}
```

**Gemini CLI** (`~/.gemini/settings.json`): the same `mcpServers` block.

## Use

Ask your agent, for example:

- "Use game-builder to make an anime dress-up game with punk and romantic outfits."
- "Make a Three.js Backrooms walking sim with flickering lights."
- "Build an online werewolf game for 6–12 players with AI seats, in English and Chinese."
- "Set up a Unity third-person viking game where draugr ambush you in fog."
- "Write the image prompt for a 4-frame walk cycle, 256 × 256 per frame."

The agent plans, scaffolds, builds, checks and serves the game, and asks you what you see in the browser.

## Develop

```
uv run --with . python tests/test_tools.py
```

## License

MIT
