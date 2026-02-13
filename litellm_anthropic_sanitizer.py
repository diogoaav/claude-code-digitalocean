"""
Sanitize Anthropic /v1/messages payloads so they never contain empty text content blocks.

Anthropic rejects requests with: "messages: text content blocks must be non-empty".
Claude Code (and other clients) sometimes send blocks like {"type":"text","text":""}.
This module mutates messages in place to fix or remove such blocks before forwarding.
"""

from typing import Any, Dict, List

# Placeholder used when content would otherwise be empty (Anthropic requires non-empty).
EMPTY_PLACEHOLDER = " "


def sanitize_anthropic_messages(messages: List[Dict[str, Any]]) -> None:
    """
    Mutate messages in place so no content block has empty or whitespace-only text.
    Compatible with Anthropic Messages API: content is a list of blocks with
    {"type": "text", "text": "..."} or other types.
    """
    if not messages:
        return
    for msg in messages:
        content = msg.get("content")
        if content is None:
            continue
        if isinstance(content, str):
            if not content.strip():
                msg["content"] = EMPTY_PLACEHOLDER
            continue
        if isinstance(content, list):
            _sanitize_content_blocks(content)
            if not content:
                msg["content"] = EMPTY_PLACEHOLDER
            continue


def _sanitize_content_blocks(blocks: List[Dict[str, Any]]) -> None:
    """
    Mutate blocks in place: remove text blocks that are empty or whitespace-only.
    If the list becomes empty, the caller should set content to a placeholder.
    """
    i = 0
    while i < len(blocks):
        block = blocks[i]
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if text is None or (isinstance(text, str) and not text.strip()):
                blocks.pop(i)
                continue
        i += 1


class AnthropicEmptyBlockSanitizer:
    """
    LiteLLM CustomLogger that sanitizes empty text blocks in messages before
    the request is sent. Use for Anthropic pass-through routes so clients
    (e.g. Claude Code) that occasionally send empty blocks do not get 400.
    """

    async def async_pre_request_hook(self, model: str, messages: List[Dict], kwargs: Dict) -> None:
        sanitize_anthropic_messages(messages)
        return None  # no change to kwargs
