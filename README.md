Logwolfer
=========

Welcome to Logwolfer, a command line application that ingests chat messages and
spits out an analysis of those messages.

Logwolfer is able to be run multilple times, as long as the sqlite database used
isn't deleted. This means that new messages can be added to the database after
the first run.

Three operating modes are available:

1. Load data and run analysis on the data.
2. Load data only. This makes it possible to contine loading more and more information
   into the system, without needing to rebuild it over again. Duplicate messages will
   just be thrown away.
3. Analyze data already in the system. This allows you to run the system with data
   that has already been parsed. Naturally, this requires that you have already loaded
   data into the system.

All of the parsed messages are stored in ./logwolfer.db. This means, you can have
several versions of your logwolfer database floating around, and you can store different
versions of the database to target different times.

But, for most uses of logwolfer, you'll run the application as a single-shot, i.e.
you will load data in analyze it then delete the logwolfer results and start over.
(At least, this is what I would expect you to do).

Steps to install
----------------

These install steps are targeted at Ubuntu 12.04 LTS (precise 32). They were checked
on a vagrant virtual machine.

    sudo apt-get install -y python-software-properties
    sudo add-apt-repository -y ppa:pypy
    sudo apt-get update
    sudo apt-get install -y python-sqlite
    sudo apt-get install -y pypy pypy-dev
    sudo apt-get install -y python-pip
    sudo pip install virtualenv
    virtualenv -p pypy pypyenv
    source ./pypy-env/bin/activate
    pip install -r requirements.txt

Once all of these steps have run, you simply need to CD into the directory containing
Logwolfer's source to run it.

How to run
----------

For all text based filetypes, the following command will load in all of the
data then run analyses on it.

    python parser.py --fname=./data/small_input --ftype=txt

If the file is a gzip file, the following command will work:

    python parser.py --fname=./data/big_input.gz --ftype=gzip

To load data into the application without running any analysis steps run:

    python parser.py --onlyload=True --fname=./data/small_input --ftype=txt

To only run analysis steps on a logwolfer.db already loaded with data, run:

    python parser.py --onlyanalyze=false --fname=./data/small_input --ftype=txt

The application prints all of its analysis to stdout, if you would like to
capture it via another file, simlply redirect it, e.g.:

    python parser.py --fname=./data/big_input.gz --ftype=gzip > output.txt

How to test
-----------

The test suite has a few small tests and an integration test that runs in
memory, it can be run using:

    python test_parser.py

Benchmarks
----------

### Reading the big_input.gz data file into the system.

#### PyPy-2.5.1 @ 2048 mb ram on vagrant precise32 (this is a weak benchmark)
- real:	50m11.426s
- user:	0m24.582s
- sys:	16m41.775s
