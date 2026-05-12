# n8n setup (Phase 1)

Two workflows. Build them in the n8n UI at http://localhost:5678 after
`docker compose up -d`.

> Why no exported JSON? n8n workflow JSON is version-fragile across n8n
> releases. For a POC, hand-building from these notes is more robust.
> When you finish a workflow, export it via the menu (`...` → Download)
> and commit it under this folder.

## Credentials to add in n8n (Settings → Credentials)
- **GitHub API** — PAT from `.env` (`GITHUB_PAT`). Scope: repo.

---

## Workflow A: `catalog-to-pr`

Purpose: User submits the catalog form → n8n creates `request.json` on a new
branch and opens a PR for human approval.

### Nodes

1. **Form Trigger** (built-in)
   - Form title: `Create Management Zone`
   - Fields (match `catalog/items/create-management-zone.yaml`):
     - `app` — Text — required
     - `env` — Dropdown — values: `uat`, `prod` — required
     - `requester` — Text — required — label: "Your email"

2. **Code node** — generate Task ID + payload:
   ```js
   const today = new Date().toISOString().slice(0,10).replace(/-/g,'');
   const hex = Array.from(crypto.getRandomValues(new Uint8Array(3)))
     .map(b => b.toString(16).padStart(2,'0')).join('');
   return [{ json: {
     task_id: `DT-${today}-${hex}`,
     branch: `task/DT-${today}-${hex}`,
     template: 'create-management-zone',
     inputs: { app: $json.app, env: $json.env },
     requester: $json.requester
   }}];
   ```

3. **GitHub: Create or update file**
   - Owner: `{{$env.GITHUB_OWNER}}`
   - Repository: `{{$env.GITHUB_REPO}}`
   - File path: `tasks/{{$json.task_id}}/request.json`
   - Branch: `{{$json.branch}}` (set "create branch from main" if available, or use a preceding "create ref" call)
   - Content: `{{ JSON.stringify({task_id: $json.task_id, template: $json.template, inputs: $json.inputs, requester: $json.requester}, null, 2) }}`
   - Commit message: `[{{$json.task_id}}] request: create management zone`

4. **GitHub: Create pull request**
   - Title: `[{{$json.task_id}}] Approve: create MZ for {{$json.inputs.app}}/{{$json.inputs.env}}`
   - Head: `{{$json.branch}}`
   - Base: `main`
   - Body: include the request JSON inline.

5. **Respond to form** — return `{ task_id, pr_url }`.

---

## Workflow B: `pr-merged-to-run`

Purpose: When the approval PR is merged, run the template via the runner and
commit results back to `main`.

### Nodes

1. **Webhook trigger**
   - Path: `pr-merged`
   - Method: POST
   - Auth: none (or shared secret — recommended for non-local use).
   - Register the resulting URL as a GitHub repo webhook (Settings → Webhooks).
     Events: "Pull requests" only.

2. **IF node** — continue only when all true:
   - `$json.action == "closed"`
   - `$json.pull_request.merged == true`
   - `$json.pull_request.head.ref` starts with `task/`

3. **Code node** — parse `task_id` from branch name:
   ```js
   const branch = $json.pull_request.head.ref;
   const task_id = branch.replace(/^task\//, '');
   return [{ json: { task_id } }];
   ```

4. **GitHub: Get file** — `tasks/{{$json.task_id}}/request.json` from `main`.
   Decode and parse the JSON.

5. **HTTP Request** — POST to `http://runner:8080/run`
   Body (JSON):
   ```json
   {
     "task_id": "{{$json.task_id}}",
     "template": "{{$json.template}}",
     "inputs": {{ JSON.stringify($json.inputs) }}
   }
   ```

6. **GitHub: Create or update file** — commit runner result:
   - File path: `tasks/{{$json.task_id}}/result.json`
   - Content: `{{ JSON.stringify($json, null, 2) }}`
   - Branch: `main`
   - Commit message: `[{{$json.task_id}}] result`

7. **GitHub: Create or update file** (one per artifact the runner wrote to disk)
   - `tasks/{{$json.task_id}}/execution.jsonl`
   - `tasks/{{$json.task_id}}/verify.json`
   - Read these files from disk via a preceding "Read Binary File" or via the
     runner returning their contents (simpler: extend the runner response).

---

## GitHub webhook for Workflow B

For local testing your laptop must be reachable from GitHub. Easiest options:
- **ngrok**: `ngrok http 5678`, then point the GitHub webhook at
  `https://<id>.ngrok-free.app/webhook/pr-merged`.
- **cloudflared tunnel**: similar pattern, free tier available.

The webhook secret is optional but recommended; configure on both sides.

---

## Done = both workflows green for "Create Management Zone"
Phase 1 success: submit form → PR opens → merge PR → MZ exists in DT →
`tasks/<id>/verify.json` has `passed: true`. See `docs/architecture.md`
for the full success criteria.
