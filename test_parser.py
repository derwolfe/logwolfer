"""
Tests for the parser module.
"""

from __future__ import absolute_import
from unittest import TestCase, main as testmain

import json

import parser

class TestParser(TestCase):

    def test_loadsJson(self):
        msg = json.dumps({
            "id":"53367bc7-e2cf-11e4-81da-56847afe9799",
            "from":"operator1",
            "site_id":"123",
            "type":"status",
            "data":{
                "status":"online",
            },
            "timestamp":1429026448,
        })
        result = parser.parse_line(msg)
        self.assertIn("id", result.keys())


if __name__ == '__main__':
    testmain()
