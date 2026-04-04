---
name: git_workflow
description: >
  Git Agent — manages branching strategy, commit standards, pull request workflows,
  and merge policies for the Flock project. This agent is the gatekeeper for all
  code entering the main branch.
---

# Git Workflow Agent — Skill File

## Role

The Git Agent manages the entire source control lifecycle for Flock. It enforces branching conventions, commit message standards, PR workflows, and ensures no code reaches `main` without passing through the proper pipeline (Test Agent → Code Reviewer Agent → Git Agent merge).

---

## Branching Strategy — Git Flow (Simplified)

### Branch Types

| Branch | Pattern | Purpose | Lifetime |
|---|---|---|---|
| `main` | `main` | Production-ready code. Always deployable. | Permanent |
| `develop` | `develop` | Integration branch. All feature branches merge here first. | Permanent |
| `feature/*` | `feature/scoring-engine` | New feature development | Temporary — deleted after merge |
| `fix/*` | `fix/data-fetch-timeout` | Bug fixes | Temporary — deleted after merge |
| `hotfix/*` | `hotfix/critical-crash` | Production emergency fixes (branch from `main`) | Temporary — deleted after merge |
| `refactor/*` | `refactor/api-restructure` | Code restructuring without feature changes | Temporary — deleted after merge |

### Branch Rules

1. **`main` is sacred.** No direct commits. Only merges from `develop` (for releases) or `hotfix/*` (for emergencies).
2. **`develop` is the integration target.** All `feature/*`, `fix/*`, and `refactor/*` branches merge into `develop` via PR.
3. **One feature per branch.** Never mix unrelated changes in a single branch.
4. **Branch names are lowercase, hyphen-separated.** Example: `feature/monte-carlo-engine`, not `feature/MonteCarloEngine`.
5. **Delete branches after merge.** No stale branches.

### Merge Flow

```
feature/scoring-engine ──PR──→ develop ──Release PR──→ main
fix/nan-handling       ──PR──→ develop ──Release PR──→ main
hotfix/critical-crash  ──PR──→ main (and cherry-pick to develop)
```

---

## Commit Message Standards

### Format: Conventional Commits

```
<type>(<scope>): <short description>

<optional body — what and why, not how>

<optional footer — references issues, breaking changes>
```

### Types

| Type | When to Use | Example |
|---|---|---|
| `feat` | New feature | `feat(scoring): add ROE factor calculation` |
| `fix` | Bug fix | `fix(data): handle NaN in yfinance response` |
| `refactor` | Code restructuring (no behavior change) | `refactor(api): split routes into modules` |
| `test` | Adding or updating tests | `test(monte-carlo): add edge case for zero capital` |
| `docs` | Documentation changes | `docs(readme): add setup instructions` |
| `chore` | Build, CI, dependency updates | `chore(deps): upgrade fastapi to 0.115` |
| `style` | Code formatting (no logic change) | `style(scoring): fix indentation in factors.py` |
| `perf` | Performance improvement | `perf(simulation): vectorize monte carlo loop` |

### Scopes (Flock-Specific)

| Scope | Covers |
|---|---|
| `scoring` | Fundamental scoring engine, factors, pillars |
| `simulation` | Monte Carlo, historical stress test, probability engine |
| `data` | Data pipeline, fetchers, caching, cleaning |
| `api` | FastAPI routes, request/response schemas |
| `db` | Database models, migrations, queries |
| `ui` | Frontend HTML/CSS/JS |
| `charts` | Lightweight Charts, Chart.js integration |
| `auth` | Authentication (future) |
| `compliance` | Disclaimers, legal text |
| `infra` | Docker, deployment, CI/CD |

### Rules

1. **Subject line ≤ 72 characters.**
2. **Use imperative mood.** "add feature" not "added feature" or "adds feature."
3. **No period at end of subject.**
4. **Body wraps at 80 characters.**
5. **Reference issues:** `Closes #42` or `Relates to #15`.

---

## Pull Request Workflow

### PR Lifecycle

```
1. Developer creates feature branch from `develop`
2. Developer writes code + commits (following commit standards)
3. Developer opens PR → develop
4. Test Agent runs / validates test coverage
5. Code Reviewer Agent reviews code quality
6. Security Agent reviews (if touching sensitive areas)
7. Git Agent validates:
   - Branch naming ✓
   - Commit message format ✓
   - No merge conflicts ✓
   - All checks pass ✓
8. Git Agent merges (squash merge for features, merge commit for releases)
```

### PR Template

Every PR must include:

```markdown
## What does this PR do?
<!-- Brief description of the change -->

## Type of Change
- [ ] Feature (`feat`)
- [ ] Bug Fix (`fix`)
- [ ] Refactor (`refactor`)
- [ ] Test (`test`)
- [ ] Documentation (`docs`)

## Checklist
- [ ] Code follows project conventions
- [ ] Tests written and passing
- [ ] No new warnings introduced
- [ ] Self-reviewed the diff
- [ ] Relevant skill files updated (if patterns changed)

## Screenshots / Evidence
<!-- If UI change, add before/after screenshots -->
```

### Merge Strategies

| Target Branch | Merge Strategy | Why |
|---|---|---|
| `feature/*` → `develop` | **Squash merge** | Clean history — one commit per feature |
| `develop` → `main` | **Merge commit** | Preserves the full integration history |
| `hotfix/*` → `main` | **Merge commit** | Audit trail for emergency fixes |

---

## Release Process

### Versioning: Semantic Versioning (SemVer)

```
MAJOR.MINOR.PATCH
  │      │     └── Bug fixes, minor changes
  │      └──────── New features (backward compatible)
  └─────────────── Breaking changes
```

**MVP starts at `0.1.0`** — the leading `0` means "pre-stable, API may change."

### Release Steps

1. All features for the release are merged into `develop`
2. Create release PR: `develop` → `main`
3. Update version in relevant files
4. Tag the merge commit: `git tag v0.1.0`
5. Deploy from `main`

---

## Git Agent Operating Rules

1. **Never force-push to `main` or `develop`.** History is immutable on shared branches.
2. **Always rebase feature branches on latest `develop` before merging.** No unnecessary merge commits in feature branches.
3. **Validate all PRs** against the checklist before approving merge.
4. **Coordinate with Code Reviewer Agent** — Git Agent does not merge until Reviewer approves.
5. **Coordinate with Test Agent** — Git Agent does not merge until tests pass.
6. **Log all merges** — maintain a changelog or rely on conventional commit tooling to auto-generate one.
7. **Flag stale branches** — any branch >7 days without activity gets flagged for cleanup.

---

## Integration with Other Agents

| Agent | How Git Agent Interacts |
|---|---|
| **Code Reviewer Agent** | Reviewer approves/requests changes on PR. Git Agent waits for approval. |
| **Test Agent** | Test Agent runs tests on PR branch. Git Agent checks test status before merge. |
| **Security Agent** | Security Agent reviews PRs touching auth, data, or API layers. |
| **River (Architect)** | River has override authority on any merge decision. |
