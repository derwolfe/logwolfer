"""
The parser module contains all of the functions needed
to load new records into the database and to analyze them.
"""

import json


def parse_line(line):
    return json.loads(line)
