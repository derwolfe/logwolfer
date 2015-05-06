Initial design
--------------

# Create a reader
# Create functions that can parse messages
# Use the message id & timestamp as a primary key
# use json.loads/dumps on each line
# use pandas to analyze the data that will be stored in sqlite
# sqlalchemy to create the db or just raw sqlite connection
# the message id is unique

How to run
----------
``python parser.py log``


How to test
-----------

``python test_parser.py``
