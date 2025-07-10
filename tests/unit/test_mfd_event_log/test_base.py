# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Tests for `mfd_event_log` package."""

from textwrap import dedent

import pytest
from mfd_common_libs import log_levels
from mfd_connect import RPyCConnection
from mfd_connect.base import ConnectionCompletedProcess
from mfd_typing import OSName

from mfd_event_log.base import EventLog, EventType
from mfd_event_log.exceptions import EventLogExecutionError


class TestMfdEventLog:
    @pytest.fixture()
    def eventlog(self, mocker):
        conn = mocker.create_autospec(RPyCConnection)
        conn.get_os_name.return_value = OSName.WINDOWS
        eventlog_obj = EventLog(connection=conn)
        mocker.stopall()
        return eventlog_obj

    def test_clear_event_log(self, eventlog):
        eventlog._connection.execute_powershell.return_value = ConnectionCompletedProcess(
            return_code=0, args="command", stdout="", stderr=""
        )
        eventlog.clear_event_log()
        cmd = "Get-EventLog -LogName * | ForEach { Clear-EventLog $_.Log }"
        eventlog._connection.execute_powershell.assert_called_with(cmd, custom_exception=EventLogExecutionError)

    def test_get_event_log(self, eventlog):
        output = dedent(
            """Index              : 110002
            EntryType          : Information
            InstanceId         : 1073748860
            Message            : The Windows Modules Installer service entered the stopped state.
            Category           : (0)
            CategoryNumber     : 0
            ReplacementStrings : {Windows Modules Installer, stopped}
            Source             : Service Control Manager
            TimeGenerated      : 10/3/2023 4:20:47 PM
            TimeWritten        : 10/3/2023 4:20:47 PM
            UserName           :
            """
        )
        expected = [
            {
                "Index": "110002",
                "EntryType": "Information",
                "InstanceId": "1073748860",
                "Message": "The Windows Modules Installer service entered the stopped state.",
                "Category": "(0)",
                "CategoryNumber": "0",
                "ReplacementStrings": "{Windows Modules Installer, stopped}",
                "Source": "Service Control Manager",
                "TimeGenerated": "10/3/2023 4:20:47 PM",
                "TimeWritten": "10/3/2023 4:20:47 PM",
                "UserName": "",
            }
        ]
        eventlog._connection.execute_powershell.return_value = ConnectionCompletedProcess(
            return_code=0, args="command", stdout=output, stderr=""
        )
        assert expected == eventlog.get_event_log()

    def test_get_event_log_with_source(self, eventlog):
        output = dedent(
            """Index              : 110052
            EntryType          : Information
            InstanceId         : 104
            Message            : The Windows PowerShell log file was cleared.
            Category           : (104)
            CategoryNumber     : 104
            ReplacementStrings : {Administrator, B17-27878, Windows PowerShell, }
            Source             : Microsoft-Windows-Eventlog
            TimeGenerated      : 10/3/2023 4:47:12 PM
            TimeWritten        : 10/3/2023 4:47:12 PM
            UserName           : B17-27878\\Administrator

            Index              : 110051
            EntryType          : Information
            InstanceId         : 104
            Message            : The System log file was cleared.
            Category           : (104)
            CategoryNumber     : 104
            ReplacementStrings : {Administrator, B17-27878, System, }
            Source             : Microsoft-Windows-Eventlog
            TimeGenerated      : 10/3/2023 4:47:12 PM
            TimeWritten        : 10/3/2023 4:47:12 PM
            UserName           : B17-27878\\Administrator
            """
        )
        expected = [
            {
                "Index": "110052",
                "EntryType": "Information",
                "InstanceId": "104",
                "Message": "The Windows PowerShell log file was cleared.",
                "Category": "(104)",
                "CategoryNumber": "104",
                "ReplacementStrings": "{Administrator, B17-27878, Windows PowerShell, }",
                "Source": "Microsoft-Windows-Eventlog",
                "TimeGenerated": "10/3/2023 4:47:12 PM",
                "TimeWritten": "10/3/2023 4:47:12 PM",
                "UserName": "B17-27878\\Administrator",
            },
            {
                "Index": "110051",
                "EntryType": "Information",
                "InstanceId": "104",
                "Message": "The System log file was cleared.",
                "Category": "(104)",
                "CategoryNumber": "104",
                "ReplacementStrings": "{Administrator, B17-27878, System, }",
                "Source": "Microsoft-Windows-Eventlog",
                "TimeGenerated": "10/3/2023 4:47:12 PM",
                "TimeWritten": "10/3/2023 4:47:12 PM",
                "UserName": "B17-27878\\Administrator",
            },
        ]
        eventlog._connection.execute_powershell.return_value = ConnectionCompletedProcess(
            return_code=0, args="command", stdout=output, stderr=""
        )
        assert expected == eventlog.get_event_log(
            source="Microsoft-Windows-Eventlog", event_type=EventType.INFORMATION, event_id="104"
        )

    def test_get_and_verify_event_log(self, eventlog):
        output = dedent(
            """Index              : 110052
            EntryType          : Information
            InstanceId         : 104
            Message            : The Windows PowerShell log file was cleared.
            Category           : (104)
            CategoryNumber     : 104
            ReplacementStrings : {Administrator, B17-27878, Windows PowerShell, }
            Source             : Microsoft-Windows-Eventlog
            TimeGenerated      : 10/3/2023 4:47:12 PM
            TimeWritten        : 10/3/2023 4:47:12 PM
            UserName           : B17-27878\\Administrator

            Index              : 110051
            EntryType          : Information
            InstanceId         : 104
            Message            : The System log file was cleared.
            Category           : (104)
            CategoryNumber     : 104
            ReplacementStrings : {Administrator, B17-27878, System, }
            Source             : Microsoft-Windows-Eventlog
            TimeGenerated      : 10/3/2023 4:47:12 PM
            TimeWritten        : 10/3/2023 4:47:12 PM
            UserName           : B17-27878\\Administrator

            Index              : 110051
            EntryType          : Error
            InstanceId         : 10401
            Message            : The System log file was cleared.
            Category           : (104)
            CategoryNumber     : 104
            ReplacementStrings : {Administrator, B17-27878, System, }
            Source             : Microsoft-Windows-Eventlog
            TimeGenerated      : 10/3/2023 4:47:12 PM
            TimeWritten        : 10/3/2023 4:47:12 PM
            UserName           : B17-27878\\Administrator
            """
        )
        eventlog._connection.execute_powershell.return_value = ConnectionCompletedProcess(
            return_code=0, args="command", stdout=output, stderr=""
        )
        assert eventlog.get_and_verify_event_log(failure_entry_types=["Information"], ignored_event_ids=["104"])
        assert not eventlog.get_and_verify_event_log(failure_entry_types=["Information"])
        assert eventlog.get_and_verify_event_log(ignored_event_ids=["10401"])
        assert not eventlog.get_and_verify_event_log()

    @pytest.fixture()
    def mock_get_event_log(self, eventlog, mocker):
        return mocker.patch.object(eventlog, "get_event_log")

    def test_verify_log_no_errors(self, mock_get_event_log, caplog, eventlog):
        caplog.set_level(log_levels.MODULE_DEBUG)
        # Arrange
        mock_get_event_log.return_value = None
        driver = "test_driver"

        # Act
        result = eventlog.verify_log(driver)

        # Assert
        mock_get_event_log.assert_called_once_with(source=driver, event_type=EventType.ERROR)
        assert f"Driver service name: {driver}" in caplog.messages
        assert result == ""

    def test_verify_log_with_errors(self, mock_get_event_log, caplog, eventlog):
        # Arrange
        caplog.set_level(log_levels.MODULE_DEBUG)
        mock_get_event_log.return_value = [{"Message": "Error message"}]
        driver = "test_driver"

        # Act
        result = eventlog.verify_log(driver)

        # Assert
        mock_get_event_log.assert_called_once_with(source=driver, event_type=EventType.ERROR)
        assert f"Driver service name: {driver}" in caplog.messages
        assert result == "Error message\n"
