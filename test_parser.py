"""
Tests for the parser module.
"""

from __future__ import absolute_import, print_function
from unittest import TestCase, main as testmain

from datetime import datetime
import json

import parser


class TestParseStatus(TestCase):

    def setUp(self):
        self.msg = {
            "id":"53367bc7-e2cf-11e4-81da-56847afe9799",
            "from":"operator1",
            "site_id":"123",
            "type":"status",
            "data":{
                "status":"online",
            },
            "timestamp":1429026448
        }

        self.msg_type, self.parsed = parser.parse_line(
            json.dumps(self.msg)
        )

    def test_parsesMsgId(self):
        self.assertEqual("status", self.msg_type)

    def test_parsesMsgId(self):
        self.assertEqual(
            self.msg["id"],
            self.parsed["system_id"]
        )

    def test_parsesRecvFrom(self):
        self.assertEqual(
            self.msg["from"],
            self.parsed["from_id"]
        )

    def test_parsesSiteId(self):
        self.assertEqual(
            int(self.msg["site_id"]),
            self.parsed["site_id"]
        )

    def test_parsesStatus(self):
        self.assertTrue(self.parsed["status"])

    def test_parsesTimestamp(self):
        self.assertEqual(
            datetime.fromtimestamp(self.msg["timestamp"]),
            self.parsed["timestamp"]
        )

    def test_is_online(self):
        self.assertTrue(parser.is_online("online"))
        self.assertFalse(parser.is_online("offline"))


class TestParseMessage(TestCase):

    def setUp(self):
        self.msg = {
            "id":"45094d07-e2cf-11e4-9454-56847afe9799",
            "from":"visitor5",
            "type":"message",
            "site_id":"123",
            "data":{
                "message":"Hi, how's it going",
            },
            "timestamp":1429026445,
        }
        self.msg_type, self.parsed = parser.parse_line(json.dumps(self.msg))

    def test_parsesMsgType(self):
        self.assertEqual("message", self.msg_type)

    def test_parsesMsgId(self):
        self.assertEqual(
            self.msg["id"], self.parsed["system_id"]
        )

    def test_parsesRecvFrom(self):
        self.assertEqual(
            self.msg["from"], self.parsed["from_id"]
        )

    def test_parsesSiteId(self):
        self.assertEqual(
            int(self.msg["site_id"]), self.parsed["site_id"]
        )

    def test_parsesTimestamp(self):
        self.assertEqual(
            datetime.fromtimestamp(self.msg["timestamp"]),
            self.parsed["timestamp"]
        )


class TestInsertMessages(TestCase):

    def setUp(self):
        self.engine = parser.engine_factory("sqlite://")
        parser.build_db(parser.metadata, self.engine)

        self.msg = parser.parse_message(
            msg_id=1,
            from_id=1,
            site_id=1,
            timestamp=1429026448
        )

    def test_doesNotInsertDuplicates(self):
        parser.insert_messages([self.msg, self.msg, self.msg], self.engine)
        result = self.engine.execute("select count(*) as ct from messages;")
        self.assertEqual(1, result.scalar())


class TestInsertStatuses(TestCase):

    def setUp(self):
        self.engine = parser.engine_factory("sqlite://")
        parser.build_db(parser.metadata, self.engine)

        self.status = parser.parse_status(
            status_id=1,
            from_id=1,
            site_id=1,
            status=False,
            timestamp=1429026448
        )

    def test_doesNotInsertDuplicates(self):
        parser.insert_statuses([self.status, self.status, self.status], self.engine)
        result = self.engine.execute("select count(*) as ct from statuses;")
        self.assertEqual(1, result.scalar())


if __name__ == "__main__":
    testmain()
