# Game Builder

A terminal agent that builds games with you. Describe a game, and it pitches a plan, writes the code into your folder, runs checks, writes image prompts for the art, and tells you how to play it. It is a standalone command-line app, not a plugin for another coding tool.

```
$ game-builder -C werewolf "a 6-player werewolf game friends can join from their phones"
```

It knows the stacks behind real games: an anime styling game, a Backrooms crawler, a haunted hotel, a Roblox-style campus, a Unity survival-horror game, online werewolf and murder-mystery games, and a Rust terminal life sim.

| Stack | Good for |
|---|---|
| 2D web (canvas + HTML) | dress-up, visual novel, puzzle, card, idle, 2D arcade |
| Three.js, single HTML file | first-person exploration and horror |
| A-Frame, single HTML file | third-person explorable worlds, VR |
| Unity (C#) + GameCI WebGL deploy | third-person action, physics games |
| Next.js + Cloudflare D1 | online multiplayer: werewolf, murder mystery, betrayal games |
| Rust + ratatui | terminal life sims and roguelikes |
| Finite-state-machine NPC AI | guards, enemies and squads in any engine |

Its genre guide covers 15 genres, from dress-up and platformers to social deduction, murder mystery and creature life sims. The playbook, stacks guide and genre guide live in [`gamebuilder/playbook/`](gamebuilder/playbook/).

## Install

Needs Python 3.10+.

```
uv tool install git+https://github.com/wuisabel-gif/game-builder
```

or `pipx install git+https://github.com/wuisabel-gif/game-builder`.

## Sign in

It uses Claude through the Anthropic API. Either set an API key:

```
export ANTHROPIC_API_KEY=sk-ant-...
```

or sign in once with the Anthropic CLI: `ant auth login`.

## Use

```
game-builder                      # chat in the current folder
game-builder -C my-game "idea"    # start in my-game/ with a first request
game-builder -y "..."             # run shell commands without asking each time
```

Inside the chat:
- Type what you want, then keep refining: "make the jump floatier", "add a second level".
- `/serve` serves the game folder (or its `dist/`) at http://127.0.0.1:8000 and opens your browser.
- `/quit` exits. Ctrl-C stops the current step without losing the conversation.

The agent can read and write files only inside the project folder. It asks before every shell command unless you pass `-y`. It cannot see your screen, so it will ask you what the game looks like and fix what you report.

Set `GAME_BUILDER_MODEL` to use a different Claude model (default `claude-opus-5-5`).

### Ideas to try

```
game-builder -C closet "an anime dress-up game with punk and romantic outfits and makeup"
game-builder -C level0 "a Three.js Backrooms walking sim with flickering lights"
game-builder -C campus "an A-Frame campus you explore to collect study tips"
game-builder -C mistwalker "a Unity third-person viking game where draugr ambush you in fog"
game-builder -C nightfall "online werewolf for 6-12 players with AI seats, English and Chinese"
game-builder -C critters "a Rust terminal game where little creatures build a culture"
```

## Develop

```
uv run --with . python tests/test_tools.py
```

## License

MIT
