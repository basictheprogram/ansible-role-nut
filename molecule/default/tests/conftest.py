"""pytest-testinfra fixtures for the ansible-role-nut Molecule suite."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._data import DEBIAN_CONFIG_DIR, REDHAT_CONFIG_DIR, REDHAT_DISTROS

if TYPE_CHECKING:
    from testinfra.host import Host


@pytest.fixture(scope="module")
def nut_config_dir(host: Host) -> str:
    """Return the NUT configuration directory path for the current host.

    Maps ansible_os_family to the value of __nut_config_dir in vars/*.yml:
    - Debian family  → /etc/nut  (vars/Debian.yml)
    - RedHat family  → /etc/ups  (vars/RedHat.yml)
    """
    dist: str = host.system_info.distribution.lower()
    if dist in REDHAT_DISTROS:
        return REDHAT_CONFIG_DIR
    return DEBIAN_CONFIG_DIR
