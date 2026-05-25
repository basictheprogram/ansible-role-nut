Ansible Role: NUT
=================

[![CI](https://github.com/basictheprogram/ansible-role-nut/actions/workflows/ci.yml/badge.svg)](https://github.com/basictheprogram/ansible-role-nut/actions/workflows/ci.yml)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-realtime.nut-blue?logo=ansible)](https://galaxy.ansible.com/ui/standalone/roles/realtime/nut/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/basictheprogram/ansible-role-nut/blob/master/.pre-commit-config.yaml)

> **Fork notice** — This is a fork of
> [ntd/ansible-role-nut](https://github.com/ntd/ansible-role-nut) by
> Nicola Fontana. Bugs, feature requests, and pull requests for this fork
> should be submitted to
> **[basictheprogram/ansible-role-nut](https://github.com/basictheprogram/ansible-role-nut/issues)**.
> Issues that reproduce against the upstream role may also be reported at
> [ntd/ansible-role-nut](https://github.com/ntd/ansible-role-nut/issues).

Installs and configures [NUT](http://networkupstools.org/) (Network UPS
Tools) on Debian, Arch Linux, and RedHat-based systems.

Requirements
------------

Ansible core >= 2.20.

Supported Platforms
-------------------

| OS Family  | Versions                                    |
|------------|---------------------------------------------|
| Ubuntu     | 22.04 Jammy, 24.04 Noble, 26.04 Resolute    |
| Debian     | 12 Bookworm, 13 Trixie                      |
| EL         | 9                                           |
| Arch Linux | rolling (any)                               |

Role Variables
--------------

Available variables are listed below, along with default values (see
`defaults/main.yml`):

### Generic Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `nut_managed_config` | `true` | If false, no configuration files under `/etc/nut/` are written — you manage them yourself. |
| `nut_enable_service` | `true` | Whether to start and enable the NUT services after configuration. |
| `nut_mode` | `standalone` | NUT mode setting (see `man 5 nut.conf` MODE directive). |
| `nut_extra` | empty | Raw text appended verbatim to `nut.conf`. Must not use spaces around `=` (shell-sourced). |
| `nut_services` | `[nut-server.service, nut-monitor.service, nut.target]` | List of non-driver NUT service units to enable. |
| `nut_users` | See example below | List of users written into `upsd.users`. The first entry is used for upsmon unless `nut_upsmon_*` variables are set explicitly. |
| `nut_ups` | `[]` | List of UPS device definitions written into `ups.conf`. |
| `nut_ups_extra` | `maxretry = 3` | Raw text appended verbatim to `ups.conf`. |
| `nut_upsd_extra` | Multi-line config | Raw text appended verbatim to `upsd.conf`. |
| `nut_maxretry` | `3` | **DEPRECATED** — Use `nut_ups_extra` instead. |

### UPSMON Configuration

These settings are primarily used for the local `upsmon.conf` configuration.

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `nut_host` | `localhost` | Hostname of the NUT server written into the MONITOR directive. |
| `nut_powervalue` | `1` | Power value for the MONITOR directive (see `man 5 upsmon.conf`). |
| `nut_upsmon_user` | Auto-derived | Override the upsmon monitor username. Defaults to `nut_user` or `nut_users[0].name`. |
| `nut_upsmon_password` | Auto-derived | Override the upsmon monitor password. Defaults to `nut_password` or `nut_users[0].password`. |
| `nut_upsmon_role` | Auto-derived | Override the upsmon type field. Defaults to `nut_role`, `nut_users[0].role`, or `master`. |
| `nut_upsmon_extra` | Multi-line config | Raw text appended verbatim to `upsmon.conf`. |
| `nut_upsmon_notifycmd` | undefined | Path where the NOTIFYCMD script is installed. |
| `nut_upsmon_notifycmd_content` | undefined | Content written to the `nut_upsmon_notifycmd` path. |
| `nut_user` | empty | **DEPRECATED** — Legacy upsmon username. Migrate to `nut_users`. |
| `nut_password` | empty | **DEPRECATED** — Legacy upsmon password. Migrate to `nut_users`. |
| `nut_role` | empty | **DEPRECATED** — Legacy upsmon role. Migrate to `nut_users`. |

### OS-specific variables (vars/)

The following variables are loaded from `vars/<OsFamily>.yml` via
`include_vars` and are **not** user-overridable in the normal sense —
they reflect package names and paths that differ per distribution.

| Variable | Debian | RedHat | Arch Linux |
|----------|--------|--------|------------|
| `__nut_packages` | `nut-client`, `nut-server`, `nut-monitor` | `nut-client`, `nut` | `nut` |
| `__nut_config_dir` | `/etc/nut/` | `/etc/nut/` | `/etc/ups/` |

### UPS Definition

```yaml
nut_ups:
  - name: UPS
    driver: riello_ups
    device: /dev/ttyUSB0
    description: Some descriptive information
    extra: |
      maxretry = 10
      retrydelay = 1
```

`name` is an arbitrary string that must uniquely identify the UPS.

`driver` depends on your hardware and must be one of the [available NUT
drivers](http://networkupstools.org/stable-hcl.html).

`device` is the path where the UPS is connected (typically a USB or serial
device).

`description` is optional and used for debugging and reporting.

`extra` is optional multiline text inserted verbatim into the UPS section.

### Users Definition

```yaml
nut_users:
  - name: nutuser1
    password: password1
    role: primary  # DEPRECATED: use extra instead
  - name: nutuser2
    password: password2
    extra: |
      role = admin
      actions = set
      actions = fsd
```

The legacy variables `nut_user`, `nut_password`, and `nut_role` are
**deprecated**. If `nut_user` is defined, the legacy variables are added
to `upsd.users` and used in `upsmon.conf`. Otherwise the first entry of
`nut_users` is used.

This default behaviour can be overridden by explicitly setting the
`nut_upsmon_*` variables. In that case you are responsible for creating
the matching user in `nut_users`.

Task Flow
---------

1. **Include OS-specific variables** — loads `vars/<OsFamily>.yml` for
   package names and config directory path.
2. **Preflight assertions** — validates Ansible version (>= 2.20),
   required fields on each `nut_ups` entry (`name`, `driver`, `device`),
   and required fields on each `nut_users` entry (`name`, `password`).
3. **Install packages** — installs `__nut_packages` for the detected OS.
4. **Template configuration files** — writes `nut.conf`, and conditionally
   `ups.conf`, `upsd.conf`, `upsd.users`, `upsmon.conf` based on which
   services are enabled.
5. **Install notifycmd script** — copies `nut_upsmon_notifycmd_content`
   to `nut_upsmon_notifycmd` when the variable is defined.
6. **Driver services** — on handler trigger, enables per-device driver
   services (modern enumerator → per-device → legacy fallback).
7. **NUT services** — on handler trigger, enables and restarts `nut_services`.

Example Playbook
----------------

```yaml
- hosts: all
  roles:
    - role: ntd.nut
      nut_ups:
        - name: riello
          driver: riello_usb
          device: /dev/ups
          description: iPlug 800
```

For more examples, see `tests/test.yml`.

License
-------

MIT

Author Information
------------------

The original role was created in 2016 by Nicola Fontana (ntd@entidi.it)
and is maintained upstream at
[ntd/ansible-role-nut](https://github.com/ntd/ansible-role-nut).

This fork is maintained at
[basictheprogram/ansible-role-nut](https://github.com/basictheprogram/ansible-role-nut).
Please open issues and pull requests there.
