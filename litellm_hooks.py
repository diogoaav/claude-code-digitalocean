from typing import Any, Optional

from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import DualCache, UserAPIKeyAuth


def _strip_nulls(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_nulls(item) for item in obj]
    return obj


class FixRequestHook(CustomLogger):
    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: str,
    ) -> Optional[dict]:
        if call_type not in ("completion", "text_completion"):
            return data

        messages = data.get("messages")
        if isinstance(messages, list):
            for message in messages:
                content = message.get("content")
                if isinstance(content, str):
                    if not content.strip():
                        message["content"] = " "
                elif isinstance(content, list):
                    for block in content:
                        if block.get("type") == "text":
                            text = block.get("text", "")
                            if not isinstance(text, str) or not text.strip():
                                block["text"] = " "

        max_tokens = data.get("max_tokens")
        if max_tokens is None or not isinstance(max_tokens, int) or max_tokens < 1:
            data["max_tokens"] = 4096

        data = _strip_nulls(data)
        return data


proxy_handler_instance = FixRequestHook()
