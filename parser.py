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

from datetime import datetime

# the tables
connectionString = "sqlite:///"
engine = create_engine(connectionString + "chat_logs.db", echo=True)
metadata = MetaData(bind=engine)

# make sure duplicates are ignored!
Messages = Table(
    "messages", metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("from_id", String, nullable=False),
    Column("site_id", Integer, nullable=False),
    Column("type", String, nullable=False),
    Column("status", String, nullable=False),
    Column("timestamp", DateTime, nullable=False),
)

# make sure duplicates are ignored!
Statuses = Table(
    "statuses", metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("from_id", String, nullable=False),
    Column("site_id", Integer, nullable=False),
    Column("type", String, nullable=False),
    Column("online", Boolean, nullable=False),
    Column("timestamp", DateTime, nullable=False),
)

Email_or_chats = Table(
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
        self.timestamp = datetime.fromtimestamp(timestamp)


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
        self.timestamp = datetime.fromtimestamp(timestamp)

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

def insert_statuses(statuses):
    """
    Insert status messages into the database. Will not insert duplicates.

    @param statuses - a list of status messages
    @type statuses - list of L{parser.Status} objects.

    @returns - None
    """
    to_db = []
    for s in statuses:
        parsed = dict(
            id=s.status_id,
            from_id=s.recv_from,
            site_id=s.site_id,
            type=s.msg_type,
            status=s.status,
            timestamp=s.timestamp
        )
        insert_stmt = Statuses.insert(
            prefixes=['OR IGNORE']
        ).values(parsed)
        engine.execute(insert_stmt)


def insert_messages(messages):
    """
    Insert chat messages into the database.

    @param messages - a list of chat messages
    @type messages - list of L{parser.Messages} objects.

    @returns - None
    """
    to_db = []
    for m in messages:
        parsed = dict(
            id=m.msg_id,
            from_id=m.recv_from,
            site_id=m.site_id,
            type=m.msg_type,
            status=m.status,
            timestamp=m.timestamp
        )
        to_db.append(parsed)
        insert_stmt = Messages.insert(
            prefixes=['OR IGNORE']
        ).values(parsed)
        engine.execute(insert_stmt)


def read_file(fname):
    statuses = []
    messages = []
    insert_when = 500
    with open(fname, 'rb') as f:
        for line in f:
            line_type, parsed = parse_line(line)

            if line_type == 'status':
                statuses.append(parsed)
            elif line_type == 'message':
                messages.append(parsed)

            # db calls
            if len(statuses) == insert_when:
                insert_statuses(statuses)
                statuses = []
            elif len(messages) == insert_when:
                insert_messages(messages)
                messages = []

        # insert the remaining records
        insert_statuses(statuses)
        insert_messages(messages)


# query the database with select ... group by...msg
