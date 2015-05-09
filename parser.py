"""
The parser module contains all of the functions needed
to load new records into the database and to analyze them.
"""

import json

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    Boolean,
    ForeignKey,
    MetaData,
    Table,
    create_engine
)

# the tables
connectionString = "sqlite:///"
engine = create_engine(connectionString + "chat_logs.db", echo=True)
metadata = MetaData(bind=engine)
messages = Table(
    "messages", metadata,
    Column("id", Integer, primary_key=True),
    Column("from_id", String, nullable=False),
    Column("site_id", Integer, nullable=False),
    Column("type", String, nullable=False),
    Column("status", String, nullable=False),
    Column("timestamp", DateTime, nullable=False)
)

statuses = Table(
    "statuses", metadata,
    Column("id", Integer, primary_key=True),
    Column("from_id", String, nullable=False),
    Column("site_id", Integer, nullable=False),
    Column("type", String, nullable=False),
    Column("online", Boolean, nullable=False),
    Column("timestamp", DateTime, nullable=False)

)

email_or_chats = Table(
    "email_or_chats", metadata,
    Column("id", Integer, ForeignKey("messages.id"), primary_key=True),
    Column("email", Boolean, nullable=False),
    Column("chat", Boolean, nullable=False)
)

metadata.create_all()


class Message(object):
    """
    A chat message intended for a site.
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


class Status(object):
    """
    A status message that states whether or not a given site is online.
    """
    def __init__(self,
                 status_id,
                 recv_from,
                 site_id,
                 msg_type,
                 status,
                 timestamp):
        self.status_id = status_id
        self.recv_from = recv_from
        self.site_id = site_id
        self.msg_type = msg_type
        self.online = Status.is_online(status)
        self.timestamp = timestamp

    @staticmethod
    def is_online(status):
        if status == u"online":
            return True
        else:
            return False


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

    @returns a new L{parser.Message} or L{parser.Status} object.
    """
    msg = json.loads(line)
    if msg["type"] == u"message":
        return 'message', Message(
            msg_id=msg["id"],
            recv_from=msg["from"],
            site_id=msg["site_id"],
            msg_type=msg["type"],
            status=msg["data"]["message"],
            timestamp=msg["timestamp"]
        )
    else:
        return 'status', Status(
            status_id=msg["id"],
            recv_from=msg["from"],
            site_id=msg["site_id"],
            msg_type=msg["type"],
            status=msg["data"]["status"],
            timestamp=msg["timestamp"]
        )

# the tables
connectionString = "sqlite:///"
engine = create_engine(connectionString + "chat_logs.db", echo=True)
metadata = MetaData(bind=engine)
messages = Table(
    "messages", metadata,
    Column("id", Integer, primary_key=True),
    Column("from", String, nullable=False),
    Column("site_id", Integer, nullable=False),
    Column("type", String, nullable=False),
    Column("status", String, nullable=False),
    Column("timestamp", DateTime, nullable=False)
)

statuses = Table(
    "statuses", metadata,
    Column("id", Integer, primary_key=True),
    Column("from", String, nullable=False),
    Column("site_id", Integer, nullable=False),
    Column("type", String, nullable=False),
    Column("online", Boolean, nullable=False),
    Column("timestamp", DateTime, nullable=False)

)
email_or_chats = Table(
    "email_or_chat", metadata,
    Column("id", Integer, ForeignKey("messages.id"), primary_key=True),
    Column("email", Boolean, nullable=False),
    Column("chat", Boolean, nullable=False)
)
metadata.create_all()


# if it is by query, you will need to order the results by their timestamps
# to know which window they used (i.e. email or chat).
# soln: make a message table, a status table, and a email/chat table
# when you are finished reading the messages and status, begin to add
# records to the email_chat table, basically jsaying "message 12312 is chat"
# then run join/sum on that table to get the results.

# create a database

# read the lines from the log into the database
#    only insert if PK doesn't already exist.
# Every unique message will also have a unique timestamp.
# you can do an insert and then ignore duplicates


# query the database with select ... group by...msg
