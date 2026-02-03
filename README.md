[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/jkpe/claude-code-digitalocean/tree/main)

# Use DigitalOcean Serverless inference with Claude Code.

Did you know you can use DigitalOcean Serverless Inference endpoint with Claude Code?

This is because Claude Code supports [third party gateways](https://code.claude.com/docs/en/llm-gateway). A third party gateway is a server that supports the Anthropic API format `/v1/messages` `/v1/messages/count_tokens`

Using this this setup provides:

- Consolidated billing and usage tracking through your DigitalOcean account.
- Your own self-hosted [LiteLLM](https://www.litellm.ai/) gateway - a proxy server (AI Gateway) to call 100+ LLM APIs in OpenAI (or native) format, with cost tracking, guardrails, loadbalancing and logging.

## How does it work?

DigitalOcean's Serverless Inference API Endpoints support support a wide range of [models](https://docs.digitalocean.com/products/gradient-ai-platform/details/models/), including Claude Sonnet 4.5 and Claude Opus 4.5. However, it only supports the OpenAI API format `/v1/chat/completions` endpoint.

We use Litellm, hosted on DigitalOcean App Platform, to proxy requests from Claude Code to the DigitalOcean Serverless Inference API.

# Products used:

- [Claude Code](https://www.anthropic.com/news/claude-code)
- [Litellm](https://github.com/BerriAI/litellm)
- [DigitalOcean Serverless Inference](https://docs.digitalocean.com/products/gradient-ai-platform/how-to/use-serverless-inference/)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [DigitalOcean Database](https://docs.digitalocean.com/products/databases/)

## How to deploy the gateway

1. Click the button below to deploy the gateway to DigitalOcean App Platform:

   [![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/jkpe/claude-code-digitalocean/tree/main)

2. Set the following environment variables, leave the rest as default:

   Use `openssl rand -hex 32` to generate a random master key.

   | Environment Variable   | Description                                                      |
   |-----------------------|------------------------------------------------------------------|
   | `LITELLM_MASTER_KEY`  | Master key for authenticating and protecting your LiteLLM gateway|
   | `UI_USERNAME`         | Username for accessing the LiteLLM web user interface            |
   | `UI_PASSWORD`         | Password for accessing the LiteLLM web user interface                       |

3. Once deployed, browse to the app URL and login with the username and password you set. `https://your-app-name.ondigitalocean.app/ui`

4. Add DigitalOcean Serverless Inference API Endpoint to the gateway in the UI. [Here are the steps with screenshots.](https://docs.litellm.ai/docs/proxy/ui_credentials)

- Provider: `OpenAI-Compatible Endpoints`
- LiteLLM Model Name: `anthropic-claude-4.5-sonnet`
- Model Name: `digitalocean-anthropic-claude-4.5-sonnet` (this is the model name that Claude Code will use, set it to whatever you want, it will be used as the `ANTHROPIC_MODEL` environment variable in Claude Code)
- API Base: `https://inference.do-ai.run/v1`
- API Key: Generate it here: [https://cloud.digitalocean.com/gen-ai/model-access-keys](https://cloud.digitalocean.com/gen-ai/model-access-keys).

<a href="./screenshots/litellm-ui.png"><img src="./screenshots/litellm-ui.png" alt="LiteLLM web user interface" width="300" /></a>
<a href="./screenshots/litellm-deployed.png"><img src="./screenshots/litellm-deployed.png" alt="LiteLLM deployed to DigitalOcean App Platform" width="300" /></a>
<a href="./screenshots/add-model.png"><img src="./screenshots/add-model.png" alt="LiteLLM with DigitalOcean Serverless Inference API Endpoint added" width="300" /></a>
<a href="./screenshots/add-do.png"><img src="./screenshots/add-do.png" alt="LiteLLM with DigitalOcean Serverless Inference API Endpoint added" width="300" /></a>

### Configuring Claude Code to use the gateway

(optional) Generate a Virtual Key for Claude Code to use the gateway, you can also use your master key that we set earlier.

1. Browse to the LiteLLM web user interface.
2. Click on the "Virtual Keys" tab.
3. Click on "Create New Key"
4. Set the API Key as the `ANTHROPIC_AUTH_TOKEN` environment variable in Claude Code.

Set the following environment variables for Claude Code to use the gateway:

```
export ANTHROPIC_BASE_URL=https://your-app-name.ondigitalocean.app
export ANTHROPIC_MODEL=digitalocean-anthropic-claude-4.5-sonnet
export ANTHROPIC_AUTH_TOKEN=sk-litellm-key
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
```

Start Claude Code