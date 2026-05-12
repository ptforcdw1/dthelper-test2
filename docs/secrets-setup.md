# Secrets setup

You will set these when ready to run the stack. They are NOT consumed by the
Phase 1 scaffold at write time — only at runtime by `docker compose up`.

## 1. Dynatrace API token
- URL: `<your-tenant>/#settings/integration/apikeys`
- Required scopes:
  - `WriteConfig`
  - `ReadConfig`
  - `entities.read`
  - `settings.write`
  - `settings.read`
- Save to `.env` as `DT_API_TOKEN`. Also set `DT_TENANT_URL`
  (e.g. `https://abc12345.live.dynatrace.com`).

## 2. GitHub PAT
- URL: https://github.com/settings/tokens
- Recommend: **fine-grained** PAT scoped to repo `ptforcdw1/dthelper-test2`.
- Permissions:
  - Contents: Read and write
  - Pull requests: Read and write
  - Metadata: Read-only
- Save to `.env` as `GITHUB_PAT`.
- Also add it as an n8n credential (Settings → Credentials → GitHub API)
  when you build the workflows.

## 3. Anthropic API key (Phase 2+ only)
- URL: https://console.anthropic.com/settings/keys
- Not used in Phase 1. Leave as `__set_me_phase_2__`.

## 4. n8n basic auth
- Set `N8N_BASIC_AUTH_USER` and `N8N_BASIC_AUTH_PASSWORD` in `.env`
  before first `docker compose up`. n8n reads these at container start.

## 5. GitHub webhook (for the PR-merge trigger)
- After building Workflow B (`pr-merged-to-run`) in n8n, copy the webhook
  URL it provides.
- GitHub repo → Settings → Webhooks → Add webhook:
  - Payload URL: the n8n webhook URL
  - Content type: `application/json`
  - Events: "Pull requests"
- Note: n8n must be reachable from GitHub. For local POC, use `ngrok` or
  `cloudflared tunnel`.

## What's NOT a secret
Anything in `config/` is non-secret. Tokens are only referenced **by env-var
name** in `config/global.yaml` (Rule 10).
