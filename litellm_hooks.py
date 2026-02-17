from typing import Any, Optional

from litellm.integrations.custom_logger import CustomLogger


def _strip_nulls(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_nulls(item) for item in obj]
    return obj


class FixRequestHook(CustomLogger):
    async def async_pre_call_hook(
        self,
        user_api_key_dict: Any,
        cache: Any,
        data: dict,
        call_type: str,
    ) -> Optional[dict]:
        # completion/text_completion = /chat/completions; anthropic_messages = /v1/messages (Claude Code)
        if call_type not in ("completion", "text_completion", "anthropic_messages"):
            return data

        messages = data.get("messages")
        if isinstance(messages, list):
            for message in messages:
                content = message.get("content")
                if content is None:
                    message["content"] = " "
                elif isinstance(content, str):
                    if not content.strip():
                        message["content"] = " "
                elif isinstance(content, list):
                    if not content:
                        message["content"] = " "
                    else:
                        for block in content:
                            if not isinstance(block, dict):
                                continue
                            # Fix any block with a "text" key (text, thinking, etc.)
                            if "text" in block:
                                text = block.get("text", "")
                                if not isinstance(text, str) or not text.strip():
                                    block["text"] = " "
                            elif block.get("type") == "text":
                                text = block.get("text", "")
                                if not isinstance(text, str) or not text.strip():
                                    block["text"] = " "

        max_tokens = data.get("max_tokens")
        if max_tokens is None:
            data["max_tokens"] = 4096
        else:
            try:
                n = int(max_tokens) if not isinstance(max_tokens, int) else max_tokens
                if n < 1:
                    data["max_tokens"] = 4096
            except (TypeError, ValueError):
                data["max_tokens"] = 4096

        data = _strip_nulls(data)
        return data


proxy_handler_instance = FixRequestHook()
