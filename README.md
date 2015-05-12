Logwolfer
=========

Welcome to Logwolfer, a command line application that ingests chat messages and
spits out an analysis of those messages.

Logwolfer is able to be run multilple times, as long as the sqlite database used
isn't deleted. This means that new messages can be added to the database after
the first run.

Three operating modes are available:

1. Load data and run analyses.
2. Load data only. This makes it possible to contine loading more and more information
   into the system, without needing to rebuild it over again. Duplicate messages will
   just be thrown away.
3. Analyze data already in the system. This allows you to run the system with data
   that has already been parsed. Naturally, this requires that you have already loaded
   data into the system.

All of the parsed messages are stored in ./logwolfer.db. This means, you can have
several versions of your logwolfer database floating around, and you can store different
versions of the database to target different times, instances, etc.

Steps to install
----------------

These install steps are targeted at Ubuntu 12.04 LTS (precise 32). They were checked
on a vagrant virtual machine.

     sudo apt-get update
     sudo apt-get install -y python-software-properties
     sudo add-apt-repository ppa:fkrull/deadsnakes
     sudo add-apt-repository -y ppa:pypy
     sudo apt-get update
     sudo apt-get install -y build-essential
     sudo apt-get install -y pypy pypy-dev
     sudo apt-get install -y python-sqlite
     sudo apt-get install -y python-pip
     sudo pip install --upgrade pip
     sudo pip install virtualenv
     virtualenv -p pypy pypyenv
     source ./pypyenv/bin/activate
     # cd into logwolfer root dir
     pip install -r requirements.txt
     # then run or test!
   

How to run
----------

For all text based filetypes, the following command will load in all of the
data in, then analyze it.

    python logwolfer.py --fname=./data/small_input --ftype=txt

If the file is a gzip file, the following command will work:

    python logwolfer.py --fname=./data/big_input.gz --ftype=gzip

To load data into the application without running any analysis steps run:

    python logwolfer.py --onlyload=True --fname=./data/small_input --ftype=txt

To only run analysis steps on a logwolfer.db already loaded with data, run:

    python logwolfer.py --onlyanalyze=false --fname=./data/small_input --ftype=txt

The application prints all of its analysis to stdout, if you would like to
capture it via another file, simlply redirect it, e.g.:

    python logwolfer.py --fname=./data/big_input.gz --ftype=gzip > output.txt

How to test
-----------

The test suite has a few small tests and an integration test that runs in
memory, it can be run using:

    python test_logwolfer.py

Benchmarks
----------

### Reading the big_input.gz data file into the system.

#### PyPy-2.5.1 @ 2048 mb ram on vagrant precise32 (this is a weak benchmark)
- real:	50m11.426s
- user:	0m24.582s
- sys:	16m41.775s
