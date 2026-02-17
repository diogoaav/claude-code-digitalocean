# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Does

This is an infrastructure repo that deploys a **LiteLLM proxy** on **DigitalOcean App Platform** so that Claude Code can use **DigitalOcean Serverless Inference** as its LLM backend.

The request flow is:
```
Claude Code (Anthropic /v1/messages format)
    → LiteLLM proxy (hosted on DO App Platform)
    → DigitalOcean Serverless Inference (OpenAI /v1/chat/completions format)
```

LiteLLM translates between the Anthropic API format that Claude Code expects and the OpenAI-compatible format that DigitalOcean Serverless Inference exposes.

## Key Files

- `.do/deploy.template.yaml` — DigitalOcean App Platform app spec. Defines the `litellm` service, its environment variables, and the managed Postgres database (`litellm-db`). Currently pulls `ghcr.io/berriai/litellm:main-stable` directly.
- `PROMPT_FIX_LITELLM.md` — Describes known request failures (empty text blocks, missing `max_tokens`, null fields) and a plan to fix them via a custom LiteLLM `async_pre_call_hook`. This work is **not yet implemented** — it requires adding `litellm_hooks.py`, `config.yaml`, and a `Dockerfile`, and updating the deploy spec to build from source.

## Deploy Template Structure

The deploy spec uses:
- **Service**: `litellm` running on `apps-s-1vcpu-1gb`, port 4000
- **Database**: Managed Postgres referenced as `${litellm-db.DATABASE_URL}`
- **Key env vars**: `LITELLM_MASTER_KEY` (secret), `UI_USERNAME`, `UI_PASSWORD` (secret), `STORE_MODEL_IN_DB=True`, `LITELLM_DROP_PARAMS=True`, `REQUEST_TIMEOUT=600`
- Models are stored in the DB (not in a static config), so `STORE_MODEL_IN_DB=True` is essential.

## Claude Code Environment Variables

To point Claude Code at this gateway:
```sh
export ANTHROPIC_BASE_URL=https://<your-app>.ondigitalocean.app
export ANTHROPIC_MODEL=<model-name-configured-in-litellm>
export ANTHROPIC_AUTH_TOKEN=<litellm-virtual-key-or-master-key>
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
```

## Known Issues (Pending Fix)

See `PROMPT_FIX_LITELLM.md` for full context. The pre-built LiteLLM image can fail with:
- `messages: text content blocks must be non-empty` — empty text blocks from Claude Code
- `max_tokens: must be greater than or equal to 1` — missing/zero max_tokens
- Null field rejections from the downstream API

The fix is a custom LiteLLM `CustomLogger` with `async_pre_call_hook`, loaded via a `config.yaml`, built into a custom `Dockerfile`. Once implemented, the deploy spec must switch from the `image:` block to a `github:` source with `dockerfile_path: Dockerfile`.
