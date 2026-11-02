---
name: skill-maintenance
description: Use when an agent mistake is caught — by the compiler, a test, code review or a human correction — and the same mistake could happen again. Turns the correction into a rule in the right skill, through the same merge-request review as code. Also use for periodic pruning of the skills. Triggers on "add a rule", "remember this", "the agent keeps doing", "update the skill", "learned rule", "same mistake again", "prune skills".
---

# Keeping the skills alive

Skills are code. They are versioned, reviewed and maintained. A skill that never changes after week one
stops matching the codebase, and the agent repeats the same mistakes.

## When to add a rule

Add one when **all three** hold:

1. The mistake was caught: compile error, failing test, review comment, or a developer's correction.
2. It is **reusable**: it would happen again on a different file or task.
3. No existing rule already covers it. If one does, sharpen that rule instead.

Do not add rules for one-off typos or for things the compiler already catches instantly and unambiguously.

## Where

| Mistake about | Skill |
|---------------|-------|
| language, RTL, XE7 availability, memory | `delphi-xe7` |
| build, tests, CI | `delphi-build-test` |
| threads, UI responsiveness | `vcl-threading` |
| frames, CRC, versions, firmware upload | `binary-protocol` |
| review blind spots | `delphi-review` |
| project conventions, units, components | the project's `CLAUDE.md` |

## Format

Inside the `<!-- learned-rules -->` block of that skill, one entry per rule:

```markdown
- **Never use `TThread.ForceQueue`** — not in XE7 (10.2 Tokyo). Use `TThread.Queue`.
  Evidence: MR !123, E2003 in Panel.Session.pas. Added 2026-11-02.
```

- **Wrong → right → why**, in one or two lines.
- **Evidence:** the merge request, the compiler message or the review comment.
- **Date.**

## Process

1. The agent proposes the rule in the same merge request as the fix, or in a separate one.
2. A developer reviews it like code. Skills that teach the agent wrong things are worse than no skills.
3. Merged rules are shared by the whole team through the repository.

## Pruning (monthly or quarterly)

- Merge duplicate rules, generalise near-duplicates.
- Delete rules that no longer apply (Delphi upgrade, refactored module).
- Move a rule from a project `CLAUDE.md` into a skill when it proves general, and the other way round.
- Keep each `SKILL.md` short enough to be read in full; move depth into reference files.

## Signals the skills need work

- The same review comment appears on several merge requests.
- The agent needs more than two build iterations on routine changes.
- Developers stop trusting the agent's first draft for a whole area of the code.
