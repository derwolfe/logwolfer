"""
The logwolfer module contains all of the functions needed to load new records
into the database and to analyze them.
"""

from __future__ import absolute_import, print_function
import json

from sqlalchemy import (
    Column,
    Integer,
    Index,
    DateTime,
    Text,
    Boolean,
    MetaData,
    Table,
    UniqueConstraint,
    create_engine,
)

from datetime import datetime

import logging
import gzip

import click


logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

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

Sites = Table(
    "sites", metadata,
    Column("site_id", Integer, primary_key=True, autoincrement=False)
)

Chats = Table(
    "chats", metadata,
    Column("message_id", Text, primary_key=True, autoincrement=False),
    Column("site_id", Integer, nullable=False),
    Column("chat", Boolean, nullable=False)
)

def engine_factory(connection_string):
    """
    Given a connection string, create a new sqlalchemy db engine object.

    @param connection_string: a connection string for sqlalchemy
    @type conneciton_string: a string, unicode or bytes.

    @return: a new L{sqlalchemy.engine.Engine}
    """
    return create_engine(connection_string, echo=False)


def build_db(metadata, engine):
    """
    Build a database using the given metadata and sqlengine.

    @param metadata: table metadata that sqlalchemy understands.
    @type metadata: a L{sqlalchemy.schema.MetaData} object.

    @param engine: a db engine sql alchemy understands
    @type engine: a L{sqlalchemy.engine.Engine}
    """
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
        timestamp=datetime.fromtimestamp(
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

    @returns a new C{dictionary} containing data representing a message or a
        status message.
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
    """
    log.info("writing statuses")
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
    """
    log.info("writing messages")
    insert_stmt = Messages.insert(
        prefixes=["OR IGNORE"]
    )
    engine.execute(
        insert_stmt,
        messages
    )


def read_file(fname, filetype, engine):
    """
    Given a filename, filetype, and sqlalchemy db engine, find the appropriate
    reader to use, and start reading the file.

    @param fname: the filename
    @type fname: unicode string

    @param ftpe: the filetype, e.g. "gzip" or "txt"
    @type fype: unicode string

    @param engine: a db engine capable of executing sql queries.
    @type engine: a sqlalchemy db engine
    """
    log.info("starting to read file")
    if filetype == u"gzip":
        with gzip.open(fname, 'r') as f:
            parse_logs(engine, f)
    else:
        with open(fname, 'r') as f:
            parse_logs(engine, f)


def parse_logs(engine, logs):
    """
    Insert all of the new messages into the system.

    @param logs: an iterable that contains C{dictionares} of either
        messages or statuses.
    """
    statuses = []
    messages = []
    insert_when = 5000
    for line in logs:
        try:
            line_type, parsed = parse_line(line)

            if line_type == "status":
                statuses.append(parsed)
            elif line_type == "message":
                messages.append(parsed)
        except KeyError:
            log.warning("error parsing message: %s", line)

        # db calls
        if len(statuses) == insert_when:
            insert_statuses(statuses, engine)
            statuses = []
        elif len(messages) == insert_when:
            insert_messages(messages, engine)
            messages = []

    # insert the remaining records
    insert_statuses(statuses, engine)
    insert_messages(messages, engine)
    log.info("final writes")


def build_sites(engine):
    """
    With the logs loaded, build a table containing all of the site_ids.
    """
    sql = """
INSERT OR IGNORE INTO sites (site_id)
SELECT site_id
FROM (
    SELECT distinct site_id FROM messages
    UNION ALL
    SELECT distinct site_id FROM statuses
)
GROUP BY site_id
"""
    log.info("building sites table")
    engine.execute(sql)
    log.info("finished populating sites table")


def build_indices(engine):
    """
    Build indexes on the data in the database and populate the sites
    table.

    This is meant to be run __after__ the data has been inserted into the db.

    @param engine: a sqlalchemy engine capable of talking to the database that
        already has been loaded with data.
    @type engine: a L{sqlalchemy.engine} object

    @returns: nothing
    """
    log.info("adding indices")

    d1 = "DROP INDEX IF EXISTS message_site_id_idx;"
    d2 = "DROP INDEX IF EXISTS status_site_id_idx;"
    d3 = "DROP INDEX IF EXISTS status_site_timestamp_idx;"
    engine.execute(d1)
    engine.execute(d2)
    engine.execute(d3)

    msg_index = Index("message_site_id_idx", Messages.c.site_id)
    status_index = Index("status_site_id_idx", Statuses.c.site_id)
    status_time_index = Index("status_site_timestamp_idx",
                              Statuses.c.timestamp.desc(), Statuses.c.site_id)

    msg_index.create(engine)
    status_index.create(engine)
    status_time_index.create(engine)
    log.info("finished adding indices")


def classify_messages(engine):
    """
    Insert new chats into the L{parser.Chats} table. If a chat with a given
    message ID has already been added, it will be treated as a duplicate and
    skipped.

    @param engine: a sqlalchemy engine that can perform queries.
    @type engine: L{sqlalchemy.engine.Engine}
    """
    log.info("tagging messages as chats or emails")

    chats_insert_stmt = """
INSERT OR IGNORE INTO chats(message_id, site_id, chat)
SELECT
  m.system_id
  , m.site_id
  , CASE WHEN
    ( SELECT s.timestamp
      FROM Statuses s
      WHERE s.timestamp <= m.timestamp
        and s.status == 1  -- online
        and s.site_id = m.site_id
     ORDER BY s.timestamp DESC
     LIMIT 1) is null THEN 0 ELSE 1 END
     as chat
FROM messages m;
"""
    engine.execute(chats_insert_stmt)


def build_results(engine):
    """
    Build a summary of activity for each site in the logs. If no prior online
    status is found for a given site, that site can be assumed to be offline.

    Sum the total messages, emails, unique operators, and unique visitors to
    the site.

    Results should be of the format:

    123,messages=1,emails=0,operators=1,visitors=2
    124,messages=2,emails=1,operators=4,visitors=1
    """

    analyze_stmt = """
SELECT
  s.site_id AS site_id
  , (SELECT COUNT(*)
       FROM chats ch WHERE ch.site_id = s.site_id and ch.chat = 0)
    as emails
  , (SELECT COUNT(*)
       FROM chats ch WHERE ch.site_id = s.site_id and ch.chat = 1)
    as chats
  , (SELECT COUNT(*) FROM
      (SELECT distinct FROM_id
       FROM statuses st WHERE st.site_id = s.site_id))
    as operators
  , (SELECT COUNT(*) FROM
       (SELECT DISTINCT FROM_id
        FROM messages ms WHERE ms.site_id = s.site_id))
    as visitors
FROM sites s
ORDER BY s.site_id ASC;
"""
    log.info("performing analysis")
    results = engine.execute(analyze_stmt)
    log.info("fetching analysis results")
    for row in results:
        print("%d,messages=%d,emails=%d,operators=%d,visitors=%d"
              %(row["site_id"], row["chats"], row["emails"], row["operators"],
                row["visitors"]))


def run_all(fname, ftype, metadata, engine):
    """
    Build the database, load data into it, and analyze it.

    @param fname: the filename to load data from
    @type fname: a unicode string

    @param ftype: the filetype being loaded, e.g. C{u'txt'} or C{u'gzip'}
    @type ftype: a unicode string

    @param metadata: table metadata
    @type metadata: L{sqlalchemy.schema.Metadata}
    """
    build_db(metadata, engine)
    read_file(fname, ftype, engine)
    build_indices(engine)
    build_sites(engine)
    classify_messages(engine)
    build_results(engine)


def load_only(fname, ftype, metadata, engine):
    """
    Run only the steps needed to load data into the db.

    @param fname: the filename to load data from
    @type fname: a unicode string

    @param ftype: the filetype being loaded, e.g. C{u'txt'} or C{u'gzip'}
    @type ftype: a unicode string

    @param metadata: table metadata
    @type ftype: L{sqlalchemy.schema.Metadata}
    """
    build_db(metadata, engine)
    read_file(fname, ftype, engine)
    build_indices(engine)
    build_sites(engine)
    classify_messages(engine)


@click.command()
@click.option("--onlyanalyze", type=click.BOOL, default=False,
              help=("Only run the analysis step. This requires data to have"
                    "already been loaded into a database name ./logwolfer.db"))
@click.option("--onlyload", type=click.BOOL, default=False,
              help=("Load data into the database without performing analysis"))
@click.option("--fname", help="The absolute or relative name of the logfile")
@click.option("--ftype", default="gzip",
              help="Enter gzip if the file is a gzip, otherwise use txt")
def run(onlyanalyze, onlyload, fname, ftype):
    engine = engine_factory("sqlite:///logwolfer.db")
    if onlyload:
        load_only(fname, ftype, metadata, engine)
    elif onlyanalyze:
        build_results(engine)
    else:
        run_all(fname, ftype, metadata, engine)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    engine = engine_factory("sqlite:///logwolfer.db")
    run()
