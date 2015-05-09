"""
Tests for the parser module.
"""

from __future__ import absolute_import
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

        self.msg_type, self.parsed = parser.parse_line(json.dumps(self.msg))

    def test_parsesMsgId(self):
        self.assertEqual('status', self.msg_type)

    def test_parsesMsgId(self):
        self.assertEqual(self.msg["id"], self.parsed.status_id)

    def test_parsesRecvFrom(self):
        self.assertEqual(self.msg["from"], self.parsed.recv_from)

    def test_parsesSiteId(self):
        self.assertEqual(self.msg["site_id"], self.parsed.site_id)

    def test_parsesType(self):
        self.assertEqual(self.msg["type"], self.parsed.msg_type)

    def test_parsesStatus(self):
        self.assertTrue(self.parsed.online)

    def test_parsesTimestamp(self):
        self.assertEqual(
            datetime.fromtimestamp(self.msg["timestamp"]),
            self.parsed.timestamp
        )

    def test_is_online(self):
        self.assertTrue(parser.Status.is_online("online"))
        self.assertFalse(parser.Status.is_online("offline"))


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

    def test_parsesMsgId(self):
        self.assertEqual('message', self.msg_type)

    def test_parsesMsgId(self):
        self.assertEqual(self.msg["id"], self.parsed.msg_id)

    def test_parsesRecvFrom(self):
        self.assertEqual(self.msg["from"], self.parsed.recv_from)

    def test_parsesSiteId(self):
        self.assertEqual(self.msg["site_id"], self.parsed.site_id)

    def test_parsesType(self):
        self.assertEqual(self.msg["type"], self.parsed.msg_type)

    def test_parsesMessage(self):
        self.assertEqual(self.msg["data"]["message"], self.parsed.status)

    def test_parsesTimestamp(self):
        self.assertEqual(
            datetime.fromtimestamp(self.msg["timestamp"]),
            self.parsed.timestamp
        )

class TestInsertMessages(TestCase):

    def setUp(self):
        self.msg = parser.Message(
            msg_id=1,
            recv_from=1,
            site_id=1,
            msg_type='message',
            status="stuff",
            timestamp=1429026448
        )

    def test_doesNotInsertDuplicates(self):
        parser.insert_messages([self.msg, self.msg])
        conn = parser.engine.raw_connection()
        cursor = conn.cursor("select count(*) from messages;")
        results = cursor.fetchall()
        print results


if __name__ == '__main__':
    testmain()
