"""
The parser module contains all of the functions needed
to load new records into the database and to analyze them.
"""

import json


class Message(object):
    """
    A simplified message containing only the data needed from parsing.
    """
    def __init__(self,
                 msg_id,
                 recv_from,
                 site_id,
                 msg_type,
                 status,
                 timestamp):
        self.msg_id = msg_id
        self.recv_from = recv_from
        self.site_id = site_id
        self.msg_type = msg_type
        self.status = status
        self.timestamp = timestamp


def parse_line(line):
    """
    Parse a line in the chat logs.

    @param line - a json string containing a id, from, site_id, type,
        data[status], and a timestamp field.
    @type line - a string

    @returns a new L{parser.Message} object.
    """
    msg = json.loads(line)
    return Message(
        msg_id=msg["id"],
        recv_from=msg["from"],
        site_id=msg["site_id"],
        msg_type=msg["type"],
        status=msg["data"]["status"],
        timestamp=msg["timestamp"]
    )
