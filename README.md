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
Tools) on Debian and RedHat-based systems.

Requirements
------------

Ansible core >= 2.20.

Supported Platforms
-------------------

| OS Family | Versions                                  |
|-----------|-------------------------------------------|
| Ubuntu    | 22.04 Jammy, 24.04 Noble, 26.04 Resolute  |
| Debian    | 12 Bookworm, 13 Trixie                    |
| EL        | 9, 10                                     |

Role Variables
--------------

Available variables are listed below, along with default values (see
`defaults/main.yml`):

### Generic Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `nut_managed_config` | `true` | If false, no configuration files under `/etc/nut/` are written — you manage them yourself. |
| `nut_enable_service` | `true` | Whether to start and enable the NUT services after configuration. |
| `nut_extra_packages` | `[]` | Additional OS packages to install alongside the NUT packages, e.g. `bsd-mailx` for a notify script that shells out to `mail`. |
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
| `nut_upsmon_role` | Auto-derived | Override the upsmon type field. Defaults to `nut_role`, `nut_users[0].role`, or `master`. NUT 2.8+ (Ubuntu 26.04 Resolute) uses `primary`/`secondary`; use those values on modern systems. |
| `nut_upsmon_extra` | Multi-line config | Raw text appended verbatim to `upsmon.conf`. |
| `nut_upsmon_monitors` | `[]` | List of remote NUT servers to monitor, each with its own host/user/password/role. See [Multi-server monitoring](#multi-server-monitoring) below. |
| `nut_upsmon_notifycmd` | undefined | Path where the NOTIFYCMD script is installed. |
| `nut_upsmon_notifycmd_content` | undefined | Content written to the `nut_upsmon_notifycmd` path. |
| `nut_user` | empty | **DEPRECATED** — Legacy upsmon username. Migrate to `nut_users`. |
| `nut_password` | empty | **DEPRECATED** — Legacy upsmon password. Migrate to `nut_users`. |
| `nut_role` | empty | **DEPRECATED** — Legacy upsmon role. Migrate to `nut_users`. |

### OS-specific variables (vars/)

The following variables are loaded from `vars/<OsFamily>.yml` via
`include_vars` and are **not** user-overridable in the normal sense —
they reflect package names and paths that differ per distribution.

| Variable | Debian | RedHat |
|----------|--------|--------|
| `__nut_packages` | `nut-client`, `nut-server`, `nut-monitor` | `nut-client`, `nut` |
| `__nut_config_dir` | `/etc/nut/` | `/etc/ups/` |

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
3. **Install packages** — installs `__nut_packages` for the detected OS,
   plus any `nut_extra_packages`.
4. **Template configuration files** — writes `nut.conf`, and conditionally
   `ups.conf`, `upsd.conf`, `upsd.users`, `upsmon.conf` based on which
   services are enabled. Removes any of those five files that were
   previously managed but are no longer needed (e.g. `ups.conf` after
   switching to netclient mode).
5. **Install notifycmd script** — copies `nut_upsmon_notifycmd_content`
   to `nut_upsmon_notifycmd` when the variable is defined.
6. **Driver services** — on handler trigger, enables per-device driver
   services (modern enumerator → per-device → legacy fallback).
7. **NUT services** — on handler trigger, enables and restarts `nut_services`.

NUT 2.8+ Compatibility
----------------------

NUT 2.8 renamed the upsmon role values:

- `master` → `primary`
- `slave` → `secondary`

Ubuntu 26.04 Resolute ships NUT 2.8+. Use `primary`/`secondary` for
`nut_upsmon_role` on any platform running NUT 2.8 or later. The legacy
values still work in NUT 2.8 but produce deprecation warnings.

To discover which NUT version is installed:

```bash
upsd --version
```

Example Playbook
----------------

**Standalone** — UPS connected locally:

```yaml
- hosts: all
  roles:
    - role: realtime.nut
      nut_ups:
        - name: riello
          driver: riello_usb
          device: /dev/ups
          description: iPlug 800
```

**Netclient** — monitoring a single remote NUT server (e.g. a Synology
NAS). The local host runs only `nut-monitor`. You **must** set
`nut_ups: []` explicitly — omitting it causes the non-empty role default
to apply, which starts a local driver and fails:

```yaml
- hosts: all
  roles:
    - role: realtime.nut
      nut_mode: netclient
      nut_ups: []               # required: suppresses ups.conf and local driver
      nut_services:
        - nut-monitor.service
      nut_upsmon_monitors:
        - name: ups               # name from `upsc -l <host>`
          host: 10.0.1.201        # IP of the remote NUT server
          user: "{{ vault_nut_upsmon_user }}"
          password: "{{ vault_nut_upsmon_password }}"
          role: secondary          # NUT 2.8+; use 'slave' for older NUT
```

To discover the UPS name exported by a remote server:

```bash
upsc -l <host>
```

### Multi-server monitoring

`nut_upsmon_monitors` is a list, so one host can monitor any number of
remote NUT servers — each with its own host and credentials — independent
of (and in addition to) any locally-driven UPS in `nut_ups`. For example,
a dedicated monitoring host (`uart`) watching three UPSes attached to
three different NUT servers, each running its own local driver:

```yaml
- hosts: uart
  roles:
    - role: realtime.nut
      nut_mode: netclient
      nut_ups: []                 # uart has no local UPS; it only monitors remote servers
      nut_services:
        - nut-monitor.service
      nut_upsmon_monitors:
        - name: ups1
          host: synology1.lan
          user: monitor
          password: "{{ vault_synology1_monitor_password }}"
          role: secondary
        - name: ups2
          host: synology2.lan
          user: monitor
          password: "{{ vault_synology2_monitor_password }}"
          role: secondary
        - name: ups3
          host: pve-02.lan
          user: monitor
          password: "{{ vault_pve02_monitor_password }}"
          role: secondary
```

Each entry in `nut_upsmon_monitors` requires `name`, `host`, `user`, and
`password`. `role` defaults to `nut_upsmon_role` if omitted; use
`secondary` here since `synology1`, `synology2`, and `pve-02` are each
already running their own `primary` upsmon against their locally-attached
UPS — `uart` is an additional observer, not the system issuing shutdown
commands.

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
Please open issues and pull requests here.
