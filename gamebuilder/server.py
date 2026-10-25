"""Game Builder MCP server: game-making know-how and tools for any MCP-capable coding agent.

The host agent (Claude Code, Codex, Cursor, ...) does the thinking and file editing with its
own model; this server supplies the playbook, starters, art prompts, checks and a local server.
"""

import asyncio
import re
import shutil
import struct
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path

from mcp.server.mcpserver import Image, MCPServer

from . import __version__
from .templates import PAGES_WORKFLOW, SETUP_STEPS, STARTERS

GUIDES = ("PLAYBOOK.md", "stacks.md", "genres.md")

mcp = MCPServer(
    "game-builder",
    version=__version__,
    instructions=(
        "Game Builder helps you make games. Start a new game with plan_game, then follow its guidance: "
        "pitch, scaffold_game, build the playable loop, check_game and playtest_game after each change, serve_game so the user can play. "
        "Use get_guide for any stack or genre, and image_prompt when the game needs generated art. "
        "Pass absolute folder paths."
    ),
)


def guide(name: str) -> str:
    return (files("gamebuilder") / "playbook" / name).read_text(encoding="utf-8")


def sections() -> dict[str, str]:
    """Every '## ' section of the stacks and genre guides, keyed by lowercase heading."""
    out = {}
    for name in GUIDES[1:]:
        for chunk in re.split(r"(?m)^(?=## )", guide(name)):
            if chunk.startswith("## "):
                out[chunk.splitlines()[0][3:].strip().lower()] = chunk.strip()
    return out


# Engines named outright win; then multiplayer and story words; then 3D words choose
# Godot, or 3D web when the idea says it runs in a browser; everything else is 2D web.
NAMED = [
    ("unity", ("unity",)), ("unreal", ("unreal",)), ("godot", ("godot",)), ("bevy", ("bevy",)),
    ("monogame", ("monogame", "fna", "xna")), ("libgdx", ("libgdx",)), ("raylib", ("raylib",)),
    ("löve", ("love2d", "löve")), ("defold", ("defold",)), ("pygame", ("pygame", "pyxel", "python")),
    ("flutter flame", ("flutter", "flame")), ("visual novels", ("ren'py", "renpy", "monogatari")),
    ("3d web", ("three.js", "threejs", "babylon", "babylon.js", "playcanvas", "a-frame", "aframe", "webxr")),
    ("2d web", ("phaser", "pixijs", "kaplay", "canvas")),
]
STACK_HINTS = [
    ("online multiplayer", ("multiplayer", "online", "mmo", "werewolf", "mafia", "murder mystery", "social deduction", "party game", "co-op", "pvp")),
    ("visual novels", ("visual novel", "dating sim", "branching story", "interactive fiction")),
]
THREE_D = ("3d", "first-person", "first person", "fps", "third-person", "third person", "shooter", "racing", "open world", "vr", "horror", "souls")
BROWSER = ("browser", "web", "itch", "link")


def has(text: str, words) -> bool:
    return any(re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", text) for w in words)


GENERIC = {"game", "games", "action", "online", "mobile", "builder", "creator", "simulation", "first", "person"}


def pick_stack(idea: str) -> str:
    text = idea.lower()
    for stack, words in NAMED + STACK_HINTS:
        if has(text, words):
            return stack
    if has(text, THREE_D):
        return "3d web" if has(text, BROWSER) else "godot"
    return "2d web"


def find_sections(query: str, all_sections: dict[str, str]) -> list[str]:
    query = query.lower()
    hits = [k for k in all_sections if query in k or k.split(" (")[0] in query]
    if not hits:  # fall back to word overlap with headings
        words = set(re.findall(r"[a-z0-9]+", query))
        hits = [k for k in all_sections if words & set(re.findall(r"[a-z0-9]+", k)) - {"and", "the", "game", "games", "web"}]
    return hits


@mcp.tool()
def plan_game(idea: str, stack: str = "") -> str:
    """Start a new game. Returns the playbook, the recommended stack's guide and matching genre
    guides for the idea. Use it to write a short pitch (title, hook, core loop, stack, 3-5 v1
    features, what waits for later) before building. `stack` overrides the automatic choice."""
    all_sections = sections()
    stack_key = next(iter(find_sections(stack, all_sections)), None) if stack else None
    stack_key = stack_key or next(k for k in all_sections if k.startswith(pick_stack(idea)))
    idea_words = set(re.findall(r"[a-z]+", idea.lower()))
    genre_names = [k for k in sections_of("genres.md") if idea_words & (set(re.findall(r"[a-z]{4,}", k)) - GENERIC)]
    parts = [f"# Plan for: {idea}", f"Recommended stack: {stack_key}", guide("PLAYBOOK.md"), all_sections[stack_key]]
    parts += [all_sections[g] for g in genre_names[:3]] or ["No genre matched by name; call get_guide('genres') to pick the closest."]
    return "\n\n".join(parts)


def sections_of(name: str) -> list[str]:
    return [line[3:].strip().lower() for line in guide(name).splitlines() if line.startswith("## ")]


@mcp.tool()
def get_guide(topic: str) -> str:
    """Return guidance: 'playbook', 'stacks', 'genres', or any stack or genre name
    (e.g. 'unity', 'three.js', 'werewolf', 'murder mystery', 'platformer')."""
    whole = {"playbook": "PLAYBOOK.md", "stacks": "stacks.md", "genres": "genres.md"}
    if topic.lower().strip() in whole:
        return guide(whole[topic.lower().strip()])
    all_sections = sections()
    hits = find_sections(topic, all_sections)
    if not hits:
        return "No match. Topics: playbook, stacks, genres, or one of:\n" + "\n".join(f"- {k}" for k in all_sections)
    return "\n\n".join(all_sections[k] for k in hits[:3])


@mcp.tool()
def scaffold_game(folder: str, stack: str, title: str) -> str:
    """Create a playable starter in an empty or new folder. `stack` is one of: web2d, threejs,
    aframe (files are written), or godot, unity, unreal, bevy, monogame, libgdx, raylib, love, pygame,
    flame, renpy, multiplayer (setup steps are returned).
    Use an absolute folder path."""
    stack = stack.lower().strip()
    if stack in SETUP_STEPS:
        return f"{stack} needs its own toolchain, so no files were written. Steps:\n{SETUP_STEPS[stack]}"
    if stack not in STARTERS:
        return f"Unknown stack {stack!r}. Choose one of: {', '.join([*STARTERS, *SETUP_STEPS])}."
    root = Path(folder).expanduser()
    if not root.is_absolute():
        return "Pass an absolute folder path."
    if root.exists() and any(root.iterdir()):
        return f"{root} is not empty. Choose a new or empty folder so nothing is overwritten."
    tree, publish, run = STARTERS[stack]
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "game"
    written = []
    for rel, text in {**tree, ".github/workflows/pages.yml": PAGES_WORKFLOW.replace("__PATH__", publish),
                      "progress.md": f"# {title}\n\nStarted from the Game Builder {stack} starter.\n"}.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.replace("__TITLE__", title).replace("__SLUG__", slug), encoding="utf-8")
        written.append(rel)
    return (f"Created {title} in {root}:\n" + "\n".join(f"- {w}" for w in written)
            + f"\n\nRun it: cd {root} && {run}  (or call serve_game). Next: replace the placeholder loop with the game's core loop.")


@mcp.tool()
def image_prompt(subject: str, columns: int, cell_width: int, cell_height: int, cells: list[str],
                 rows: int = 1, style: str = "", keep_from_reference: str = "", change: str = "") -> str:
    """Write a layout-exact prompt for an image model (ChatGPT, Midjourney, ...) to generate a
    sprite sheet that lines up with the game's code. `cells` describes each cell in reading order.
    When extending existing art, describe what must stay identical in `keep_from_reference` and the
    one thing that changes in `change`; the user should attach the current sheet."""
    width, height = columns * cell_width, rows * cell_height
    lines = [
        f"Create a game sprite sheet: {subject}.",
        "",
        "Layout (must match exactly, it is read by code):",
        f"- Canvas {width} × {height} px, transparent background, PNG.",
        f"- {columns} column(s) × {rows} row(s); every cell is {cell_width} × {cell_height} px.",
        "- Cells in reading order (left to right, top to bottom):",
        *[f"  {i + 1}. {c}" for i, c in enumerate(cells)],
        "- Same scale, angle and anchor in every cell: head and feet at the same height, centered in the cell.",
        "- Nothing crosses a cell edge.",
    ]
    if keep_from_reference:
        lines += ["", "Keep identical to the attached reference, pixel for pixel:", f"- {keep_from_reference}"]
    if change:
        lines += ["", f"Change only this: {change}"]
    lines += ["", f"Style: {style or 'match the reference'}.", "No text, no frame, no background, no shadows outside the subject."]
    return "\n".join(lines)


def png_size(path: Path):
    with path.open("rb") as f:
        head = f.read(24)
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", head[16:24])
    return None


REF = re.compile(r"""(?:src|href)=["']([^"'#?]+)|url\(["']?([^"')#?]+)|from\s+["'](\.[^"']+)["']|["']((?:\./)?assets/[^"']+\.(?:png|jpe?g|webp|gif|svg|glb|gltf|mp3|ogg|wav|json))["']""")


@mcp.tool()
def check_game(folder: str) -> str:
    """Check a game folder: missing local files referenced from HTML/CSS/JS, JavaScript syntax
    errors (when Node.js is installed) and PNG sizes. Run after each change. Use an absolute path."""
    root = Path(folder).expanduser()
    if not root.is_dir():
        return f"{folder} is not a folder."
    skip = {"node_modules", ".git", "Library", "target", ".next"}
    source = [p for p in root.rglob("*") if p.suffix in {".html", ".css", ".js", ".mjs"} and not skip & set(p.parts)]
    missing, syntax = [], []
    for p in source:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for groups in REF.findall(text):
            ref = next(g for g in groups if g)
            if re.match(r"^(?:[a-z]+:|//|data:|\$\{|/)", ref) or "${" in ref:
                continue
            if not (p.parent / ref).exists() and not (root / ref).exists():
                missing.append(f"{p.relative_to(root)} → {ref}")
    node = shutil.which("node")
    if node:
        for p in source:
            if p.suffix in {".js", ".mjs"}:
                r = subprocess.run([node, "--check", str(p)], capture_output=True, text=True)
                if r.returncode:
                    syntax.append(f"{p.relative_to(root)}:\n{r.stderr.strip()[-800:]}")
    images = []
    for p in sorted(root.rglob("*.png")):
        size = None if skip & set(p.parts) else png_size(p)
        if size:
            images.append(f"{p.relative_to(root)}: {size[0]}×{size[1]}")
    report = [f"Checked {len(source)} source files in {root}."]
    report.append("Missing files:\n" + "\n".join(f"- {m}" for m in missing) if missing else "No missing local files.")
    report.append(("Syntax errors:\n" + "\n\n".join(syntax)) if syntax else ("JavaScript syntax OK." if node else "Node.js not found; skipped the JavaScript syntax check."))
    if images:
        report.append("PNG sizes:\n" + "\n".join(f"- {i}" for i in images[:60]))
    return "\n\n".join(report)


servers: dict[str, tuple[subprocess.Popen, int]] = {}


@mcp.tool()
def serve_game(folder: str, port: int = 8000) -> str:
    """Serve a game folder over http://127.0.0.1 so the user can play it in a browser (serves
    dist/ when present). Keeps running until the agent session ends. Use an absolute path."""
    root = Path(folder).expanduser()
    if not root.is_dir():
        return f"{folder} is not a folder."
    web = root / "dist" if (root / "dist" / "index.html").exists() else root
    key = str(web.resolve())
    if key in servers and servers[key][0].poll() is None:
        return f"Already serving {web} at http://127.0.0.1:{servers[key][1]}/"
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", key],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        proc.wait(timeout=0.8)  # exits at once if the port is taken
        return f"Could not start the server on port {port} (probably in use). Try another port."
    except subprocess.TimeoutExpired:
        servers[key] = (proc, port)
        return f"Serving {web} at http://127.0.0.1:{port}/ . Ask the user to open it and say what they see."


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):  # stdout and stderr belong to the MCP connection
        pass


ACTION = re.compile(r"^(press|hold|click|type|wait|advance):(.+)$")
STATE_JS = "() => typeof window.render_game_to_text === 'function' ? String(window.render_game_to_text()) : null"


async def launch_browser(playwright):
    try:
        return await playwright.chromium.launch()
    except Exception as e:
        if "Executable doesn't exist" not in str(e):
            raise
    # First run: download the headless browser, keeping its output off the MCP stdio channel.
    proc = await asyncio.create_subprocess_exec(sys.executable, "-m", "playwright", "install", "chromium",
                                                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE)
    _, err = await proc.communicate()
    if proc.returncode:
        raise RuntimeError(f"could not install Chromium: {err.decode()[-400:]}")
    return await playwright.chromium.launch()


@mcp.tool(structured_output=False)
async def playtest_game(folder: str, actions: list[str] | None = None, width: int = 1280, height: int = 800,
                        page: str = "index.html") -> list:
    """Play a web game in a headless browser and see the result: returns a screenshot taken after
    the actions, console and page errors, failed asset loads, and the game's state from
    window.render_game_to_text() before and after (when the game defines it).
    Actions run in order: 'press:ArrowRight' taps a key, 'hold:KeyW:800' holds a key for 800 ms,
    'click:320,200' clicks at page coordinates, 'type:hello' types text, 'wait:500' waits 500 ms,
    'advance:1000' calls window.advanceTime(1000). Serves dist/ when present. Use an absolute path.
    The first run downloads a headless Chromium (about 150 MB)."""
    root = Path(folder).expanduser()
    web = root / "dist" if (root / "dist" / "index.html").exists() else root
    if not (web / page).is_file():
        return [f"{web / page} does not exist."]
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return ["Playwright is not installed. Reinstall game-builder, which depends on it."]
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(web)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    errors, failed, notes = [], [], []
    try:
        async with async_playwright() as pw:
            browser = await launch_browser(pw)
            tab = await browser.new_page(viewport={"width": width, "height": height})
            tab.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type in ("error", "warning") else None)
            tab.on("pageerror", lambda e: errors.append(f"uncaught: {e}"))
            tab.on("requestfailed", lambda r: failed.append(f"{r.url} ({r.failure})"))
            tab.on("response", lambda r: failed.append(f"{r.url} (HTTP {r.status})") if r.status >= 400 else None)
            await tab.goto(f"http://127.0.0.1:{httpd.server_address[1]}/{page}", wait_until="load")
            # Let the game start its loop (two animation frames) and settle before acting.
            await tab.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
            await tab.wait_for_timeout(300)
            before = await tab.evaluate(STATE_JS)
            for action in actions or []:
                match = ACTION.match(action.strip())
                if not match:
                    notes.append(f"skipped unknown action {action!r}")
                    continue
                kind, arg = match.groups()
                try:
                    if kind == "press":
                        await tab.keyboard.press(arg)
                    elif kind == "hold":
                        key, _, ms = arg.rpartition(":")
                        await tab.keyboard.down(key)
                        await tab.wait_for_timeout(int(ms))
                        await tab.keyboard.up(key)
                    elif kind == "click":
                        x, y = (float(v) for v in arg.split(","))
                        await tab.mouse.click(x, y)
                    elif kind == "type":
                        await tab.keyboard.type(arg)
                    elif kind == "wait":
                        await tab.wait_for_timeout(int(arg))
                    elif kind == "advance":
                        ok = await tab.evaluate("ms => typeof window.advanceTime === 'function' && (window.advanceTime(ms), true)", int(arg))
                        if not ok:
                            notes.append("advance skipped: the game has no window.advanceTime")
                except Exception as e:
                    notes.append(f"{action!r} failed: {e}")
            after = await tab.evaluate(STATE_JS)
            shot = await tab.screenshot(type="png")
            await browser.close()
    except Exception as e:
        return [f"Playtest could not run: {e}"]
    finally:
        httpd.shutdown()
        httpd.server_close()
    clip = lambda v: "not defined (add window.render_game_to_text to inspect state)" if v is None else v[:2000]
    report = [f"Playtested {web / page} at {width}×{height} with {len(actions or [])} action(s)."]
    report.append("Errors:\n" + "\n".join(f"- {e}" for e in errors[:30]) if errors else "No console or page errors.")
    report.append("Failed loads:\n" + "\n".join(f"- {f}" for f in failed[:30]) if failed else "All files loaded.")
    if notes:
        report.append("Notes:\n" + "\n".join(f"- {n}" for n in notes))
    report.append(f"State before: {clip(before)}\nState after: {clip(after)}")
    report.append("The screenshot shows the page after the actions. Look at it before telling the user it works.")
    return [Image(data=shot, format="png"), "\n\n".join(report)]


@mcp.resource("gamebuilder://playbook", mime_type="text/markdown", description="How to pitch, build, art-direct, test and ship a game")
def playbook_resource() -> str:
    return guide("PLAYBOOK.md")


@mcp.resource("gamebuilder://stacks", mime_type="text/markdown", description="Stacks: 2D and 3D web, Godot, Unity, Unreal, Bevy, MonoGame, libGDX, raylib, LÖVE, Defold, Pygame, Flame, Ren'Py, multiplayer backends")
def stacks_resource() -> str:
    return guide("stacks.md")


@mcp.resource("gamebuilder://genres", mime_type="text/markdown", description="Genre playbooks: loop, systems, data and pitfalls")
def genres_resource() -> str:
    return guide("genres.md")


@mcp.prompt()
def new_game(idea: str) -> str:
    """Make a new game from an idea."""
    return (f"Let's make a game: {idea}\n\nCall plan_game with this idea, write a short pitch, then build it step by step: "
            "scaffold_game, a playable loop first, check_game and playtest_game after each change, serve_game so I can play, "
            "and image_prompt when it needs art. Keep a progress.md log.")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
