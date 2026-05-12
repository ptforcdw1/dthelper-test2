---
name: check-naming
description: Validate a proposed resource name against config/naming-convention.yaml. Read-only, deterministic.
---

# check-naming

No LLM judgement — apply the rules. Pure validator.

## Inputs to gather (any one):
- A proposed name string (the literal name the user wants), OR
- An `{app, env, name}` triplet plus a resource type (e.g. `management_zone`)
  — in which case compute the canonical name and return it.

Optional: resource type (`management_zone`, `tag`, `alerting_profile`) for
pattern matching.

## Steps
1. Read `config/naming-convention.yaml`.
2. Apply `validation_regex` to the proposed name. Report PASS/FAIL with the
   regex string shown.
3. If `casing: lowercase`: confirm no uppercase. Report.
4. If a resource type is provided:
   - Read `pattern.<resource_type>` and `resource_codes.<resource_type>`.
   - Reverse-check whether the name could have been produced by the pattern
     for some `{app, env, name}` triplet.
   - If not, warn "doesn't match expected pattern".
5. If `{app, env, name}` provided instead of a literal name:
   - Validate each piece with `validation_regex` and `allowed_envs`.
   - Render: `pattern.format(app=..., env=..., resource_type=..., name=...)`.
   - Return canonical name.

## Output
A short report:
- Validation: PASS / FAIL
- Pattern match: PASS / FAIL / N/A
- Canonical name (if computed)
- Specific rule that failed (if any)

## Do not
- Modify `config/naming-convention.yaml`. This skill is read-only.
