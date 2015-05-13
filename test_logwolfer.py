"""
Tests for the logwolfer module.
"""

from __future__ import absolute_import, print_function
from unittest import TestCase, main as testmain

import sys
from cStringIO import StringIO
from contextlib import contextmanager

from datetime import datetime
import json

import logwolfer


@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


class TestParseStatus(TestCase):

    def setUp(self):
        self.msg = {
            "id": "53367bc7-e2cf-11e4-81da-56847afe9799",
            "from": "operator1",
            "site_id": "123",
            "type": "status",
            "data": {
                "status": "online",
            },
            "timestamp": 1429026448
        }

        self.msg_type, self.parsed = logwolfer.parse_line(
            json.dumps(self.msg)
        )

    def test_parsesMsgType(self):
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
        self.assertTrue(logwolfer.is_online("online"))
        self.assertFalse(logwolfer.is_online("offline"))


class TestParseMessage(TestCase):

    def setUp(self):
        self.msg = {
            "id": "45094d07-e2cf-11e4-9454-56847afe9799",
            "from": "visitor5",
            "type": "message",
            "site_id": "123",
            "data": {
                "message": "Hi, how's it going",
            },
            "timestamp": 1429026445,
        }
        self.msg_type, self.parsed = logwolfer.parse_line(json.dumps(self.msg))

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


class IntegrationTests(TestCase):

    def setUp(self):
        self.engine = logwolfer.engine_factory("sqlite://")

    def tearDown(self):
        # close the connection

    def test_doesNotInsertDuplicates(self):
        engine = logwolfer.engine_factory("sqlite://")
        logwolfer.build_db(logwolfer.metadata, engine)

        self.msg = logwolfer.parse_message(
            msg_id=1,
            from_id=1,
            site_id=1,
            timestamp=1429026448
        )

        logwolfer.insert_messages([self.msg, self.msg], engine)
        result = self.engine.execute("select count(*) as ct from messages;")
        self.assertEqual(1, result.scalar())


    def test_doesNotInsertDuplicates(self):
        logwolfer.build_db(logwolfer.metadata, engine)

        self.status = logwolfer.parse_status(
            status_id=1,
            from_id=1,
            site_id=1,
            status=False,
            timestamp=1429026448
        )
        logwolfer.insert_statuses([self.status, self.status], self.engine)
        result = self.engine.execute("select count(*) as ct from statuses;")
        self.assertEqual(1, result.scalar())


    def test_runWithSmallInput(self):
        with capture(logwolfer.run_all,
                     "./data/small_input",
                     "txt",
                     logwolfer.metadata,
                     self.engine) as output:
            self.assertEquals(
                "1,messages=4,emails=4,operators=2,visitors=5",
                output.strip()
            )

    def test_runWithBadInput(self):
        with capture(logwolfer.run_all,
                     "./data/bad_input",
                     "txt",
                     logwolfer.metadata,
                     self.engine) as output:
            self.assertEquals(
                "1,messages=3,emails=4,operators=2,visitors=4",
                output.strip()
            )


if __name__ == "__main__":
    testmain()
