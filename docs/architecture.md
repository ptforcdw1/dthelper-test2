# Architecture — Phase 1

## Goal
Execute a Dynatrace administration task chosen from a catalog, with approval
via PR, and an auditable trail.

## Components

| Component | Role |
|---|---|
| n8n (Docker) | Catalog form, GitHub PR creation, webhook receiver, runner orchestration |
| Python runner (Docker, FastAPI) | Executes a template's `execute.py` + `verify.py` |
| GitHub | Source of truth for code, configs, templates, and task records |
| Dynatrace tenant | Target system |

## Component diagram

```mermaid
flowchart LR
    user(["User"])

    subgraph local["Local Docker stack"]
        direction TB
        subgraph n8n["n8n container"]
            form["Form trigger<br/>(catalog)"]
            wfA["Workflow A<br/>catalog-to-pr"]
            wfB["Workflow B<br/>pr-merged-to-run"]
            wh["Webhook<br/>pr-merged"]
        end
        subgraph runner["runner container<br/>(FastAPI)"]
            api["POST /run"]
            exec["execute.py<br/>(per template)"]
            verify["verify.py<br/>(per template)"]
        end
        repo[("Mounted repo<br/>/repo volume")]
    end

    subgraph ext["External"]
        gh[("GitHub<br/>dthelper-test2")]
        dt["Dynatrace<br/>tenant"]
        ant["Anthropic API<br/>(Phase 2+)"]:::future
    end

    user -- "1. submit form" --> form
    form --> wfA
    wfA -- "2. create branch + request.json + PR" --> gh
    user -- "3. review + merge PR" --> gh
    gh -- "4. PR-merged webhook" --> wh
    wh --> wfB
    wfB -- "5. POST /run" --> api
    api --> exec
    exec -- "6a. DT API" --> dt
    exec -- "audit log" --> repo
    api --> verify
    verify -- "6b. read-back" --> dt
    verify -- "verify.json" --> repo
    wfB -- "7. commit results to main" --> gh

    classDef future stroke-dasharray: 5 5,opacity:0.5
```

## Sequence — end-to-end task lifecycle

```mermaid
sequenceDiagram
    actor U as User
    participant Form as n8n Form
    participant N as n8n Workflows
    participant GH as GitHub
    participant R as Runner
    participant DT as Dynatrace

    U->>Form: submit (app, env, requester)
    Form->>N: trigger Workflow A
    Note over N: mint Task ID<br/>DT-YYYYMMDD-xxxxxx
    N->>GH: create branch task/<id><br/>commit tasks/<id>/request.json
    N->>GH: open PR
    GH-->>U: PR url

    U->>GH: review + merge PR
    GH->>N: PR-merged webhook (Workflow B)
    N->>GH: read tasks/<id>/request.json
    N->>R: POST /run {task_id, template, inputs}

    R->>R: execute.py
    R->>DT: GET managementZones (idempotency)
    DT-->>R: list
    alt MZ missing
        R->>DT: POST managementZones
        DT-->>R: created
    end
    R->>R: append execution.jsonl

    R->>R: verify.py
    R->>DT: GET managementZones (read-back)
    DT-->>R: confirms MZ
    R->>R: write verify.json

    R-->>N: { status: passed, ... }
    N->>GH: commit result.json + execution.jsonl + verify.json to main
    N-->>U: task closed
```

## Auditability (Rule 4, 17, 18)
Every step is one of:
- a commit (request, execution.jsonl, verify.json, result.json),
- a PR + review (the approval itself),
- a structured JSON line in `tasks/<id>/execution.jsonl`.

Task ID format: `DT-YYYYMMDD-<6 hex>`. Used as folder name, branch suffix,
and PR title prefix.

## Naming convention (Rule 11)
Defined in `config/naming-convention.yaml`. Example:
`myapp_uat_mz_default` = `{app}_{env}_{resource_type}_{name}`.

## Token-minimization (Rule 13)
- Phase 1 makes **zero LLM calls** at runtime. Catalog + templates are
  deterministic.
- When Phase 2 (CodeGen bot) lands, the bot will read `templates/index.yaml`
  and `docs/dt-api-index.md` only — no full repo load.

## Success criteria (Rule 4, 19)
1. Form submission produces a task ID like `DT-20260512-ab12cd`.
2. A PR appears in `dthelper-test2` containing only `tasks/<id>/request.json`.
3. Merging the PR triggers execution; an MZ named `myapp_uat_mz_default`
   exists in the DT tenant.
4. `tasks/<id>/verify.json` has `passed: true`.
5. Re-running with same inputs is idempotent (no duplicate MZ, verify still passes).
6. All artifacts (`request.json`, `execution.jsonl`, `verify.json`,
   `result.json`) are committed to `main` under `tasks/<id>/`.

## NOT in Phase 1
- LLM bots (Interface, CodeGen, Problem Responder) — see Phase 2+.
- Chat / Slack / Teams surface.
- Auto-retry on failure.
- Multiple apps / envs (only `myapp/uat` is configured).
