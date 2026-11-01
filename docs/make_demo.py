"""Regenerate docs/demo.gif from real tool calls.

Run: uv run --with . --with pillow python docs/make_demo.py

Every line in the terminal panel is real output from the Game Builder tools, and every
game frame is a screenshot of the generated starter being played in headless Chromium.
"""

import asyncio
import base64
import html
import io
import json
import tempfile
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

from gamebuilder.server import QuietHandler, plan_game, playtest_game, scaffold_game

OUT = Path(__file__).with_name("demo.gif")
W, GAME_H, TERM_H = 760, 520, 200
work = Path(tempfile.mkdtemp())

PANEL = """<html><body style="margin:0;width:{w}px;background:#16130f;font:15px/1.45 ui-monospace,Menlo,monospace">
<div style="height:{th}px;box-sizing:border-box;padding:14px 18px;color:#e8dfcf;overflow:hidden">{lines}</div>
<div style="height:{gh}px;background:#000"><img src="data:image/png;base64,{img}" style="width:{w}px;height:{gh}px;object-fit:contain;display:block"></div>
</body></html>"""


def line(text, kind="out"):
    color = {"you": "#f3c969", "call": "#8fd3a9", "out": "#cfc6b6", "dim": "#8a8275"}[kind]
    prefix = {"you": "you ▸ ", "call": "agent ▸ ", "out": "  ", "dim": "  "}[kind]
    return f'<div style="color:{color};white-space:pre">{html.escape(prefix + text)}</div>'


def serve(folder):
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(folder)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def blank_png():
    buf = io.BytesIO()
    Image.new("RGB", (W, GAME_H), "#0b0a08").save(buf, "PNG")
    return buf.getvalue()


def main():
    frames, durations = [], []

    def add(panel_page, lines, game_png, ms):
        panel_page.set_content(PANEL.format(w=W, th=TERM_H, gh=GAME_H, lines="".join(lines[-7:]),
                                            img=base64.b64encode(game_png).decode()))
        frames.append(Image.open(io.BytesIO(panel_page.screenshot(type="png"))).convert("RGB"))
        durations.append(ms)

    idea = "a cosy browser game where you catch stars"
    plan = plan_game(idea).splitlines()
    stack = next(l for l in plan if l.startswith("Recommended stack"))
    web = work / "stars"
    made = scaffold_game(str(web), "web2d", "Star Catch").splitlines()
    # The real playtest report shown after the play-through (run before the sync browser session).
    _, report = asyncio.run(playtest_game(str(web), ["hold:ArrowLeft:900", "hold:ArrowUp:400"]))
    errors = next(l for l in report.split("\n\n") if "error" in l.lower()).splitlines()[0]
    end = json.loads(next(l for l in report.splitlines() if l.startswith("State after"))[len("State after: "):])
    after = f'State after: x={end["x"]:.0f} y={end["y"]:.0f} score={end["score"]}  (input moved the player)'
    hall = work / "hall"
    hall_made = scaffold_game(str(hall), "threejs", "The Corridor").splitlines()[0].split(" in ")[0]
    _, hall_report = asyncio.run(playtest_game(str(hall), ["click:380,260", "hold:KeyW:2000"], width=W, height=GAME_H))
    walked = json.loads(next(l for l in hall_report.splitlines() if l.startswith("State after"))[len("State after: "):])
    hall_moved = f'State after: x={walked["x"]:.1f} z={walked["z"]:.1f}  (walked down the corridor)'

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        panel = browser.new_page(viewport={"width": W, "height": TERM_H + GAME_H})
        log = [line(f"make {idea}", "you")]
        add(panel, log, blank_png(), 1400)
        log += [line(f'plan_game("{idea}")', "call"), line(stack)]
        add(panel, log, blank_png(), 1500)
        log += [line('scaffold_game(folder, "web2d", "Star Catch")', "call"), line(made[0].split(" in ")[0]),
                line("dist/index.html  dist/app.js  dist/style.css  pages.yml")]
        add(panel, log, blank_png(), 1600)

        # Play the generated 2D starter: steer toward each star with the arrow keys.
        httpd = serve(web / "dist")
        game = browser.new_page(viewport={"width": W, "height": GAME_H})
        game.goto(f"http://127.0.0.1:{httpd.server_address[1]}/index.html")
        game.wait_for_timeout(400)
        log += [line('playtest_game(folder, ["hold:ArrowLeft:900", "hold:ArrowUp:400", …])', "call")]
        held = set()
        for _ in range(46):
            s = json.loads(game.evaluate("render_game_to_text()"))
            want = set()
            dx, dy = s["star"]["x"] - s["x"], s["star"]["y"] - s["y"]
            if abs(dx) > 6: want.add("ArrowRight" if dx > 0 else "ArrowLeft")
            if abs(dy) > 6: want.add("ArrowDown" if dy > 0 else "ArrowUp")
            for k in held - want: game.keyboard.up(k)
            for k in want - held: game.keyboard.down(k)
            held = want
            game.wait_for_timeout(70)
            state = line(f'state: x={s["x"]:.0f} y={s["y"]:.0f} score={s["score"]}', "dim")
            add(panel, log + [state], game.screenshot(type="png"), 90)
        for k in held: game.keyboard.up(k)
        httpd.shutdown()

        log += [line(errors), line(after)]
        add(panel, log, game.screenshot(type="png"), 1800)

        # Then a 3D idea: scaffold the Three.js starter and walk the corridor.
        log = [line("now a first-person corridor in the browser", "you"),
               line('scaffold_game(folder, "threejs", "The Corridor")', "call"), line(hall_made + ": index.html, pages.yml")]
        httpd = serve(hall)
        game.goto(f"http://127.0.0.1:{httpd.server_address[1]}/index.html")
        game.wait_for_timeout(1200)
        add(panel, log, game.screenshot(type="png"), 1500)
        game.mouse.click(380, 260)
        log += [line('playtest_game(folder, ["click:380,260", "hold:KeyW:2000"])', "call")]
        game.keyboard.down("KeyW")
        for i in range(24):
            game.wait_for_timeout(80)
            pos = json.loads(game.evaluate("render_game_to_text()"))
            if pos["x"] > 3:  # stop partway so the last frame still looks down the corridor
                game.keyboard.up("KeyW")
            add(panel, log + [line(f'state: x={pos["x"]:.1f} z={pos["z"]:.1f}', "dim")], game.screenshot(type="png"), 90)
        game.keyboard.up("KeyW")
        httpd.shutdown()
        log += [line(hall_moved), line("install: uvx game-builder-mcp", "dim")]
        add(panel, log, game.screenshot(type="png"), 2600)
        browser.close()

    # A palette per frame keeps both the warm 2D board and the dim 3D corridor true to colour.
    small = [f.quantize(colors=160, dither=Image.Dither.NONE) for f in frames]
    small[0].save(OUT, save_all=True, append_images=small[1:], duration=durations, loop=0, optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {len(frames)} frames)")


if __name__ == "__main__":
    main()
