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

#### PyPy-2.5.1 @ 2048 mb ram
- real:	50m11.426s
- user:	0m24.582s
- sys:	16m41.775s
