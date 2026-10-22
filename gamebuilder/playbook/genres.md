# Genre playbooks

The genres that make up most of the PC, console and mobile market. Each entry gives the core
loop, the systems a first version needs, common pitfalls, engines that suit it, and open-source
games on GitHub worth reading for reference. Build the loop first, then add systems in order.

## Action / platformer / metroidvania
- **Loop**: move → jump, dodge or attack → reach the next screen or checkpoint → die → retry in under two seconds.
- **Systems**: fixed-timestep physics separate from rendering; input buffering and coyote time; tile-based levels; checkpoints; camera follow with look-ahead; hit-stop and screen shake; for metroidvanias, ability gates and a map.
- **Pitfalls**: frame-rate-dependent movement; floaty jumps (stronger gravity on the way down); unreadable hazards; no touch controls on mobile.
- **Engines**: Godot, Phaser, Unity, MonoGame, LÖVE.
- **Read on GitHub**: SuperTux/supertux, flareteam/flare-game.

## Roguelike / roguelite
- **Loop**: enter a procedurally generated run → fight and collect → die → keep some progress → start a new run.
- **Systems**: seeded RNG; level generation (rooms and corridors, cellular automata, wave function collapse); turn or real-time combat; item and modifier pools; meta-progression between runs.
- **Pitfalls**: runs that feel the same (vary rooms, enemies and items); unfair deaths from hidden information; balance that only scales numbers.
- **Engines**: Godot, Unity, Bevy, raylib, a terminal (curses or ratatui) for classic roguelikes.
- **Read on GitHub**: 00-Evan/shattered-pixel-dungeon, tmewett/BrogueCE, crawl/crawl, CleverRaven/Cataclysm-DDA, mxgmn/WaveFunctionCollapse.

## RPG (action, turn-based, JRPG, CRPG)
- **Loop**: explore → fight → gain experience and loot → get stronger → unlock the next area or story beat.
- **Systems**: stats and level curve; combat (turn queue or real time); inventory and equipment; quests and dialogue trees; save slots; data-driven items, enemies and abilities.
- **Pitfalls**: content scope (plan one region first); stat bloat; grind instead of choices; save bugs.
- **Engines**: Godot, Unity, Unreal (3D action RPGs), RPG Maker-style 2D in Phaser.
- **Read on GitHub**: GDQuest/godot-open-rpg, OpenMW/openmw, ihhub/fheroes2.

## Shooter (FPS, TPS, top-down, arena)
- **Loop**: move → aim → shoot → take cover → win the encounter or round.
- **Systems**: character controller; hitscan and projectile weapons; recoil and spread; enemy AI with cover and flanking; health, armor and pickups; for online play, authoritative server with lag compensation.
- **Pitfalls**: weak feedback (add hit markers, sound and impact effects); spongy enemies; netcode bolted on late.
- **Engines**: Unreal, Unity, Godot; Three.js or Babylon.js for browser shooters.
- **Read on GitHub**: id-Software/Quake-III-Arena, id-Software/DOOM, assaultcube/AC, Unvanquished/Unvanquished, TeamHypersomnia/Hypersomnia.

## Survival / crafting / sandbox
- **Loop**: gather → craft tools → build shelter → survive threats (hunger, night, enemies) → expand.
- **Systems**: needs meters; resource nodes; crafting recipes as data; building on a grid or voxels; day/night cycle; world saving; often co-op multiplayer.
- **Pitfalls**: an empty midgame (give goals beyond survival); inventory tedium; world size that outgrows performance.
- **Engines**: Unity, Godot, Unreal; voxel engines for block worlds.
- **Read on GitHub**: luanti-org/luanti, veloren/veloren, OpenStarbound/OpenStarbound.

## Strategy (RTS, 4X, turn-based tactics, grand strategy)
- **Loop**: gather resources → build → expand → fight or out-plan rivals → win by conquest, score or victory condition.
- **Systems**: map and fog of war; unit selection and orders; pathfinding (A*, flow fields); economy; tech tree; AI opponents; deterministic lockstep simulation for multiplayer.
- **Pitfalls**: an AI that cannot play the game; information overload; late-game slowdown.
- **Engines**: Unity, Godot, custom C++/C#; Phaser or PixiJS for browser tactics.
- **Read on GitHub**: OpenRA/OpenRA, wesnoth/wesnoth, freeciv/freeciv, yairm210/Unciv, OpenXcom/OpenXcom.

## Tower defense
- **Loop**: enemies walk a path → place and upgrade towers → survive the wave → earn more → harder wave.
- **Systems**: path or flow field; wave table; tower targeting rules (first, strongest, closest); upgrade trees; speed controls.
- **Pitfalls**: one dominant tower; waves that only add health; no information about upcoming enemies.
- **Engines**: Phaser, Godot, Unity.
- **Read on GitHub**: Anuken/Mindustry (tower defense crossed with factory building).

## Simulation and management (city builder, tycoon, colony, farming)
- **Loop**: plan and build → time passes → systems produce money or resources → unlock new buildings → grow.
- **Systems**: tick-based simulation with pause and speed; grid placement; supply and demand chains; agents with needs; budgets; overlays that show what is going wrong.
- **Pitfalls**: hidden causes of failure (show the numbers); inflation that breaks the economy; performance with many agents (data-oriented design helps).
- **Engines**: Unity, Godot, Bevy (ECS suits large simulations), PixiJS for 2D browser sims.
- **Read on GitHub**: OpenTTD/OpenTTD, OpenRCT2/OpenRCT2, bvschaik/julius, CorsixTH/CorsixTH, OpenLoco/OpenLoco.

## Racing
- **Loop**: race → overtake → hit the racing line → finish → unlock cars or tracks.
- **Systems**: vehicle physics (arcade or simulation); track splines and checkpoints; AI drivers following the racing line with rubber-banding; lap timing and ghosts; drift or boost mechanics.
- **Pitfalls**: physics that feel slippery or stiff; AI that is either perfect or useless; poor sense of speed (field of view, motion blur, camera shake).
- **Engines**: Unity, Unreal, Godot; Three.js for browser racers.
- **Read on GitHub**: supertuxkart/stk-code.

## Fighting
- **Loop**: read the opponent → space and attack → land a combo → win the round.
- **Systems**: frame data (startup, active, recovery); hitboxes and hurtboxes per frame; input buffer and motion inputs; combo and cancel rules; rollback netcode for online play.
- **Pitfalls**: inconsistent frame timing; netcode added late (design for rollback early); a cast too large for v1.
- **Engines**: Godot, Unity, custom; MUGEN-style engines.
- **Read on GitHub**: ikemen-engine/Ikemen-GO.

## Sports
- **Loop**: control a player or team → pass, shoot or score → win the match → progress a season.
- **Systems**: ball physics; team AI with positions and roles; rules and referee logic; stamina; season or league mode.
- **Pitfalls**: AI clumping around the ball; controls that hide what the player can do; licensing (use original teams and names).
- **Engines**: Unity, Unreal, Godot.

## Puzzle (match-3, logic, physics puzzle, 2048-style)
- **Loop**: read the board → plan a move → satisfying resolution → slightly harder board.
- **Systems**: board logic as pure functions (easy to test); move validation; cascades; undo; level list with star goals; hints after idle time.
- **Pitfalls**: unsolvable generated boards (generate backwards or verify with a solver); animations that block input.
- **Engines**: Phaser, PixiJS, Godot, Unity; plain canvas for small puzzles.
- **Read on GitHub**: gabrielecirulli/2048, hextris/hextris.

## Casual and hyper-casual mobile
- **Loop**: one tap or swipe mechanic → short session (30-90 s) → score → instant retry.
- **Systems**: one-thumb controls; difficulty ramp; daily rewards; ads or in-app purchases only if the user asks; analytics hooks.
- **Pitfalls**: slow startup; small touch targets; the first ten seconds not showing the fun.
- **Engines**: Unity, Godot, Defold, Cocos, Flutter Flame, Phaser for web.

## Card game / deck builder
- **Loop**: draw → play cards with a limited resource → resolve effects → adjust the deck after the fight.
- **Systems**: deck, hand and discard piles; card effects as small functions keyed by id; enemy intent shown in advance; seeded RNG; for collectible card games, a rules engine and deck validation.
- **Pitfalls**: too many keywords at once; vague card text (show exact numbers); effect ordering bugs (resolve on a stack).
- **Engines**: Godot, Unity, Phaser; boardgame.io for turn-based online card games.
- **Read on GitHub**: Card-Forge/forge, boardgameio/boardgame.io.

## Visual novel / narrative / dating sim
- **Loop**: read → choose → see consequences → reach one of several endings.
- **Systems**: script as data (nodes with speaker, text and choices); flags and affinity; character sprites with expressions; backlog, skip and auto; save slots; gallery of unlocked art.
- **Pitfalls**: walls of text (keep each box short); choices that do not matter; no way to re-read.
- **Engines**: Ren'Py, Monogatari (web), Godot with a dialogue plugin, Unity with Ink or Yarn Spinner.
- **Read on GitHub**: renpy/renpy, Monogatari/Monogatari.

## Dress-up / fashion / avatar creator
- **Loop**: pick an item → see the character change instantly → match a goal or theme → save or share the look.
- **Systems**: layered sprite renderer (body, outfit, hair, face, makeup, accessories); wardrobe thumbnails drawn by the same renderer; undo; themed challenges scored by simple checks; album and image export; share links.
- **Pitfalls**: layers that misalign between poses; a head that does not match body proportions; UI covering the character's face.
- **Engines**: plain canvas or PixiJS, Phaser, Unity for mobile.

## Rhythm
- **Loop**: hear the beat → hit on time → timing grade → build a combo.
- **Systems**: the audio clock as the only timer (Web Audio `currentTime`, `AudioSettings.dspTime` in Unity); charts as timed notes; timing windows; latency calibration; chart editor.
- **Pitfalls**: drift from using frame time; licensed music (use original or CC0 tracks).
- **Engines**: Unity, Godot, Phaser.
- **Read on GitHub**: ppy/osu.

## Idle / incremental
- **Loop**: click or wait → buy a generator → numbers grow faster → prestige for a permanent bonus.
- **Systems**: tick loop with delta time; costs `base * rate^owned`; number formatting (1.2K, 3.4M, scientific); offline progress; prestige layers; a big-number library for very large values.
- **Pitfalls**: dead zones with nothing to buy; floating-point overflow; numbers without new mechanics.
- **Engines**: plain web or Vue/React, Godot, Unity.
- **Read on GitHub**: IvarK/AntimatterDimensionsSourceCode.

## Horror
- **Loop**: explore → sense danger → find a clue, tool or exit → tension spike → relief.
- **Systems**: first-person or fixed camera; limited light and resources; sound as the main signal; a threat with readable rules (it hears noise, it hates light); scripted scares paced by tension.
- **Pitfalls**: darkness that hides the path; jump scares without build-up; motion sickness (offer sensitivity and field-of-view settings).
- **Engines**: Unity, Unreal, Godot; Three.js for browser horror.

## Party and social deduction (werewolf, mafia, murder mystery, betrayal games)
- **Loop**: secret roles or goals → private actions → open discussion → vote or accuse → reveal.
- **Systems**: room codes and invite links; server-authoritative state; per-player private information; phases with timers; voting and win checks; bots for empty seats; spectators.
- **Pitfalls**: leaking private information through the network; rules interactions left undefined; phases that drag; a mystery that cannot be solved from its clues.
- **Engines**: web (Next.js or similar) with Colyseus, Socket.IO or boardgame.io; Unity or Godot with Nakama.
- **Read on GitHub**: boardgameio/boardgame.io, colyseus/colyseus.

## Online multiplayer and MMO
- **Loop**: depends on the genre; multiplayer adds cooperation, competition and a shared world.
- **Systems**: authoritative server; client prediction and reconciliation (action games) or lockstep (strategy); matchmaking and rooms; persistence; anti-cheat basics (never trust the client).
- **Pitfalls**: building multiplayer last; no reconnect handling; server costs (ask before adding paid hosting).
- **Engines**: Colyseus or Socket.IO (web), Nakama (any engine), Unity Netcode, Godot high-level multiplayer.
- **Read on GitHub**: mozilla/BrowserQuest (archived, small browser MMO), TrinityCore/TrinityCore.
