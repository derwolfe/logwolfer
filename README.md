Initial design
--------------

Steps:

* -Create functions that can parse messages-
* use json.loads/dumps on each line
* Create a reader that can read a line at a time.
* Use the message id & timestamp as a primary key
* write some sql to analyze
* sqlalchemy to create the db or just raw sqlite connection
* the message id is unique

How to run
----------
``python parser.py log``


How to test
-----------

``python test_parser.py``
