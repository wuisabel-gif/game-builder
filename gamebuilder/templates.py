"""Starter projects for the no-build web stacks. Each is a playable loop to grow from."""

PAGES_WORKFLOW = """name: Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: __PATH__
      - id: deployment
        uses: actions/deploy-pages@v4
"""

WEB2D = {
    "dist/index.html": """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><link rel="stylesheet" href="style.css"></head>
<body>
<header><h1>__TITLE__</h1><p id="score" role="status">Score 0 · Best 0</p></header>
<main><canvas id="game" width="640" height="400" aria-label="Game area"></canvas>
<p class="hint">Arrow keys or WASD to move. Tap or click to move on touch screens.</p></main>
<div id="toast" role="status" aria-live="polite"></div>
<script type="module" src="app.js"></script>
</body></html>
""",
    "dist/style.css": """:root{--bg:#f3ecdc;--ink:#29241f;--accent:#671d30;--line:#ccc2b1}
*{box-sizing:border-box}body{margin:0;min-height:100svh;background:var(--bg);color:var(--ink);font-family:Georgia,serif;display:grid;grid-template-rows:auto 1fr}
header{display:flex;justify-content:space-between;align-items:baseline;padding:16px 20px;border-bottom:1px solid var(--line)}h1{margin:0;font-size:clamp(24px,4vw,40px)}
main{display:grid;place-items:center;padding:16px}canvas{width:min(100%,640px);height:auto;background:#fffaf0;border:1px solid var(--line);touch-action:none}
.hint{font:14px system-ui,sans-serif;opacity:.7}
#toast{position:fixed;left:50%;bottom:20px;translate:-50% 120px;background:var(--accent);color:#fff;padding:10px 18px;font:14px system-ui,sans-serif;transition:translate .25s}
#toast.show{translate:-50% 0}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
""",
    "dist/app.js": """// One plain state object drives rendering, saving and tests.
const canvas = document.querySelector('#game'), ctx = canvas.getContext('2d');
const initial = { x: 320, y: 200, star: { x: 120, y: 120 }, score: 0, best: 0 };
let state = structuredClone(initial);
try { const saved = JSON.parse(localStorage.getItem('__SLUG__') || 'null'); if (Number.isInteger(saved?.best)) state.best = saved.best; } catch {}
const save = () => { try { localStorage.setItem('__SLUG__', JSON.stringify({ best: state.best })); } catch {} };
const keys = new Set(), speed = 220;
let target = null;
addEventListener('keydown', e => keys.add(e.key.toLowerCase()));
addEventListener('keyup', e => keys.delete(e.key.toLowerCase()));
canvas.addEventListener('pointerdown', e => { const r = canvas.getBoundingClientRect(); target = { x: (e.clientX - r.left) * canvas.width / r.width, y: (e.clientY - r.top) * canvas.height / r.height }; });

function toast(text) { const t = document.querySelector('#toast'); t.textContent = text; t.classList.add('show'); clearTimeout(toast.timer); toast.timer = setTimeout(() => t.classList.remove('show'), 1500); }

function update(dt) {
  let dx = (keys.has('arrowright') || keys.has('d')) - (keys.has('arrowleft') || keys.has('a'));
  let dy = (keys.has('arrowdown') || keys.has('s')) - (keys.has('arrowup') || keys.has('w'));
  if (target && !dx && !dy) { dx = target.x - state.x; dy = target.y - state.y; if (Math.hypot(dx, dy) < 4) target = null; }
  const len = Math.hypot(dx, dy) || 1;
  state.x = Math.max(16, Math.min(canvas.width - 16, state.x + dx / len * speed * dt * (dx || dy ? 1 : 0)));
  state.y = Math.max(16, Math.min(canvas.height - 16, state.y + dy / len * speed * dt * (dx || dy ? 1 : 0)));
  if (Math.hypot(state.x - state.star.x, state.y - state.star.y) < 28) {
    state.score++; state.star = { x: 30 + Math.random() * (canvas.width - 60), y: 30 + Math.random() * (canvas.height - 60) };
    if (state.score > state.best) { state.best = state.score; save(); }
    if (state.score % 5 === 0) toast(`${state.score} stars!`);
  }
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#d9a441'; ctx.beginPath(); ctx.arc(state.star.x, state.star.y, 12, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#671d30'; ctx.beginPath(); ctx.arc(state.x, state.y, 16, 0, Math.PI * 2); ctx.fill();
  document.querySelector('#score').textContent = `Score ${state.score} · Best ${state.best}`;
}

// Fixed-step loop so speed does not depend on frame rate.
let last = performance.now(), acc = 0;
function frame(now) { acc += Math.min(0.25, (now - last) / 1000); last = now; while (acc >= 1 / 60) { update(1 / 60); acc -= 1 / 60; } render(); requestAnimationFrame(frame); }
requestAnimationFrame(frame);

// Test hooks: inspect state and step time without a screen.
window.render_game_to_text = () => JSON.stringify(state);
window.advanceTime = ms => { for (let t = 0; t < ms; t += 1000 / 60) update(1 / 60); render(); };
""",
}

THREEJS = {
    "index.html": """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>html,body{margin:0;height:100%;background:#000;overflow:hidden;font-family:Georgia,serif}
#start{position:fixed;inset:0;display:grid;place-items:center;color:#f3ecdc;background:#000c;cursor:pointer;text-align:center}
#start h1{font-size:clamp(32px,6vw,64px);margin:0}#walk{position:fixed;right:20px;bottom:20px;width:72px;height:72px;border-radius:50%;border:0;font-size:28px;display:none}
@media(pointer:coarse){#walk{display:block}}</style>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
</head><body>
<div id="start"><div><h1>__TITLE__</h1><p>Click to enter · WASD to walk · mouse to look · Esc to release</p></div></div>
<button id="walk" aria-label="Walk forward">▲</button>
<script type="module">
import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1612); scene.fog = new THREE.Fog(0x1a1612, 2, 28);
const camera = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, 0.1, 100); camera.position.set(0, 1.6, 0);
const renderer = new THREE.WebGLRenderer({ antialias: true }); renderer.setSize(innerWidth, innerHeight); renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
document.body.append(renderer.domElement);

// Level: a grid of walls ('#') and floor ('.'). Edit the map to change the space.
const MAP = ['##########', '#........#', '#..##....#', '#..#..#..#', '#.....#..#', '#.###....#', '#........#', '##########'];
const SIZE = 3, walls = [];
const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: 0x6b5a3a }));
floor.rotation.x = -Math.PI / 2; scene.add(floor);
const wallGeo = new THREE.BoxGeometry(SIZE, 3, SIZE), wallMat = new THREE.MeshStandardMaterial({ color: 0xc9b36a });
MAP.forEach((row, z) => [...row].forEach((c, x) => {
  if (c !== '#') return;
  const m = new THREE.Mesh(wallGeo, wallMat); m.position.set((x - 4.5) * SIZE, 1.5, (z - 3.5) * SIZE); scene.add(m); walls.push(m);
}));
scene.add(new THREE.AmbientLight(0xfff2cc, 0.25));
const lantern = new THREE.PointLight(0xffd59a, 3, 12); camera.add(lantern); scene.add(camera);
const lamps = [0, 1, 2].map(i => { const l = new THREE.PointLight(0xfff0c0, 2, 10); l.position.set((i - 1) * 6, 2.8, 0); scene.add(l); return l; });

const controls = new PointerLockControls(camera, document.body);
document.querySelector('#start').onclick = () => controls.lock();
controls.addEventListener('lock', () => document.querySelector('#start').style.display = 'none');
controls.addEventListener('unlock', () => document.querySelector('#start').style.display = 'grid');
const keys = new Set(); addEventListener('keydown', e => keys.add(e.code)); addEventListener('keyup', e => keys.delete(e.code));
let touchWalk = false; const walk = document.querySelector('#walk');
walk.onpointerdown = () => touchWalk = true; walk.onpointerup = walk.onpointerleave = () => touchWalk = false;

const box = new THREE.Box3();
function blocked(pos) { return walls.some(w => box.setFromObject(w).expandByScalar(0.3).containsPoint(new THREE.Vector3(pos.x, 1, pos.z))); }

const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), 0.1), speed = 3.2 * dt;
  const before = camera.position.clone();
  if (keys.has('KeyW') || touchWalk) controls.moveForward(speed);
  if (keys.has('KeyS')) controls.moveForward(-speed);
  if (keys.has('KeyA')) controls.moveRight(-speed);
  if (keys.has('KeyD')) controls.moveRight(speed);
  if (blocked(camera.position)) camera.position.copy(before);
  lamps.forEach(l => { l.intensity = Math.random() < 0.01 ? 0.2 : 2; }); // flicker
  renderer.render(scene, camera);
});
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });
window.render_game_to_text = () => JSON.stringify({ x: camera.position.x, z: camera.position.z });
</script>
</body></html>
""",
}

AFRAME = {
    "index.html": """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<script src="https://aframe.io/releases/1.5.0/aframe.min.js"></script>
<style>#card{position:fixed;left:50%;bottom:24px;translate:-50% 0;max-width:min(520px,90vw);background:#f3ecdc;color:#29241f;padding:16px 20px;font:16px/1.5 Georgia,serif;box-shadow:0 6px 24px #0005;display:none}
#progress{position:fixed;top:12px;left:12px;background:#29241fcc;color:#f3ecdc;padding:8px 12px;font:14px system-ui,sans-serif}</style>
<script>
// Walk into a signboard to open its card and count it as found.
const found = new Set();
AFRAME.registerComponent('signboard', {
  schema: { text: { type: 'string' } },
  tick() {
    const cam = document.querySelector('[camera]').object3D.position, here = this.el.object3D.position;
    const near = cam.distanceTo(here) < 2.5, card = document.querySelector('#card');
    if (near) {
      card.textContent = this.data.text; card.style.display = 'block'; this.wasNear = true;
      if (!found.has(this.el.id)) { found.add(this.el.id); document.querySelector('#progress').textContent = `Found ${found.size} / ${document.querySelectorAll('[signboard]').length}`; }
    } else if (this.wasNear) { card.style.display = 'none'; this.wasNear = false; }
  },
});
window.render_game_to_text = () => JSON.stringify({ found: [...found] });
</script>
</head><body>
<div id="progress">Found 0 / 3</div><div id="card" role="status"></div>
<a-scene fog="type: linear; color: #cfe3f2; near: 10; far: 60" renderer="antialias: true">
  <a-sky color="#cfe3f2"></a-sky>
  <a-plane rotation="-90 0 0" width="80" height="80" color="#7fb069"></a-plane>
  <a-box id="sign-1" signboard="text: Sign one. Replace this with your first idea." position="-6 1 -8" width="2" height="1.4" depth="0.2" color="#8c5a3c"></a-box>
  <a-box id="sign-2" signboard="text: Sign two. Each board teaches one thing." position="6 1 -14" width="2" height="1.4" depth="0.2" color="#8c5a3c"></a-box>
  <a-box id="sign-3" signboard="text: Sign three. Find them all to finish." position="0 1 -24" width="2" height="1.4" depth="0.2" color="#8c5a3c"></a-box>
  <a-entity camera look-controls wasd-controls="acceleration: 40" position="0 1.6 0"></a-entity>
  <a-entity light="type: ambient; intensity: 0.6"></a-entity><a-entity light="type: directional; intensity: 0.8" position="2 6 3"></a-entity>
</a-scene>
</body></html>
""",
}

STARTERS = {
    "web2d": (WEB2D, "dist", "python3 -m http.server 5174 --directory dist"),
    "threejs": (THREEJS, ".", "python3 -m http.server 8000"),
    "aframe": (AFRAME, ".", "python3 -m http.server 8000"),
}

# Stacks with a toolchain of their own: the agent sets these up by following the steps.
SETUP_STEPS = {
    "unity": "Create the project in Unity Hub (Unity 6, Built-In or URP). Add Input System and Cinemachine from the Package Manager. "
             "Then write scripts into Assets/Scripts following the Unity section of the stacks guide, add a .gitignore for Library/ Temp/ Logs/ UserSettings/, "
             "enable Git LFS for models, and add a GameCI workflow for a WebGL build deployed to GitHub Pages.",
    "multiplayer": "Run `npx create-next-app@latest <folder> --ts --app`, add drizzle-orm, drizzle-kit and wrangler, define rooms/players/events tables, "
                   "and put every rule in pure functions under lib/ with tests in tests/game.mjs. Follow the online multiplayer section of the stacks guide.",
    "rust-tui": "Run `cargo new <folder>`, then `cargo add ratatui crossterm rand`. Keep the simulation in its own module with a fixed tick and a --seed flag, "
                "and draw with ratatui. Follow the terminal game section of the stacks guide.",
    "npc-fsm": "Create the FSM module (PATROL, CHASE, ATTACK, SEARCH, RETURN) behind a small world adapter, plus a mock world and a terminal demo. "
               "Follow the NPC AI section of the stacks guide.",
}
