"""Run: uv run --with . python tests/test_tools.py"""
import tempfile
from pathlib import Path

from gamebuilder.cli import add_user, run_tool, system_prompt

root = Path(tempfile.mkdtemp()).resolve()
yes = lambda c: True

assert run_tool(root, "write_file", {"path": "dist/index.html", "content": "<h1>hi</h1>"}, yes) == ("Wrote dist/index.html (1 lines).", False)
assert run_tool(root, "read_file", {"path": "dist/index.html"}, yes) == ("<h1>hi</h1>", False)
assert run_tool(root, "write_file", {"path": "../escape.txt", "content": "x"}, yes)[1] is True
assert run_tool(root, "read_file", {"path": "/etc/hosts"}, yes)[1] is True
assert not (root.parent / "escape.txt").exists()
assert run_tool(root, "edit_file", {"path": "dist/index.html", "old": "zzz", "new": "y"}, yes)[1] is True
assert run_tool(root, "edit_file", {"path": "dist/index.html", "old": "hi", "new": "hello"}, yes)[1] is False
assert "hello" in (root / "dist/index.html").read_text()
assert "dist/index.html" in run_tool(root, "list_files", {"path": "."}, yes)[0]
assert run_tool(root, "write_file", {"path": "a.txt"}, yes)[1] is True  # missing content
assert run_tool(root, "run_command", {"command": "echo ok"}, yes) == ("exit code 0\nok\n", False)
assert run_tool(root, "run_command", {"command": "echo ok"}, lambda c: False)[0].startswith("The user declined")

msgs = []
add_user(msgs, "make a game")
add_user(msgs, [{"type": "tool_result", "tool_use_id": "t", "content": "x"}])
assert len(msgs) == 1 and len(msgs[0]["content"]) == 2

assert "Stacks guide" in system_prompt(root) and "Genre playbooks" in system_prompt(root)
print("all tool checks passed")
