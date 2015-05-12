Steps to install
----------------

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

How to run
----------

For all text based filetypes, the following command will load in all of the
data then run analyses on it.

    python parser.py --fname=./data/small_input --ftype=txt

If the file is a gzip file, the following command will work:

    python parser.py --fname=./data/big_input.gz --ftype=gzip

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

#### PyPy-2.5.1 @ 2048 mb ram
- real:	50m11.426s
- user:	0m24.582s
- sys:	16m41.775s
