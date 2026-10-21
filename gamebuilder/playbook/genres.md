# Genre playbooks

Each entry: the core loop, the systems v1 needs, the data shape, and the pitfalls that
usually sink it. Build the loop first, then add systems in the order listed.

## Dress-up / styling
- **Loop**: pick an item → see the character change instantly → compare against a goal → save or share.
- **Systems**: layered sprite renderer (body, outfit, hair, face, makeup, accessories); wardrobe grid with thumbnails rendered from the same renderer; undo/redo; briefs scored by simple checks (`[label, state => bool]`); saved looks album; PNG export; share link (`#` + base64 state).
- **Data**: `{outfit, hair, hairColor, lip, blush, liner, accessory, pose, expression}` as integers.
- **Pitfalls**: atlas cells that bleed into neighbours; a replaced head that does not match body proportions; moving the head separately from the body leaves a seam (animate the whole figure with CSS instead); the UI covering the face.
- **Extras**: story chapters that each map to a brief; a second character who stands behind and can be swapped in; idle breathing and blinking.

## Visual novel / story
- **Loop**: read a line → make a choice → see the consequence → want the next scene.
- **Systems**: script as an array of nodes `{id, speaker, text, choices:[{text, goto, set}]}`; flags object; portrait layer with expressions; backlog; auto/skip; save slots; chapter select after completion.
- **Pitfalls**: walls of text (cap ~200 characters per box); choices that do not matter; no way to re-read.
- **Extras**: affinity meters, multiple endings, a gallery of unlocked CGs.

## Platformer / arcade / action
- **Loop**: move → dodge or attack → score → die → retry in under two seconds.
- **Systems**: fixed-timestep update (e.g. 60 Hz accumulator) separate from render; input map for keyboard, touch buttons and gamepad; AABB collisions; camera follow; particles; hit-stop and screen shake; high score in storage.
- **Data**: levels as tile strings or arrays; entities as `{x, y, vx, vy, w, h, type}`.
- **Pitfalls**: frame-rate-dependent physics; floaty jumps (use higher gravity on the way down, coyote time and jump buffering); unreadable hazards; no touch controls on phones.

## Puzzle (match-3, sliding, logic)
- **Loop**: read the board → plan a move → satisfying resolution → slightly harder board.
- **Systems**: pure board logic separate from animation (testable with asserts); move validation; cascade/resolve loop; undo; level list with star thresholds; hint after idle time.
- **Pitfalls**: unsolvable generated boards (generate by playing backwards or validate with a solver); animations that block input too long.

## Cozy sim / management (café, farm, shop, room decor)
- **Loop**: spend resources → time passes → earn more → unlock something new to place or sell.
- **Systems**: day/tick clock with pause; inventory and prices in one table; customers or crops as timers; placeable grid for decor; unlock tree; offline progress capped to a few hours.
- **Pitfalls**: numbers that inflate too fast; nothing new to see after ten minutes (stagger unlocks); hidden timers (always show progress bars).

## Rhythm
- **Loop**: hear the beat → hit on time → feedback grade → combo.
- **Systems**: Web Audio clock as the single source of time (never `setTimeout`); chart as `[{t, lane}]`; timing windows (perfect/good/miss); latency calibration screen.
- **Pitfalls**: drift from using frame time instead of `audioContext.currentTime`; licensed music (use original or CC0 tracks).

## Card / deck builder
- **Loop**: draw → play cards with a limited resource → resolve → add or remove a card after the fight.
- **Systems**: deck/hand/discard arrays; card effects as small functions keyed by id; enemy intent shown in advance; seeded RNG for reproducible runs.
- **Pitfalls**: too many keywords at once; unclear card text (show exact numbers).

## Idle / incremental
- **Loop**: click or wait → buy a generator → numbers grow faster → prestige.
- **Systems**: tick loop with delta time; costs scaling `base * rate^owned`; number formatting (1.2K, 3.4M); offline gains; prestige reset with a permanent multiplier.
- **Pitfalls**: dead zones with nothing to buy; floating-point overflow past 1e308 (cap or use a big-number lib only when needed).

## Local / online multiplayer
- **Local**: shared keyboard or split touch zones; turn-based hot-seat is the simplest.
- **Online**: needs a server; prefer turn-based over real-time. Keep game rules in one pure function `step(state, action)` that both client and server run. Ask the user before adding any backend, accounts or paid service.
- **Pitfalls**: trusting the client for scores; no reconnect handling.

## Social deduction (werewolf / mafia)
- **Loop**: secret role → night action → day discussion → vote someone out → reveal and suspicion shifts.
- **Systems**: role table (Wolves, Seer, Witch, Hunter, Guard, Villagers) with setups by player count; timed night phases; private wolf chat; turn-based speaking; vote resolution; win checks after every death; a draw after N cycles; rule-based AI seats that can lie.
- **Pitfalls**: leaking private info through the API; ambiguous interaction rules (write them down, e.g. guard + antidote cancel, poison ignores protection); phases that drag (offer a fast mode for AI seats).

## Murder mystery (剧本杀 / script game)
- **Loop**: read your private script → search for clues → share or hide them → private talks → accuse with evidence.
- **Systems**: fixed seats with private scripts (background, secret, timeline, personal goal); search locations with per-round clues; public case file; one-to-one whispers; secret accusation with suspect, key evidence and reasoning; a full reveal of the truth.
- **Pitfalls**: a solution that cannot be deduced from the clues; timers that auto-skip humans (let players confirm before advancing); spoilers on replay (same culprit, warn players).

## Negotiation and betrayal (prisoner's dilemma family)
- **Loop**: negotiate in chat → lock in a secret move → simultaneous reveal → scores change → trust updates.
- **Systems**: many small mode cards sharing one engine (move set and payoff table per mode); 3/5/7 rounds; whispers; recap with awards.
- **Pitfalls**: a dominant strategy that makes talking pointless; unclear payoff tables (always show them).

## Horror exploration / walking sim
- **Loop**: explore → sense something is wrong → find the next clue or exit → tension spike → relief.
- **Systems**: first-person movement; light and sound as the main tools (flicker, blackouts, drones); NPCs or entities that react to the player's attention; collectible lore cards or a quiz.
- **Pitfalls**: darkness that hides everything (keep a readable path); jump scares without build-up; motion sickness (offer sensitivity and FOV settings).

## Third-person action / survival
- **Loop**: move through the world → enemies ambush → fight with timing and positioning → heal on kills → push further.
- **Systems**: character controller and follow camera; melee arc hit detection with cooldowns; enemy archetypes (slow tank, fast runner, animal); spawn waves scaled by score; endless terrain recycling; health and score HUD; a friendly guide NPC for lore.
- **Pitfalls**: unreadable attacks (telegraph wind-ups); enemies stuck on obstacles; difficulty that only ever goes up (add recovery moments).

## Life sim / creature society
- **Loop**: care for creatures → watch them act on their own → intervene (food, eggs, ideas) → see the society change.
- **Systems**: needs (hunger, energy, social) on a tick; simple agents that wander, eat, sleep and meet; ideas or traits that spread and mutate on contact; scarcity pressure; an inspector panel with memories and stats.
- **Pitfalls**: nothing changes without input (seed small random events); runaway population (tie growth to food).
