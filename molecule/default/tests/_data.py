"""Shared constants for the ansible-role-nut Molecule test suite.

All values here must stay in sync with molecule/default/converge.yml and
the role's vars/ files. Do not import from conftest.py in test files —
conftest is a pytest plugin, not a regular module, and the import breaks
when __init__.py is present.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# OS-family detection
# ---------------------------------------------------------------------------

#: Distribution names that map to the RedHat OS family.
REDHAT_DISTROS: frozenset[str] = frozenset(
    {
        "rocky",
        "almalinux",
        "rhel",
        "centos",
        "ol",
        "fedora",
    }
)

# ---------------------------------------------------------------------------
# Package expectations (must match vars/Debian.yml and vars/RedHat.yml)
# ---------------------------------------------------------------------------

#: NUT packages installed on Debian-family systems.
DEBIAN_PKGS: tuple[str, ...] = ("nut-client", "nut-server", "nut-monitor")

#: NUT packages installed on RedHat-family systems.
REDHAT_PKGS: tuple[str, ...] = ("nut-client", "nut")

# ---------------------------------------------------------------------------
# Configuration directory (must match __nut_config_dir in vars/*.yml)
# ---------------------------------------------------------------------------

#: Config directory on Debian/Ubuntu.
DEBIAN_CONFIG_DIR: str = "/etc/nut"

#: Config directory on RedHat/EL (vars/RedHat.yml: /etc/ups/).
REDHAT_CONFIG_DIR: str = "/etc/ups"

# ---------------------------------------------------------------------------
# Configuration file inventory
# ---------------------------------------------------------------------------

#: Files written when nut_managed_config is true and both nut-server.service
#: and nut-monitor.service are present in nut_services.
CONFIG_FILES: tuple[str, ...] = (
    "nut.conf",
    "ups.conf",
    "upsd.conf",
    "upsd.users",
    "upsmon.conf",
)

# ---------------------------------------------------------------------------
# Converge fixture values — MUST match molecule/default/converge.yml
# ---------------------------------------------------------------------------

#: NUT mode written to nut.conf (nut_mode).
TEST_NUT_MODE: str = "standalone"

#: UPS name used in ups.conf and upsmon.conf MONITOR directive (nut_ups[0].name).
TEST_UPS_NAME: str = "testups"

#: UPS driver written to ups.conf (nut_ups[0].driver).
TEST_UPS_DRIVER: str = "dummy-ups"

#: UPS device/port written to ups.conf (nut_ups[0].device).
TEST_UPS_DEVICE: str = "testups.dev"

#: NUT user name written to upsd.users (nut_users[0].name).
TEST_USER_NAME: str = "testmonitor"

#: NUT host written to upsmon.conf MONITOR directive (nut_host default).
TEST_NUT_HOST: str = "localhost"

#: nut_upsmon_monitors fixture — remote NUT servers monitored in addition
#: to the local testups UPS. remoteups3 omits "role" and "port" on purpose,
#: to exercise the nut_upsmon_role/nut_powervalue defaulting in the
#: upsmon.conf.j2 template.
TEST_UPSMON_MONITORS: tuple[dict[str, str], ...] = (
    {
        "name": "remoteups1",
        "host": "remote1.example.test",
        "user": "remoteuser1",
        "password": "remotepass1",
        "role": "secondary",
    },
    {
        "name": "remoteups2",
        "host": "remote2.example.test",
        "port": "3493",
        "user": "remoteuser2",
        "password": "remotepass2",
        "role": "secondary",
    },
    {
        "name": "remoteups3",
        "host": "remote3.example.test",
        "user": "remoteuser3",
        "password": "remotepass3",
    },
)
