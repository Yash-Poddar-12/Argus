# Sync Protocol: marking status on every push and pull

> Everyone (human or agent, any IDE) marks what they **pushed** and what they **pulled**. The design goal is that status tracking itself **never causes merge conflicts**.

## 1. Where status lives (and why it doesn't conflict)

| File | Who edits | What goes in it |
|------|-----------|-----------------|
| `docs/03-modules/MXX-*/STATUS.md` | **Only that module's owner** | Module state, WP states, mocks in use, blockers, contract changes, **Update log** (one line per push) |
| `docs/05-status/sync-log/<handle>.md` | **Only that person** | Personal log of every PULL and PUSH, plus notes on what changed for you |
| `docs/05-status/STATUS_BOARD.md` | Nobody (static index) | Links + instructions; live values come from `python scripts/status.py board` |

Because each file has exactly one writer, two teammates never edit the same status file, and status updates never conflict.

## 2. Before every push

```bash
# 1. make sure you're current
git fetch origin && git rebase origin/develop           # resolve code conflicts first

# 2. mark status (module STATUS.md + your sync log in one go)
python scripts/status.py log --module M04 --action PUSH \
    --msg "proximity engine: closing speed + TTC, tests" \
    --wp M04-WP2=IN_REVIEW --state IN_PROGRESS

# 3. commit it WITH the code and push
git add -A
git commit -m "m04(wp2): closing-speed proximity rule"
git push
```

What the command does:

- Sets `Last updated` in your module's summary table
- Optionally sets WP states (`--wp`, repeatable) and the module `State` / `Current focus`
- Inserts `- 2026-09-23 · @you · PUSH · feature/m04-wp2-proximity · <msg>` at the top of the module's Update log
- Inserts the same entry into `docs/05-status/sync-log/<you>.md`

**No Python / prefer manual?** Edit the same three spots by hand. The format is shown in each STATUS.md. Newest line goes directly under `<!-- log:insert -->`.

## 3. After every pull

```bash
git checkout develop && git pull --rebase                 # or pull into your branch
python scripts/status.py changes                          # diff since ORIG_HEAD (git sets it on pull)
```

`changes` shows:
- changed files in `contracts/`, `docs/02-contracts/`, `docs/03-modules/`, the master plan, and `AGENTS.md`
- a **!! warning** listing every contract/catalog file that changed
- new Update-log lines from other modules (what teammates pushed)

Then:

1. **If a contract you consume changed:** read it. If it's additive, nothing to do. If it's breaking, check the linked `contract_change` issue and plan your migration (add it to your STATUS → "Contract changes").
2. **If a dependency went LIVE** (someone marked a WP `DONE`), plan to switch that mock off (STATUS → "Using mocks for").
3. **Record the pull:**

```bash
python scripts/status.py log --action PULL --msg "pulled develop; M06 task-time v1.1 adds p90 (additive), M04-WP6 LIVE -> switch safety mock off"
```

The PULL entry goes only into **your** sync log and is committed with your next push.

## 4. Status vocabulary

| State | Meaning |
|-------|---------|
| `NOT_STARTED` | Not begun |
| `IN_PROGRESS` | Actively being built |
| `MOCKED` | Contract + `public.py` + mocks shipped; consumers can build against it (WP0 done) |
| `BLOCKED` | Can't proceed. **Must** have an entry under Blockers naming who or what blocks it |
| `IN_REVIEW` | PR open |
| `DONE` | Merged to `develop` and meets `DEFINITION_OF_DONE.md` |

Module `State` is the overall state: usually the "least done" of its active WPs, or `DONE` when all WPs are done.

## 5. Actions vocabulary

| Action | When |
|--------|------|
| `PUSH` | You pushed commits |
| `PULL` | You pulled/rebased onto `develop` |
| `MERGE` | Your PR merged into `develop` (optional; useful for the owner's log) |
| `REBASE` | Big rebase that changed your plan |
| `NOTE` | Anything else worth recording (decision, blocker cleared) |

## 6. Agents

Coding agents (Claude Code, Codex, Antigravity, …) must follow the same protocol:

- At the **start** of a session: run `python scripts/status.py changes` (or `git log` on the watched paths) and read your module's STATUS.md.
- At the **end** of a task: run or propose the `status.py log … --action PUSH` command with an accurate one-line summary **before** committing.
- Never edit another module's STATUS.md or another person's sync log.

## 7. Optional automation

To get a reminder on every commit, add a **local** pre-push hook (not committed, so it's opt-in):

```bash
# .git/hooks/pre-push   (chmod +x on macOS/Linux)
#!/bin/sh
git diff --name-only @{u}.. 2>/dev/null | grep -q "docs/03-modules/.*/STATUS.md" || {
  echo "Reminder: no STATUS.md change in this push. Run: python scripts/status.py log --module MXX --action PUSH --msg ..."
}
exit 0
```

CI can later add a soft check that warns when a PR touches a module's paths without touching its STATUS.md.
