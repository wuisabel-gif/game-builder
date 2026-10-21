"""Game Builder terminal agent: chat in the terminal, it writes and runs the game in your folder."""

import argparse
import os
import platform
import subprocess
import sys
import webbrowser
from importlib.resources import files
from pathlib import Path

import anthropic

from . import __version__

MODEL = os.environ.get("GAME_BUILDER_MODEL", "claude-opus-5-5")
SKIP_DIRS = {".git", "node_modules", "Library", "Temp", "Logs", "target", ".next", "__pycache__", ".venv", "dist-newstyle"}
MAX_READ = 100_000
MAX_OUTPUT = 20_000

INTRO = """You are Game Builder, a terminal agent that makes games together with the user.
You work inside one project folder (the project root) through the tools you are given:
list_files, read_file, write_file, edit_file and run_command. Paths are relative to the project root.
Read before you edit. Prefer edit_file for small changes and write_file for new files.
Keep each file under about 1,500 lines; split larger work into modules.
The user approves shell commands, and you cannot see a screen or a browser: tell the user
how to look at the result (in this tool, /serve starts a local web server) and ask what they see.
Follow the playbook, stacks guide and genre guide below.
"""


def system_prompt(root: Path) -> str:
    book = files("gamebuilder") / "playbook"
    guides = "\n\n".join((book / name).read_text(encoding="utf-8") for name in ("PLAYBOOK.md", "stacks.md", "genres.md"))
    return f"{INTRO}\n{guides}\n\n# Environment\nProject root: {root}\nOS: {platform.system()}"


def string_tool(name, description, props, eager=False):
    tool = {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": {k: {"type": "string", "description": d} for k, d in props.items()},
            "required": list(props),
            "additionalProperties": False,
        },
    }
    if eager:
        tool["eager_input_streaming"] = True  # stream big file bodies; inputs are validated in run_tool
    return tool


TOOLS = [
    string_tool("list_files", "List files under a folder in the project, recursively. Skips .git, node_modules, build output and Unity cache folders.",
                {"path": "Folder relative to the project root; '.' for the root."}),
    string_tool("read_file", "Read a text file from the project.", {"path": "File path relative to the project root."}),
    string_tool("write_file", "Create or overwrite a file with the full contents given. Creates parent folders.",
                {"path": "File path relative to the project root.", "content": "The complete file contents."}, eager=True),
    string_tool("edit_file", "Replace one exact, unique snippet of text in an existing file.",
                {"path": "File path relative to the project root.", "old": "Exact text to replace; must occur exactly once.", "new": "Replacement text."}, eager=True),
    string_tool("run_command", "Run a shell command in the project root (120 second timeout). The user approves each command. "
                "Do not start servers or other long-running processes; tell the user to run them instead.",
                {"command": "The shell command to run."}),
]
SCHEMAS = {t["name"]: t["input_schema"]["required"] for t in TOOLS}


class ToolError(Exception):
    pass


def inside(root: Path, rel: str) -> Path:
    path = (root / rel).resolve()
    if path != root and not path.is_relative_to(root):
        raise ToolError(f"{rel} is outside the project folder")
    return path


def list_files(root, path):
    base = inside(root, path)
    if not base.is_dir():
        raise ToolError(f"{path} is not a folder")
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for f in sorted(filenames):
            p = Path(dirpath, f)
            out.append(f"{p.relative_to(root)}  ({p.stat().st_size} bytes)")
            if len(out) >= 500:
                return "\n".join(out + ["… more files not shown; list a subfolder"])
    return "\n".join(out) or "(empty)"


def read_file(root, path):
    p = inside(root, path)
    if not p.is_file():
        raise ToolError(f"{path} does not exist")
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"{path} is a binary file ({p.stat().st_size} bytes)."
    if len(text) > MAX_READ:
        return text[:MAX_READ] + f"\n… truncated; file has {len(text)} characters"
    return text


def write_file(root, path, content):
    p = inside(root, path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {path} ({content.count(chr(10)) + 1} lines)."


def edit_file(root, path, old, new):
    p = inside(root, path)
    if not p.is_file():
        raise ToolError(f"{path} does not exist")
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise ToolError(f"old text found {count} times in {path}; it must occur exactly once")
    p.write_text(text.replace(old, new), encoding="utf-8")
    return f"Edited {path}."


def run_command(root, command, approve):
    if not approve(command):
        return "The user declined to run this command."
    try:
        done = subprocess.run(command, shell=True, cwd=root, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        raise ToolError("command timed out after 120 seconds")
    out = (done.stdout + done.stderr)[-MAX_OUTPUT:]
    return f"exit code {done.returncode}\n{out}"


def run_tool(root, name, args, approve):
    """Validate input (eager streaming skips server-side validation), run it, return (text, is_error)."""
    if name not in SCHEMAS:
        return f"Unknown tool {name}.", True
    if not isinstance(args, dict) or any(not isinstance(args.get(k), str) for k in SCHEMAS[name]):
        return f"Invalid input for {name}: expected string fields {SCHEMAS[name]}.", True
    try:
        if name == "run_command":
            return run_command(root, args["command"], approve), False
        fn = {"list_files": list_files, "read_file": read_file, "write_file": write_file, "edit_file": edit_file}[name]
        return fn(root, *(args[k] for k in SCHEMAS[name])), False
    except (ToolError, OSError) as e:
        return f"Error: {e}", True


def describe(name, args):
    if not isinstance(args, dict):
        return name
    if name == "run_command":
        return f"$ {args.get('command', '')}"
    return f"{name} {args.get('path', '')}"


class Approver:
    def __init__(self, always):
        self.always = always

    def __call__(self, command):
        if self.always:
            return True
        answer = input(f"  run `{command}`? [y/N/a=always] ").strip().lower()
        if answer == "a":
            self.always = True
        return answer in ("y", "yes", "a")


def tool_results(blocks, text, is_error=True):
    return [{"type": "tool_result", "tool_use_id": b.id, "content": text, "is_error": is_error} for b in blocks]


def add_user(messages, content):
    """Append user content, merging into a trailing user message so roles keep alternating."""
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    if messages and messages[-1]["role"] == "user":
        messages[-1]["content"].extend(content)
    else:
        messages.append({"role": "user", "content": content})


def turn(client, system, messages, root, approve):
    bad_streams = 0
    while True:
        try:
            with client.beta.messages.stream(
                model=MODEL,
                max_tokens=64000,
                system=system,
                tools=TOOLS,
                messages=messages,
                thinking={"type": "adaptive"},
                output_config={"effort": "high"},
                cache_control={"type": "ephemeral"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                response = stream.get_final_message()
        except ValueError as e:  # unparseable streamed tool input: no tool_use_id to answer, so re-issue
            bad_streams += 1
            if bad_streams > 2:
                print(f"\n[stopped: the model kept sending malformed tool input: {e}]")
                return
            continue
        print()
        messages.append({"role": "assistant", "content": response.content})
        uses = [b for b in response.content if b.type == "tool_use"]
        if response.stop_reason == "refusal":
            print("[the model declined this request]")
            if uses:  # keep history valid for the next message
                add_user(messages, tool_results(uses, "Not run: the turn was declined."))
            return
        if response.stop_reason == "max_tokens" and uses:
            add_user(messages, tool_results(uses, "Not run: output hit the token limit mid-call. Split the work into smaller files or edits."))
            continue
        if not uses:
            return
        results = []
        for b in uses:
            print(f"  → {describe(b.name, b.input)}")
            text, is_error = run_tool(root, b.name, b.input, approve)
            if is_error:
                print(f"    {text.splitlines()[0]}")
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": text, "is_error": is_error})
        add_user(messages, results)


def close_dangling(messages):
    """After Ctrl-C, answer any tool calls left without results so the next request is valid."""
    if messages and messages[-1]["role"] == "assistant":
        uses = [b for b in messages[-1]["content"] if getattr(b, "type", None) == "tool_use"]
        if uses:
            add_user(messages, tool_results(uses, "Interrupted by the user."))


def serve(root):
    folder = root / "dist" if (root / "dist").is_dir() else root
    subprocess.Popen([sys.executable, "-m", "http.server", "8000", "--bind", "127.0.0.1", "--directory", str(folder)],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Serving {folder} at http://127.0.0.1:8000 (stops when you quit)")
    webbrowser.open("http://127.0.0.1:8000")


def main():
    parser = argparse.ArgumentParser(prog="game-builder", description="A terminal agent that builds games with you.")
    parser.add_argument("prompt", nargs="*", help="what to build or change (optional; you can also type it after start)")
    parser.add_argument("-C", "--dir", default=".", help="project folder (default: current folder)")
    parser.add_argument("-y", "--yes", action="store_true", help="run shell commands without asking")
    parser.add_argument("--version", action="version", version=f"game-builder {__version__}")
    args = parser.parse_args()

    root = Path(args.dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic()
    system = system_prompt(root)
    approve = Approver(args.yes)
    messages = []
    pending = " ".join(args.prompt).strip()
    print(f"game-builder {__version__} · {MODEL} · {root}\nDescribe a game. Commands: /serve, /quit")

    while True:
        try:
            text = pending or input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        pending = ""
        if text in ("/quit", "/exit"):
            return
        if text == "/serve":
            serve(root)
            continue
        if not text:
            continue
        add_user(messages, text)
        try:
            turn(client, system, messages, root, approve)
        except KeyboardInterrupt:
            print("\n[interrupted]")
            close_dangling(messages)
        except anthropic.AuthenticationError:
            print("Not signed in. Set ANTHROPIC_API_KEY, or run `ant auth login`.")
            return
        except anthropic.RateLimitError:
            print("Rate limited. Wait a minute, then send your message again.")
        except anthropic.APIConnectionError:
            print("Could not reach the API. Check your connection and try again.")
        except anthropic.APIStatusError as e:
            print(f"API error {e.status_code}: {e.message}")
        except anthropic.AnthropicError as e:  # credential problems surface here, before any request
            print(f"Sign-in problem: {e}\nRun `ant auth login`, or set ANTHROPIC_API_KEY.")
            return


if __name__ == "__main__":
    main()
