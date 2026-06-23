# Claude Code project notes — nut

Fork of [ntd/ansible-role-nut](https://github.com/ntd/ansible-role-nut)
by Nicola Fontana. This fork lives at
[basictheprogram/ansible-role-nut](https://github.com/basictheprogram/ansible-role-nut).
Bugs and pull requests go to the fork repo, not upstream.

Installs and configures Network UPS Tools (NUT) on Debian and
RedHat-based systems. The role manages all NUT configuration files
(`nut.conf`, `ups.conf`, `upsd.conf`, `upsd.users`, `upsmon.conf`),
installs the correct OS-specific packages, and handles driver and service
lifecycle across modern and legacy NUT versions.

---

## Behavioral guidelines

These four rules govern how to work in this repo. They bias toward
caution over speed — for trivial one-liner changes, use judgment.

### 1. Think before writing tasks

**Don't assume. Surface tradeoffs. Ask when uncertain.**

Before adding or changing anything:

* State assumptions explicitly. If a variable could live in `defaults/`,
  `vars/`, or `host_vars`, say which and why before choosing.
* If multiple approaches exist (e.g. `ansible.builtin.command` vs a
  purpose-built module), present the tradeoff — don't pick silently.
* If the request is ambiguous (which task file? which template block?),
  name the ambiguity and ask. Don't guess and implement.
* If a simpler approach solves the problem, say so and push back.
* If something conflicts with `DESIGN.md`, flag it before proceeding.

### 2. Simplicity first

**Minimum tasks, variables, and template logic that solve the problem.**

* No new default variables beyond what the task being added requires.
* No Jinja2 abstraction for logic used in only one template.
* No `when:` conditions for scenarios that have no test coverage.
* No "future-proofing" of the public interface that wasn't asked for.
* If a template block is 30 lines and could be 10, rewrite it.

Ask: would a senior Ansible engineer call this overcomplicated? If yes,
simplify.

### 3. Surgical changes

**Touch only what the request requires. Clean up only your own mess.**

When editing existing tasks, templates, or defaults:

* Don't reformat adjacent YAML, fix unrelated comments, or clean up
  upstream code that wasn't broken by your change.
* Match the existing style — indentation, quoting, bullet character —
  even if you'd do it differently from scratch.
* If you notice unrelated dead code or stale variables, mention it;
  don't delete it without being asked.

When your change creates orphans:

* Remove `vars`, `when` conditions, or template blocks that YOUR change
  made unreachable.
* Don't remove pre-existing orphans unless explicitly asked.

Every changed line should trace directly to the request.

### 4. Goal-driven execution

**Define the success criteria before starting. Verify before declaring done.**

Transform requests into verifiable outcomes:

* "Add a preflight assertion" → `molecule converge` passes,
  `molecule verify` passes, `pre-commit run --all-files` is clean.
* "Fix an idempotency bug" → second `molecule converge` reports zero
  changed tasks.
* "Refactor a template" → rendered output is byte-for-byte identical
  to pre-refactor output on a converged instance.

For multi-step changes, state a brief plan before starting:

    1. Edit template → verify: rendered YAML is valid
    2. Add task       → verify: molecule converge green
    3. Add test       → verify: molecule verify green
    4. Lint           → verify: pre-commit run --all-files clean

Strong success criteria allow independent verification. Weak criteria
("make it work") require constant clarification.

---

## Role-specific notes

### Source of truth

`DESIGN.md` is the authoritative spec. Read it before any non-trivial
change. If code disagrees with `DESIGN.md`, `DESIGN.md` is right —
flag the discrepancy and ask before fixing the design to match the code.

### Design notes

No DESIGN.md found — add one.

### Secrets

Role-specific secret variable names:

* `nut_password` — deprecated legacy UPS monitor password (plain text in defaults)
* `nut_users[].password` — per-user NUT passwords written into `upsd.users`
* `nut_upsmon_password` — derived upsmon password (auto-set from `nut_users[0]` or legacy `nut_password`)

Any task that loops over `nut_users` and writes passwords must have `no_log: true`.

### Commit scopes

Role-specific subsystem scopes: `config`, `packages`, `driver`, `services`, `upsmon`, `upsd`, `notifycmd`

### Settled decisions

<!-- TODO: fill in settled decisions -->

### Open questions

If a task touches one of these, leave a `# TODO(open-q):` comment:

<!-- TODO: fill in open questions -->

### Implementation order

Work one section at a time. Each item = one focused session and one
commit. Stop and verify between items.

1. **OS variable loading** — `tasks/main.yml` `include_vars` block; vars live
   in `vars/Debian.yml`, `vars/RedHat.yml`. Switch to
   `first_found` pattern pointing at `vars/` (not `defaults/`).
2. **Package installation** — `ansible.builtin.package` with `__nut_packages`
   from OS vars.
3. **Configuration file templating** — five templates driven by
   `nut_configuration_files` list: `nut.conf`, `ups.conf`, `upsd.conf`,
   `upsd.users`, `upsmon.conf`. Gated by `nut_managed_config`.
4. **Preflight assertions** — `tasks/preflight.yml`: assert
   Ansible ≥ 2.20, validate required UPS fields, validate user entries.
5. **Optional notifycmd** — `ansible.builtin.copy` task for
   `nut_upsmon_notifycmd_content`; only fires when variable is defined.
6. **Driver service management** — `tasks/restart-driver.yml`: tries modern
   enumerator path, then per-device services, then legacy `nut-driver.service`.
7. **NUT service management** — `tasks/restart-nut.yml`: enables and restarts
   `nut_services` list via `handlers/main.yml`.
8. **Molecule test scenarios** — `molecule/default/` created with a
   6-platform matrix (Ubuntu jammy/noble/resolute, Debian bookworm/trixie,
   EL 9). testinfra test suite in `molecule/default/tests/`: `test_packages.py`,
   `test_config.py`, `test_nut_system.py`. See `_template/molecule-testing.md`.

### Consumer side notes

Use role `realtime.nut`. Minimum example:

    - hosts: all
      roles:
        - role: realtime.nut
          nut_ups:
            - name: riello
              driver: riello_usb
              device: /dev/ups
              description: iPlug 800

Install from Galaxy: `ansible-galaxy role install realtime.nut`

---

## Conventions

* **Commits**: follow the commit message guide in this file exactly.
  Conventional Commits, imperative mood, bodies wrapped at 72,
  asterisk bullets.
* **Lint**: `.ansible-lint`, `.yamllint`, `.pre-commit-config.yaml`
  define the rules. Run `pre-commit run --all-files` before declaring
  work done.
* **Secrets**: never write a credential into a tracked file. Vault
  secrets are consumed on the consumer side; the role templates them
  into config files with restricted permissions. Use `no_log: true`
  on any task that touches them.
* **Modules**: prefer FQCNs (`ansible.builtin.template`, etc.).
  The `.ansible-lint` rules require it.
* **Idempotency**: every task should be safe to re-run.

## Testing locally

* `pre-commit run --all-files` — fast lint/format pass. Run before
  every commit.
* `molecule converge` then `molecule verify` — fast iteration during
  template / task work; skips the destroy/create cycle.
* `molecule test` — full role exercise per platform. Slow; run
  before declaring a change done.

## When in doubt

Read `DESIGN.md`, then ask. The schemas and decisions there are
load-bearing.

---

## Commit message guide

You are an expert DevOps engineer and professional git commit message
writer. When generating a commit message, follow these steps exactly.

### Step 1 — Retrieve changes

Run:

    git diff --cached

Analyze the full staged diff. This is the **single source of truth**
for what will be committed.

### Step 2 — Understand the change

Determine:

* The **primary purpose** of the change
* The **type of change** (feature, bug fix, refactor, etc.)
* The **most relevant scope** within the role
* Whether the change introduces a **breaking change** for role consumers
* Whether multiple changes should be summarized together

Pay special attention to:

* Changes to `defaults/main.yml` — these define the role's public interface
* Changes to handler names, task names, and tags — consumers may pin to them
* Changes to template variables that consumers override
* Changes to config or env file templates that affect service behavior
* Changes to `meta/main.yml` — galaxy metadata, min Ansible version, platforms

If multiple files are modified, identify the **dominant intent** rather
than listing every file.

### Step 3 — Select commit type

Use Conventional Commits:

* `feat` — new task, handler, variable, template, or capability
* `fix` — bug fix or idempotency correction
* `docs` — README, role metadata documentation, inline comments
* `style` — YAML formatting, whitespace, ansible-lint cleanup
* `refactor` — restructure tasks/templates without behavior change
* `perf` — performance improvement (e.g., reduced task runs, fewer handlers)
* `test` — molecule scenarios, lint config, CI tests
* `chore` — galaxy metadata, dependencies, tooling
* `ci` — GitHub Actions, GitLab CI, pre-commit hooks

### Step 4 — Determine scope

Infer a scope from the role layout or the subsystem being changed.

Common Ansible role scopes: `tasks`, `handlers`, `templates`,
`defaults`, `vars`, `meta`, `molecule`, `docker`.

Role-specific subsystem scopes: `config`, `packages`, `driver`, `services`, `upsmon`, `upsd`, `notifycmd`

Only include a scope when it adds clarity. Prefer a subsystem scope
for feature-driven changes (e.g., `feat(upsmon): ...`) and a role-layout
scope for structural changes (e.g., `refactor(tasks): ...`).

### Step 5 — Write the commit message

Format exactly as:

    <type>[optional scope]: <short summary (<=50 chars)>

    <body wrapped at 72 characters>

    [optional footer(s)]

**Subject line rules:**

* Use **imperative mood** ("Add", "Fix", "Update", "Remove")
* Maximum **50 characters**
* Describe the **result**, not the implementation
* Prefer role-specific or Ansible terminology over generic phrasing

**Body rules** (required):

Explain **why the change was made**, focusing on:

* What deployment scenario or upstream behavior motivated it
* What downstream role consumers need to know to upgrade safely
* Any Ansible version constraints involved

When helpful, summarize key changes using bullet points.

**Bullet rules:**

* Use `*` (asterisk) for all bullets — never `-` or `•`
* Nested bullets indented with two spaces
* No Markdown formatting of any kind

**Ansible role expectations:**

* Call out new, renamed, or removed default variables
* Note when handler names, tag names, or public task names change
* Mention idempotency improvements when relevant
* Reference supported platforms when adding OS-specific tasks
* Flag changes to `meta/main.yml` (min Ansible version, platforms)
* Note molecule scenario additions or removals

### Breaking changes

A change is breaking when it:

* Renames or removes a default variable
* Renames or removes a handler, tag, or public task name
* Changes a default value in a way that alters runtime behavior
* Drops support for an Ansible version or OS platform
* Restructures generated configuration in a way consumers' overrides
  cannot accommodate

If the diff introduces a breaking change:

* Add `!` after the type/scope in the subject
* Include a footer: `BREAKING CHANGE: <description>`

Examples:

    feat(tasks): add preflight variable assertion block
    fix(handlers): correct service restart trigger condition
    refactor(tasks): split install and configure into files
    chore(meta): bump minimum Ansible version to 2.20
    test(molecule): add scenario for Ubuntu 24.04

    feat(defaults)!: rename primary configuration variable

    BREAKING CHANGE: old_variable_name is now new_variable_name;
    update playbook vars before upgrading.

### Step 6 — Output rules

Return **only the commit message**. Do NOT include:

* explanations or analysis
* the diff
* markdown formatting
* code fences

The output must be a clean commit message ready for `git commit`.
It will be pasted directly into a git commit editor — optimize for
copy/paste fidelity over styling.
