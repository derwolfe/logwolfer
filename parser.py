"""
The parser module contains all of the functions needed
to load new records into the database and to analyze them.
"""
from __future__ import absolute_import, print_function
import json

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    MetaData,
    Table,
    UniqueConstraint,
    create_engine
)

from datetime import datetime


metadata = MetaData()

Messages = Table(
    "messages", metadata,
    Column("system_id", Text, primary_key=True, autoincrement=False),
    Column("from_id", Text, nullable=False),
    Column("site_id", Integer, nullable=False),
    Column("timestamp", DateTime, nullable=False),
    UniqueConstraint('system_id', 'timestamp', name='u_system_id_timestamp')
)

Statuses = Table(
    "statuses", metadata,
    Column("system_id", Text, primary_key=True, autoincrement=False),
    Column("from_id", Text, nullable=False),
    Column("site_id", Integer, nullable=False),
    Column("status", Boolean, nullable=False),
    Column("timestamp", DateTime, nullable=False),
    UniqueConstraint('system_id', 'timestamp', name='u_system_id_timestamp')
)

Email_or_chats = Table(
    "email_or_chats", metadata,
    Column("system_id", Integer, ForeignKey("messages.system_id"), primary_key=True),
    Column("email", Boolean, nullable=False),
    Column("chat", Boolean, nullable=False)
)


def engine_factory(connection_string):
    return create_engine(connection_string , echo=False)

def build_db(metadata, engine):
    metadata.bind = engine
    metadata.create_all()


def is_online(status):
    return status == u"online"

def parse_message(msg_id, from_id, site_id, timestamp):
    return dict(
        system_id=msg_id,
        from_id=from_id,
        site_id=int(site_id),
        timestamp=datetime.fromtimestamp(
            timestamp
        )
    )

def parse_status(status_id, from_id, site_id, status, timestamp):
    return dict(
        system_id=status_id,
        from_id=from_id,
        site_id=int(site_id),
        status=is_online(
            status
        ),
        timestamp= datetime.fromtimestamp(
            timestamp
        )
    )


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
        return 'message', parse_message(
            msg_id=msg["id"],
            from_id=msg["from"],
            site_id=msg["site_id"],
            timestamp=msg["timestamp"]
        )
    else:
        return 'status', parse_status(
            status_id=msg["id"],
            from_id=msg["from"],
            site_id=msg["site_id"],
            status=msg["data"]["status"],
            timestamp=msg["timestamp"]
        )

def insert_statuses(statuses, engine):
    """
    Insert status messages into the database. Will not insert duplicates.

    @param statuses - a list of status messages
    @type statuses - list of dictionaries

    @returns - None
    """
    insert_stmt = Statuses.insert(
        prefixes=['OR IGNORE']
    )
    engine.execute(
        insert_stmt,
        statuses
    )


def insert_messages(messages, engine):
    """
    Insert chat messages into the database.

    @param messages: a list of chat messages
    @type messages: list of L{parser.Messages} objects.

    @returns - None
    """
    insert_stmt = Messages.insert(
        prefixes=["OR IGNORE"]
    )
    engine.execute(
        insert_stmt,
        messages
    )


def read_file(fname, engine):
    statuses = []
    messages = []
    insert_when = 500
    with open(fname, "rb") as f:
        for line in f:
            line_type, parsed = parse_line(line)

            if line_type == "status":
                statuses.append(parsed)
            elif line_type == "message":
                messages.append(parsed)

            # db calls
            if len(statuses) == insert_when:
                insert_statuses(statuses, engine)
                statuses = []
            elif len(messages) == insert_when:
                insert_messages(messages, engine)
                messages = []

        # insert the remaining records
        insert_statuses(statuses)
        insert_messages(messages)


# query the database with select ... group by...msg

if __name__ == "__main__":
    import sys
    engine = engine_factory("sqlite:///chat-logs.db")
    build_db(metadata, engine)
    read_file(sys.argv[:1])
