# Stacks guide

The engines and frameworks most used for games on GitHub and in the market. Each entry says
when to choose it, how to start, how to ship, and what to watch out for. Choose one stack per
game. Prefer the lightest stack that can deliver the game: a browser game ships to everyone
with a link; a desktop or console game needs an engine.

## 2D web (Phaser, PixiJS, KAPLAY or plain canvas)
- **Choose for**: puzzle, casual, idle, card, dress-up, visual novel, 2D arcade and platformers that should run from a link.
- **Start**: no build step: `dist/index.html`, `style.css`, `app.js` as an ES module, assets in `dist/assets/`, libraries from a pinned CDN URL. Grow into Vite + TypeScript when the code passes a few thousand lines. Phaser (phaserjs/phaser) gives scenes, physics and input; PixiJS (pixijs/pixijs) is a fast renderer when you want your own game loop; KAPLAY (kaplayjs/kaplay) is the quickest for jams.
- **Ship**: GitHub Pages or itch.io; keep every asset path relative.
- **Watch out**: frame-rate-dependent movement (use a fixed timestep); blurry pixel art (`image-rendering: pixelated`, integer scaling); touch controls and small screens; audio that only starts after a user gesture.

## 3D web (Three.js, Babylon.js, PlayCanvas, A-Frame)
- **Choose for**: first-person exploration, horror, museums, small racers and shooters that run in a browser, WebXR.
- **Start**: one `index.html` with an import map pinning `three` to an exact version (mrdoob/three.js); Babylon.js (BabylonJS/Babylon.js) for a fuller engine with physics and an inspector; PlayCanvas (playcanvas/engine) for an editor workflow; A-Frame for declarative scenes and VR.
- **Core**: pointer-lock mouse look, WASD, simple collision against a level grid or a physics library, fog and few lights for mood, instanced or merged meshes for repeated geometry, `.glb` models.
- **Ship**: GitHub Pages or itch.io; serve over HTTP because models and audio stream.
- **Watch out**: draw calls and texture size on phones; motion sickness (field-of-view and sensitivity settings); credit CC models and sounds.

## Godot (GDScript or C#)
- **Choose for**: most 2D games and small-to-mid 3D games on desktop, mobile and web; the most-starred open-source engine (godotengine/godot).
- **Start**: create the project in the Godot editor; scenes as reusable nodes; scripts in GDScript. Read godotengine/godot-demo-projects, GDQuest/godot-open-rpg and godotengine/tps-demo.
- **Core**: signals over direct references; autoloads only for truly global state; resources (`.tres`) for data such as items and enemies; `_physics_process` for movement.
- **Ship**: export templates for Windows, macOS, Linux, Android, iOS and Web; a GitHub Action (for example with a headless Godot export) builds every push; web exports deploy to GitHub Pages or itch.io.
- **Watch out**: Godot 3 and Godot 4 APIs differ (target 4.x); C# projects cannot export to web; keep scene files small so merges stay easy.

## Unity (C#)
- **Choose for**: mobile games, 3D action, VR/AR, and teams that want the largest asset store and hiring pool.
- **Start**: create the project in Unity Hub; Input System and Cinemachine packages; scripts in `Assets/Scripts`; a `.gitignore` for `Library/`, `Temp/`, `Logs/`, `UserSettings/`; Git LFS for models and textures.
- **Core**: small single-purpose `MonoBehaviour`s wired in the scene; ScriptableObjects for data; events instead of a god-object manager; object pooling for bullets and enemies.
- **Ship**: GameCI GitHub Actions build WebGL, desktop and mobile on every push (it also proves the project compiles); WebGL deploys to GitHub Pages. The user adds `UNITY_LICENSE`, `UNITY_EMAIL` and `UNITY_PASSWORD` secrets.
- **Watch out**: an agent cannot click in the editor, so give exact editor steps (object, component, field); scene merge conflicts (one owner per scene, or prefabs); runtime fees and license terms (check the current Unity terms).

## Unreal Engine (C++ and Blueprints)
- **Choose for**: high-end 3D, realistic shooters and open worlds, cinematic games; free source access through Epic's GitHub organization after linking an Epic account.
- **Start**: create the project in the Epic launcher; gameplay framework classes (GameMode, Character, PlayerController); C++ for systems, Blueprints for tuning and level logic. Read tomlooman/ActionRoguelike for a clean C++ example.
- **Ship**: packaged builds per platform; large repositories need Git LFS or Perforce.
- **Watch out**: long compile times and large downloads; too heavy for small 2D or browser games; royalty terms above a revenue threshold (check current terms).

## Bevy (Rust)
- **Choose for**: simulation-heavy games, many entities, and Rust developers; data-driven ECS (bevyengine/bevy).
- **Start**: `cargo new <game>`, `cargo add bevy`; systems as plain functions over components; plugins per feature; enable dynamic linking during development for faster builds.
- **Ship**: native builds per platform; web through `wasm32-unknown-unknown` and `wasm-bindgen`.
- **Watch out**: the API changes between releases (pin the version and follow its migration guide); no visual editor, so lean on code and tools such as LDtk or Tiled.

## MonoGame and FNA (C#)
- **Choose for**: 2D games with full control in C#, the XNA lineage that shipped many indie hits (MonoGame/MonoGame, FNA-XNA/FNA).
- **Start**: `dotnet new` with the MonoGame templates; a content pipeline for assets; your own scene and entity structure.
- **Ship**: desktop and console ports; mobile with more work.
- **Watch out**: you build the engine pieces yourself (UI, scenes, tweening); keep it small.

## libGDX (Java or Kotlin)
- **Choose for**: 2D and light 3D games across desktop, Android, iOS and web from one Java/Kotlin codebase (libgdx/libgdx); Shattered Pixel Dungeon uses it, and Mindustry runs on Arc, a libGDX fork.
- **Start**: the gdx-liftoff project generator; screens, a `SpriteBatch`, Scene2D for UI.
- **Watch out**: web export through TeaVM or GWT has limits; plan Android from day one if it is the main target.

## raylib (C and many bindings)
- **Choose for**: learning, jams and small games where you want a simple library instead of an engine (raysan5/raylib); bindings exist for most languages.
- **Start**: one `main.c` with the init, update and draw loop; add modules as the game grows.
- **Ship**: native builds; web through Emscripten.
- **Watch out**: no editor or scene system; keep scope small.

## LÖVE (Lua)
- **Choose for**: fast 2D prototyping and jams (love2d/love).
- **Start**: `main.lua` with `love.load`, `love.update(dt)`, `love.draw`; libraries for tweening, cameras and collisions.
- **Ship**: `.love` files and fused executables; web through community ports.
- **Watch out**: mobile and web exports need extra tooling.

## Defold (Lua)
- **Choose for**: lightweight 2D games, especially mobile and HTML5, with small builds (defold/defold).
- **Start**: the Defold editor; game objects, components and message passing.
- **Watch out**: message-passing style takes adjustment; smaller community than Godot or Unity.

## Pygame and Pyxel (Python)
- **Choose for**: teaching, prototypes, and retro games in Python; Pygame (pygame/pygame) for general 2D, Pyxel (kitao/pyxel) for 16-colour retro games with built-in sprite and sound editors.
- **Start**: one `main.py` with the game loop; `pip install pygame` or `pip install pyxel`.
- **Ship**: Pyxel exports to web; Pygame web via pygbag; desktop via PyInstaller.
- **Watch out**: performance with many sprites; packaging for players who do not have Python.

## Flutter Flame (Dart)
- **Choose for**: casual mobile games, or games inside a Flutter app (flame-engine/flame).
- **Start**: `flutter create`, `flutter pub add flame`; a `FlameGame` with components.
- **Watch out**: heavier than dedicated 2D engines for action games.

## Visual novels (Ren'Py, Monogatari)
- **Choose for**: visual novels, dating sims and branching stories. Ren'Py (renpy/renpy) is the standard for desktop and mobile; Monogatari (Monogatari/Monogatari) runs in the browser.
- **Start**: Ren'Py `script.rpy` with labels, menus and character definitions; Monogatari's script object in JavaScript.
- **Watch out**: save compatibility when the script changes (keep label names stable); long scripts need a style guide for characters' voices.

## Online multiplayer (Colyseus, Nakama, Socket.IO, boardgame.io)
- **Choose for**: party and social deduction games, co-op, competitive matches and persistent worlds.
- **Options**: Colyseus (colyseus/colyseus) for room-based Node.js servers with state sync; Nakama (heroiclabs/nakama) for accounts, matchmaking and storage across engines; Socket.IO (socketio/socket.io) for custom real-time messaging; boardgame.io (boardgameio/boardgame.io) for turn-based games with rules written as pure functions.
- **Core rules**: the server owns the game state and validates every action; clients send intents, not results; private information (roles, hands, whispers) goes only to the players allowed to see it; room codes and reconnects; bots for empty seats.
- **Ship**: a host that runs a long-lived server (ask the user before adding paid hosting); the client deploys like any web or engine build.
- **Watch out**: building multiplayer last; trusting the client; no plan for reconnects or late joiners.

## Art and level tools
- **Aseprite** (aseprite/aseprite): pixel art and animation; export sprite sheets with JSON frame data.
- **Tiled** (mapeditor/tiled) and **LDtk** (deepnight/ldtk): tile-based level editors with loaders for most engines.
- **Image models**: use the playbook's prompt rules (exact canvas, grid and anchors) so generated sheets line up with code.
- **Audio**: sfxr-style generators for effects; CC0 or original music, credited in the README.
- **Lists to explore**: ellisonleao/magictools, Calinou/awesome-gamedev, godotengine/awesome-godot.
