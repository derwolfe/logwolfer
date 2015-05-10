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
connection_string = "sqlite:///chat_logs.db"
engine = create_engine(connection_string , echo=True)
metadata = MetaData()

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

def engine_factory(connection_string):
    return create_engine(connection_string , echo=True)

def build_db(metadata, engine):
    metadata.bind = engine
    metadata.create_all()

def parse_message(msg_id, recv_from, site_id,
                  msg_type, status, timestamp):
    return dict(
        id=msg_id,
        from_id=recv_from,
        site_id=site_id,
        type=msg_type,
        status=status,
        timestamp=datetime.fromtimestamp(
            timestamp
        )
    )

def is_online(status):
    if status == u"online":
        return True
    else:
        return False

def parse_status(status_id, recv_from, site_id,
                 msg_type, status, timestamp):
    return dict(
        id=status_id,
        from_id=recv_from,
        site_id=site_id,
        type=msg_type,
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
        print( msg)
        return 'message', parse_message(
            msg_id=msg["id"],
            recv_from=msg["from"],
            site_id=msg["site_id"],
            msg_type=msg["type"],
            status=msg["data"]["message"],
            timestamp=msg["timestamp"]
        )
    else:
        return 'status', parse_status(
            status_id=msg["id"],
            recv_from=msg["from"],
            site_id=msg["site_id"],
            msg_type=msg["type"],
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
        prefixes=['OR IGNORE']
    )
    engine.execute(
        insert_stmt,
        messages
    )


def read_file(fname, engine):
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
                insert_statuses(statuses, engine)
                statuses = []
            elif len(messages) == insert_when:
                insert_messages(messages, engine)
                messages = []

        # insert the remaining records
        insert_statuses(statuses)
        insert_messages(messages)


# query the database with select ... group by...msg

if __name__ == '__main__':
    import sys
    engine = engine_factory('sqlite:///chat-logs.db')
    build_db(metadata, engine)
    read_file(sys.argv[:1])
