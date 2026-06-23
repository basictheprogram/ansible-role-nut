"""Tests for NUT configuration files produced by the role.

Checks existence, ownership, permissions, and key content for every file
written by the role when nut_managed_config is true and both nut-server
and nut-monitor services are present in nut_services.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._data import (
    CONFIG_FILES,
    TEST_NUT_HOST,
    TEST_NUT_MODE,
    TEST_UPS_DEVICE,
    TEST_UPS_DRIVER,
    TEST_UPS_NAME,
    TEST_UPSMON_MONITORS,
    TEST_USER_NAME,
)

if TYPE_CHECKING:
    from testinfra.host import Host


# ---------------------------------------------------------------------------
# Config directory
# ---------------------------------------------------------------------------


def test_config_directory_exists(host: Host, nut_config_dir: str) -> None:
    """The NUT configuration directory exists and is a directory."""
    d = host.file(nut_config_dir)
    assert d.exists
    assert d.is_directory


# ---------------------------------------------------------------------------
# Existence and permissions for every config file
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("filename", CONFIG_FILES)
def test_config_file_exists(host: Host, nut_config_dir: str, filename: str) -> None:
    """Each expected config file exists as a regular file."""
    f = host.file(f"{nut_config_dir}/{filename}")
    assert f.exists
    assert f.is_file


@pytest.mark.parametrize("filename", CONFIG_FILES)
def test_config_file_owner(host: Host, nut_config_dir: str, filename: str) -> None:
    """Each config file is owned by root:nut."""
    f = host.file(f"{nut_config_dir}/{filename}")
    assert f.user == "root"
    assert f.group == "nut"


@pytest.mark.parametrize("filename", CONFIG_FILES)
def test_config_file_mode(host: Host, nut_config_dir: str, filename: str) -> None:
    """Each config file has mode 0640 (root read/write, nut read)."""
    f = host.file(f"{nut_config_dir}/{filename}")
    assert f.mode == 0o640


# ---------------------------------------------------------------------------
# Content assertions — nut.conf
# ---------------------------------------------------------------------------


def test_nut_conf_mode_directive(host: Host, nut_config_dir: str) -> None:
    """nut.conf contains the expected MODE directive."""
    content: str = host.file(f"{nut_config_dir}/nut.conf").content_string
    assert f"MODE={TEST_NUT_MODE}" in content


# ---------------------------------------------------------------------------
# Content assertions — ups.conf
# ---------------------------------------------------------------------------


def test_ups_conf_ups_section(host: Host, nut_config_dir: str) -> None:
    """ups.conf contains the test UPS stanza header."""
    content: str = host.file(f"{nut_config_dir}/ups.conf").content_string
    assert f"[{TEST_UPS_NAME}]" in content


def test_ups_conf_driver(host: Host, nut_config_dir: str) -> None:
    """ups.conf contains the expected driver line."""
    content: str = host.file(f"{nut_config_dir}/ups.conf").content_string
    assert f"driver = {TEST_UPS_DRIVER}" in content


def test_ups_conf_port(host: Host, nut_config_dir: str) -> None:
    """ups.conf contains the expected port (device) line."""
    content: str = host.file(f"{nut_config_dir}/ups.conf").content_string
    assert f"port = {TEST_UPS_DEVICE}" in content


# ---------------------------------------------------------------------------
# Content assertions — upsd.users
# ---------------------------------------------------------------------------


def test_upsd_users_section(host: Host, nut_config_dir: str) -> None:
    """upsd.users contains a stanza for the test user."""
    content: str = host.file(f"{nut_config_dir}/upsd.users").content_string
    assert f"[{TEST_USER_NAME}]" in content


# ---------------------------------------------------------------------------
# Content assertions — upsmon.conf
# ---------------------------------------------------------------------------


def test_upsmon_conf_monitor_directive(host: Host, nut_config_dir: str) -> None:
    """upsmon.conf contains a MONITOR directive referencing the test UPS."""
    content: str = host.file(f"{nut_config_dir}/upsmon.conf").content_string
    assert "MONITOR" in content
    assert TEST_UPS_NAME in content


def test_upsmon_conf_monitor_host(host: Host, nut_config_dir: str) -> None:
    """upsmon.conf MONITOR directive uses the expected NUT host."""
    content: str = host.file(f"{nut_config_dir}/upsmon.conf").content_string
    assert f"{TEST_UPS_NAME}@{TEST_NUT_HOST}" in content


def test_upsmon_conf_monitor_user(host: Host, nut_config_dir: str) -> None:
    """upsmon.conf MONITOR directive references the test monitor user."""
    content: str = host.file(f"{nut_config_dir}/upsmon.conf").content_string
    assert TEST_USER_NAME in content


# ---------------------------------------------------------------------------
# Content assertions — upsmon.conf multi-server monitoring
# (nut_upsmon_monitors — see TEST_UPSMON_MONITORS in _data.py)
# ---------------------------------------------------------------------------


def test_upsmon_conf_monitor_line_count(host: Host, nut_config_dir: str) -> None:
    """One MONITOR line per UPS, no more.

    There should be one for the local UPS plus one per nut_upsmon_monitors
    entry.
    """
    content: str = host.file(f"{nut_config_dir}/upsmon.conf").content_string
    monitor_lines = [line for line in content.splitlines() if line.startswith("MONITOR ")]
    assert len(monitor_lines) == 1 + len(TEST_UPSMON_MONITORS)


@pytest.mark.parametrize("monitor", TEST_UPSMON_MONITORS, ids=lambda m: m["name"])
def test_upsmon_conf_remote_monitor_line(host: Host, nut_config_dir: str, monitor: dict[str, str]) -> None:
    """Each nut_upsmon_monitors entry renders its own MONITOR line.

    Checks the rendered system (name@host[:port]), user, and password.
    """
    content: str = host.file(f"{nut_config_dir}/upsmon.conf").content_string
    system = f"{monitor['name']}@{monitor['host']}"
    if "port" in monitor:
        system += f":{monitor['port']}"
    assert system in content
    assert monitor["user"] in content
    assert monitor["password"] in content


def test_upsmon_conf_remote_monitor_explicit_role(host: Host, nut_config_dir: str) -> None:
    """Entries with an explicit role use that role, not nut_upsmon_role."""
    content: str = host.file(f"{nut_config_dir}/upsmon.conf").content_string
    for monitor in TEST_UPSMON_MONITORS:
        if "role" not in monitor:
            continue
        line = next(
            (line for line in content.splitlines() if line.startswith(f"MONITOR {monitor['name']}@")),
            None,
        )
        assert line is not None, f"MONITOR line for {monitor['name']} not found"
        assert line.rstrip().endswith(f" {monitor['role']}")


def test_upsmon_conf_remote_monitor_role_default(host: Host, nut_config_dir: str) -> None:
    """An entry without an explicit role falls back to nut_upsmon_role.

    Here that is derived from nut_users[0].role == primary.
    """
    content: str = host.file(f"{nut_config_dir}/upsmon.conf").content_string
    line = next(
        (line for line in content.splitlines() if line.startswith("MONITOR remoteups3@")),
        None,
    )
    assert line is not None, "MONITOR line for remoteups3 not found"
    assert line.rstrip().endswith(" primary")
