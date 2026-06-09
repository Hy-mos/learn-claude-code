"""Pretty-print Anthropic-style message traces for the teaching examples."""

from __future__ import annotations

import json
import os
from textwrap import indent
from typing import Any


def short(value: Any, n: int | None = None) -> str:
    """Return a display-safe preview without mutating the real message content."""
    if n is None:
        n = int(os.getenv("TRACE_MAX_CHARS", "800"))
    text = str(value)
    return text if len(text) <= n else text[:n] + f"\n... ({len(text) - n} more chars)"


def _block_type(block: Any) -> str:
    if isinstance(block, dict):
        return str(block.get("type", "dict"))
    return str(getattr(block, "type", type(block).__name__))


def _block_field(block: Any, name: str, default: Any = "") -> Any:
    if isinstance(block, dict):
        return block.get(name, default)
    return getattr(block, name, default)


def print_messages(messages: list[dict[str, Any]], title: str = "MESSAGES TRACE") -> None:
    """Print user/assistant/tool_result messages grouped by turn and content block."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    for i, msg in enumerate(messages, 1):
        role = msg.get("role", "<missing role>")
        content = msg.get("content", "")

        print(f"\n[{i}] role = {role}")

        if isinstance(content, str):
            print(indent(short(content), "  "))
            continue

        if not isinstance(content, list):
            print(indent(short(content), "  "))
            continue

        for j, block in enumerate(content, 1):
            block_type = _block_type(block)

            if block_type == "tool_result":
                print(f"  ({j}) tool_result")
                print(f"      tool_use_id: {_block_field(block, 'tool_use_id')}")
                is_error = _block_field(block, "is_error", False)
                if is_error:
                    print("      is_error: true")
                print(indent(short(_block_field(block, "content", "")), "      "))

            elif block_type == "tool_use":
                print(f"  ({j}) tool_use")
                print(f"      id: {_block_field(block, 'id')}")
                print(f"      name: {_block_field(block, 'name')}")
                tool_input = _block_field(block, "input", {})
                try:
                    rendered = json.dumps(tool_input, ensure_ascii=False, indent=2)
                except TypeError:
                    rendered = str(tool_input)
                print(indent(rendered, "      "))

            elif block_type == "text":
                print(f"  ({j}) text")
                print(indent(short(_block_field(block, "text", "")), "      "))

            elif block_type == "thinking":
                print(f"  ({j}) thinking")
                thinking = _block_field(block, "thinking", "")
                print(indent(short(thinking), "      ") if thinking else "      <empty thinking>")

            else:
                print(f"  ({j}) {block_type}")
                if hasattr(block, "model_dump_json"):
                    print(indent(block.model_dump_json(indent=2), "      "))
                else:
                    print(indent(short(block), "      "))
