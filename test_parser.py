"""
Tests for the parser module.
"""

from __future__ import absolute_import
from unittest import TestCase, main as testmain

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
        self.result = parser.parse_line(json.dumps(self.msg))

    def test_parsesMsgId(self):
        self.assertEqual(self.msg["id"], self.result.msg_id)

    def test_parsesRecvFrom(self):
        self.assertEqual(self.msg["from"], self.result.recv_from)

    def test_parsesSiteId(self):
        self.assertEqual(self.msg["site_id"], self.result.site_id)

    def test_parsesType(self):
        self.assertEqual(self.msg["type"], self.result.msg_type)

    def test_parsesStatus(self):
        self.assertTrue(self.result.online)

    def test_parsesTimestamp(self):
        self.assertEqual(self.msg["timestamp"], self.result.timestamp)

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
        self.result = parser.parse_line(json.dumps(self.msg))

    def test_parsesMsgId(self):
        self.assertEqual(self.msg["id"], self.result.msg_id)

    def test_parsesRecvFrom(self):
        self.assertEqual(self.msg["from"], self.result.recv_from)

    def test_parsesSiteId(self):
        self.assertEqual(self.msg["site_id"], self.result.site_id)

    def test_parsesType(self):
        self.assertEqual(self.msg["type"], self.result.msg_type)

    def test_parsesMessage(self):
        self.assertEqual(self.msg["data"]["message"], self.result.status)

    def test_parsesTimestamp(self):
        self.assertEqual(self.msg["timestamp"], self.result.timestamp)


if __name__ == '__main__':
    testmain()
