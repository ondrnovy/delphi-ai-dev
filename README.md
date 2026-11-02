# delphi-ai-dev

How I set up AI-assisted development on a **large, long-lived Delphi XE7 VCL desktop application** that
talks to hardware: device configuration, binary protocols, firmware updates. Skills for coding agents
(Claude Code, Codex, Cursor, …) plus the workflow around them: build, unit tests, UI tests, review, and
skills that learn from every caught mistake.

This is the starter kit I bring when I join a Delphi team: general Delphi knowledge pinned to the team's
compiler version, a closed loop in which the agent builds, tests and clicks through its own change, and a
process that turns every caught mistake into a reviewed rule. It is meant to be tuned on the real codebase
in the first weeks.

## Why

Agents are good at Delphi when they get the right context. I have taught an agent a proprietary,
Pascal-based ERP scripting dialect from documentation that is not publicly available; after a short
feedback loop it compiles cleanly almost every time. Standard Delphi is easier. What matters:

1. **The right language level.** Most agent errors on an old codebase are modern syntax that the old
   compiler does not know (inline variables, managed records, `[weak]`, multiline strings…).
2. **A closed loop.** The agent builds, runs the unit tests and drives the running application itself,
   and reads the compiler output, test results and UI tree instead of guessing.
3. **Skills that learn.** Every mistake caught by the compiler, a test or a reviewer becomes a rule, merged through code review.

## Skills

**Writing code**

| Skill | What it gives the agent |
|-------|-------------------------|
| [`delphi-xe7`](skills/delphi-xe7/SKILL.md) | Language and RTL for XE7: what exists, what does not, memory, strings, exceptions, common agent mistakes |
| [`delphi-architecture`](skills/delphi-architecture/SKILL.md) | Layers, where new code goes, getting logic out of forms in safe steps |
| [`vcl-threading`](skills/vcl-threading/SKILL.md) | Device I/O off the main thread, `Synchronize` vs `Queue`, stopping threads, deadlocks |
| [`binary-protocol`](skills/binary-protocol/SKILL.md) | `TBytes`, framing, byte order, CRC with test vectors, firmware-version capabilities, firmware upload |
| [`delphi-to-csharp`](skills/delphi-to-csharp/SKILL.md) | Porting logic to C#/.NET with shared test vectors proving identical behaviour |

**Verifying it**

| Skill | What it gives the agent |
|-------|-------------------------|
| [`delphi-build-test`](skills/delphi-build-test/SKILL.md) | Command-line build (`rsvars` + `msbuild`) and test run, reading compiler output, CI parity |
| [`delphi-testing`](skills/delphi-testing/SKILL.md) | Which test to write, DUnitX/DUnit, fakes instead of hardware, characterization tests for legacy code, leak detection |
| [`vcl-ui-testing`](skills/vcl-ui-testing/SKILL.md) | Driving the running VCL application through Windows UI Automation (pywinauto): inspect the control tree, click through flows, screenshots, UI smoke tests in CI |
| [`delphi-review`](skills/delphi-review/SKILL.md) | Defect-first review checklist, including firmware compatibility |

**Keeping it alive**

| Skill | What it gives the agent |
|-------|-------------------------|
| [`skill-maintenance`](skills/skill-maintenance/SKILL.md) | How a caught mistake becomes a rule, reviewed like code, and how the skills are pruned |

Plus [`templates/CLAUDE.md`](templates/CLAUDE.md): the project-specific part (paths, build and test commands,
code map, conventions) that sits next to the general skills.

## How the loop works

```
task ─► plan (layer + test) ─► change ─► build ─► unit tests ─► UI smoke ─► review ─► merge
                 ▲                          │          │             │          │
                 └──── learned rule (MR) ◄──┴──────────┴─────────────┴──────────┘
                         when a mistake could happen again
```

| Step | Who | Tool |
|------|-----|------|
| Plan: which layer, which test | agent proposes, developer approves | `delphi-architecture` |
| Change | agent | `delphi-xe7`, `vcl-threading`, `binary-protocol` |
| Build, unit and protocol tests | agent, then CI | `delphi-build-test`, `delphi-testing` |
| Click through the change, smoke tests | agent locally, CI on an interactive runner | `vcl-ui-testing` |
| Review | agent first, then a developer | `delphi-review` |
| Hardware in the loop | test stand before release | outside the agent loop |

The agent never touches real devices or the production cloud: the application gets a fake transport for
tests, demos and UI automation.

## Install

Copy `skills/` into the project's `.claude/skills/` (Claude Code) or the equivalent folder of another agent,
and `templates/CLAUDE.md` into the repository root, then fill in the placeholders. UI testing needs Python
with `pywinauto` and `pillow` on the Windows machine.

## Status

Version 0.1. The content follows the Delphi XE7 documentation and RTL, but it has **not yet been run against
a real XE7 codebase**. Items whose availability in XE7 still needs checking are marked in `delphi-xe7`.
Expect the first weeks on a real project to add learned rules and remove generic ones.

## Credits and license

`delphi-xe7` is derived from the `delphi` skill and `delphi-review` is inspired by `delphi-code-smells` in
[danieleteti/delphi-ai-skills](https://github.com/danieleteti/delphi-ai-skills) by Daniele Teti, licensed
under Apache-2.0. This repository is licensed under Apache-2.0 as well, see [LICENSE](LICENSE) and [NOTICE](NOTICE).
