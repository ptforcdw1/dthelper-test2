---
name: add-catalog-item
description: Expose an existing template via the self-serve catalog. Creates the form schema and registers in catalog/index.yaml.
---

# add-catalog-item

Use when an existing template should be invocable via the n8n catalog form
(Rule 7). For complex / one-off asks, use `/new-request` instead.

## Pre-conditions
- The target template exists under `templates/<id>/` AND is in
  `templates/index.yaml`. If not, run `/add-template` first.

## Inputs to gather
- Template id (must match `templates/index.yaml`)
- Catalog title (sentence case)
- Catalog description (one line)
- For each template input: a user-facing `label`, plus optional `help`,
  `pattern` regex, `options` (for enum)

## Steps
1. Verify the template exists in `templates/index.yaml`. If not, STOP.
2. Verify `catalog/index.yaml` does NOT already list this id. If it does, STOP.
3. Create `catalog/items/<id>.yaml` mirroring the shape of
   `catalog/items/create-management-zone.yaml`:
   - Top-level: id, title, template, inputs[]
   - Each input: name, label, type, required, plus optional pattern/options/help
   - Always include a `requester` input (string, required,
     label "Your email (for audit)")
4. Append the new item to `catalog/index.yaml` under `items:`.
5. Remind the user the n8n form must be rebuilt to match — point to
   `automation/n8n/README.md`.

## Rules for inputs (per Rule 14)
- Use human-meaningful names. NEVER include `*_id` fields.
- If the template needs an ID, the script must resolve it from a name at
  runtime via `lib/dt_client.py`.
- Allowed types: `string`, `enum` (with `options`), `int`, `bool`.
- Every input must set `required: true|false` explicitly.

## Done when
- `catalog/items/<id>.yaml` exists and matches the template's input contract.
- `catalog/index.yaml` lists the new item.
- All inputs are human-friendly.
