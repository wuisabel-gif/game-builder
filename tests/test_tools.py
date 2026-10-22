"""Run: uv run --with . python tests/test_tools.py"""
import asyncio
import sys
import tempfile
from pathlib import Path

from mcp import Client, StdioServerParameters

from gamebuilder.server import check_game, get_guide, image_prompt, plan_game, scaffold_game

tmp = Path(tempfile.mkdtemp()).resolve()

# Planning picks a stack from the idea and pulls matching guides.
assert "Recommended stack: online multiplayer" in plan_game("a werewolf game friends join from their phones")
assert "Recommended stack: godot" in plan_game("a first-person horror game")
assert "Recommended stack: 3d web" in plan_game("a first-person horror game in the browser")
assert "Recommended stack: unreal" in plan_game("an Unreal open world shooter")
assert "Recommended stack: pygame" in plan_game("a retro game in python")
assert "Recommended stack: visual novels" in plan_game("a dating sim")
assert "Recommended stack: 2d web" in plan_game("an anime dress-up game")
assert "Dress-up" in plan_game("an anime dress-up game")
assert "## Card game" not in plan_game("a racing game")  # generic words do not match genres
assert "## Racing" in plan_game("a racing game")
assert "Recommended stack: unity" in plan_game("anything", stack="unity")
assert "GameCI" in get_guide("unity") and "## Party and social deduction" in get_guide("murder mystery")
assert "No match" in get_guide("zzzz")

# Scaffolding writes playable starters and never overwrites.
for stack in ("web2d", "threejs", "aframe"):
    out = scaffold_game(str(tmp / stack), stack, "Test Game")
    assert out.startswith("Created"), out
    assert "No missing local files." in check_game(str(tmp / stack)), check_game(str(tmp / stack))
assert "not empty" in scaffold_game(str(tmp / "web2d"), "web2d", "Again")
assert "absolute" in scaffold_game("relative/path", "web2d", "X")
assert "no files were written" in scaffold_game(str(tmp / "u"), "unity", "X")
assert "__TITLE__" not in (tmp / "web2d/dist/index.html").read_text()

# Checks find broken references.
(tmp / "web2d/dist/app.js").write_text((tmp / "web2d/dist/app.js").read_text() + "\nnew Image().src = 'assets/missing.png';\n")
assert "assets/missing.png" in check_game(str(tmp / "web2d"))

prompt = image_prompt("two characters", columns=4, cell_width=543, cell_height=724, cells=["a", "b", "c", "d"], change="the face")
assert "Canvas 2172 × 724 px" in prompt and "Change only this: the face" in prompt


# End to end over stdio, the way an agent connects.
async def over_stdio():
    async with Client(StdioServerParameters(command=sys.executable, args=["-m", "gamebuilder.server"])) as client:
        names = {t.name for t in (await client.list_tools()).tools}
        assert names == {"plan_game", "get_guide", "scaffold_game", "image_prompt", "check_game", "serve_game"}, names
        result = await client.call_tool("get_guide", {"topic": "werewolf"})
        assert "social deduction" in result.content[0].text
        assert len((await client.list_resources()).resources) == 3
        assert [p.name for p in (await client.list_prompts()).prompts] == ["new_game"]

asyncio.run(over_stdio())
print("all checks passed")
