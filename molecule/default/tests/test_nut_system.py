"""Tests for the NUT system user and group created by package installation.

NUT packages create a 'nut' system user and group as part of their
post-install scripts. These tests verify that the system-level identity
required for config file ownership (root:nut, mode 0640) exists.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from testinfra.host import Host


def test_nut_group_exists(host: Host) -> None:
    """The 'nut' system group exists after package installation."""
    assert host.group("nut").exists


def test_nut_user_exists(host: Host) -> None:
    """The 'nut' system user exists after package installation."""
    assert host.user("nut").exists


def test_nut_user_primary_group(host: Host) -> None:
    """The 'nut' user's primary group is 'nut'."""
    assert host.user("nut").group == "nut"
