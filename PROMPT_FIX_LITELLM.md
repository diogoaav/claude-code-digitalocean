# Prompt: Fix LiteLLM gateway errors for Claude Code → DigitalOcean

Use this prompt with Claude Code (or another AI) to implement the fix in this repo.

---

## Context

This repo deploys a **LiteLLM** proxy on DigitalOcean App Platform so that **Claude Code** can use **DigitalOcean Serverless Inference** as its backend.

- **Claude Code** sends requests in **Anthropic-style** (e.g. `/v1/messages` format) to the LiteLLM proxy.
- **LiteLLM** converts those requests to **OpenAI-style** (e.g. `/v1/chat/completions`) and forwards them to **DigitalOcean Serverless Inference**, which only supports the OpenAI-compatible API.

## The problem

When using this setup, requests sometimes fail with one or more of these errors:

1. **`messages: text content blocks must be non-empty`**  
   Anthropic-style clients can send messages where a text content block has empty or whitespace-only `text`. Downstream (Anthropic or DigitalOcean) rejects these.

2. **`max_tokens: must be greater than or equal to 1`**  
   The request can have `max_tokens` missing, null, or 0. The backend requires `max_tokens >= 1`.

3. **Rejection of `null` values**  
   Some fields are sent as `null`; OpenAI-style backends may reject the request when optional fields are present with value `null` instead of being omitted.

## What to implement

Fix this **inside LiteLLM** using a **pre-call hook** so all clients (including Claude Code) are covered without changing the client.

1. **Add a Python module** (e.g. `litellm_hooks.py`) that defines a LiteLLM **CustomLogger** with an **`async_pre_call_hook`** that:
   - Runs only for `call_type` in `("completion", "text_completion")`.
   - **Sanitize messages:** For each message in `data["messages"]`, if `content` is a string and is empty or whitespace-only, set it to a single space `" "`. If `content` is a list of blocks, for each block with `type == "text"`, if `text` is missing, empty, or whitespace-only, set `block["text"] = " "`.
   - **Enforce max_tokens:** If `data.get("max_tokens")` is missing, null, or less than 1, set `data["max_tokens"] = 4096` (or another sensible default).
   - **Strip nulls:** Remove any key in the request `data` (recursively) whose value is `None`, so the JSON sent downstream has no `null` values for those keys.
   - Return the modified `data`.

   Use the pattern from [LiteLLM call hooks](https://docs.litellm.ai/docs/proxy/call_hooks): import `CustomLogger` from `litellm.integrations.custom_logger`, and `UserAPIKeyAuth`, `DualCache` from `litellm.proxy.proxy_server`. Expose a module-level instance (e.g. `proxy_handler_instance`) that the config can reference.

2. **Add a `config.yaml`** in the repo root with:
   ```yaml
   litellm_settings:
     callbacks:
       - litellm_hooks.proxy_handler_instance
   ```
   (No `model_list` is needed if the app already uses `STORE_MODEL_IN_DB=True` and loads models from the DB via env.)

3. **Add a `Dockerfile`** in the repo root that:
   - Uses `FROM ghcr.io/berriai/litellm:main-stable` (or `berriai/litellm:main-stable` if your registry expects that).
   - Copies `litellm_hooks.py` and `config.yaml` into the image (e.g. into `/app`).
   - Runs the proxy with that config: `CMD ["litellm", "--config", "/app/config.yaml"]`.
   - Keeps `http_port` behavior (LiteLLM default 4000; no change needed if the deploy spec uses 4000).

4. **Update `.do/deploy.template.yaml`** so the `litellm` service is built from the repo instead of the pre-built image:
   - Add a **source** (e.g. `github` with `repo`, `branch`, `deploy_on_push`) and **`dockerfile_path: Dockerfile`**, and **`source_dir: /`** so the build context is the repo root.
   - **Remove** the `image:` block (registry, repository, tag) so App Platform builds from the Dockerfile instead of pulling the pre-built image.
   - Keep all existing `envs` (e.g. `LITELLM_MASTER_KEY`, `DATABASE_URL`, `STORE_MODEL_IN_DB`, `LITELLM_DROP_PARAMS`, etc.) unchanged.

After this, a deploy from this repo will build the custom image (LiteLLM + your hook + config) and run the proxy with the hook, so empty text blocks, invalid `max_tokens`, and null values are fixed before the request is converted and sent to DigitalOcean.

## References

- LiteLLM proxy call hooks: https://docs.litellm.ai/docs/proxy/call_hooks  
- LiteLLM drop params / request handling: https://docs.litellm.ai/docs/completion/drop_params  
- DigitalOcean App Platform app spec (services, dockerfile_path, github): https://docs.digitalocean.com/products/app-platform/reference/app-spec/
