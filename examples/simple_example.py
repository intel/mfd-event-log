# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

# Put here only the dependencies required to run the module.
# Development and test requirements should go to the corresponding files.
"""Simple example of usage."""
import logging

from mfd_connect import RPyCConnection
from mfd_event_log import EventLog, EventType

conn = RPyCConnection(ip="x.x.x.x")
eventlog_obj = EventLog(connection=conn)
entries = eventlog_obj.get_event_log()
eventlog_obj.get_event_log(source="Microsoft-Windows-Eventlog", event_type=EventType.INFORMATION, event_id="104")

result0 = eventlog_obj.verify_event_log(entries, ignored_event_ids=["236"])
result1 = eventlog_obj.get_and_verify_event_log()
result2 = eventlog_obj.get_and_verify_event_log(failure_entry_types=[EventType.INFORMATION])
result3 = eventlog_obj.get_and_verify_event_log(ignored_event_ids=["236"])

eventlog_obj.clear_event_log()

errors = eventlog_obj.verify_log("i40e")
logging.debug(errors)
