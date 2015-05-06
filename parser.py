"""
The parser module contains all of the functions needed
to load new records into the database and to analyze them.
"""

import json
import sqlite3

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

    An example line looks like:

       {
            "id":"53367bc7-e2cf-11e4-81da-56847afe9799",
            "from":"operator1",
            "site_id":"123",
            "type":"status",
            "data":{
                "status":"online",
            },
            "timestamp":1429026448
        }

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
        # there is a problem with this, the status field can be either a
        # message OR a status message.
        status=msg["data"]["status"],
        timestamp=msg["timestamp"]
    )

def build_database(conn_string):
    connection = conn_string.connect()
    connection.execute("""
    CREATE TABLE messages (
    message_id TEXT primary key not null
    , from TEXT not null
    , site_id BIGINT not null
    , type TEXT not null
    , status BOOLEAN not null
    , timestamp DATETIME not null
""")

# you basically want to know which chats are delivered as emails vs which are
# are sent online. This means the timestamp is much more important than you
# had thought. Effectively you need to know when a site is online, then you can
# know if the user sent it as an email or as a chat.
# is this something you should rely on with data entry, that is learn it ON insert
# or is this something that you should query out.
# if it is by query, you will need to order the results by their timestamps
# to know which window they used (i.e. email or chat).

# create a database
# read the lines from the log into the database
#    only insert if PK doesn't already exist.
# Every unique message will also have a unique timestamp.
# you can do an insert and then ignore duplicates

#CREATE TABLE bookmarks(
#    users_id INTEGER,
#    lessoninfo_id INTEGER,
#    UNIQUE(users_id, lessoninfo_id)
#);
#INSERT OR IGNORE INTO bookmarks(users_id, lessoninfo_id) VALUES(123, 456)

# query the database with select ... group by...msg
