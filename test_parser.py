"""
Tests for the parser module.
"""

from __future__ import absolute_import
from unittest import TestCase, main as testmain

import json

import parser

class TestParser(TestCase):

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
        self.assertEqual(self.msg["data"]["status"], self.result.status)

    def test_parsesTimestamp(self):
        self.assertEqual(self.msg["timestamp"], self.result.timestamp)


if __name__ == '__main__':
    testmain()
