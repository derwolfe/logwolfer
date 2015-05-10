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

    python parser.py <logfile_name>.gz


How to test
-----------

    python test_parser.py

Benchmarks
----------

### Reading the big_input.gz data file into the system.

#### cpython2.7.3 with 384 mb ram

- real:	24m4.440s
- user:	0m28.826s
- sys: 7m42.293s

#### PyPy-2.5.1 with 384 mb ram

- real:	27m57.182s
- user:	0m29.818s
- sys: 10m1.050s
