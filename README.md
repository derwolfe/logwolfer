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

#### cpython2.7.3 @ 2048 mb ram
- real:	24m16.494s
- user:	0m25.290s
- sys:	7m18.507s

#### PyPy-2.5.1 @ 2048 mb ram
- real:	23m41.414s
- user:	0m16.173s
- sys:	7m38.157s

<!-- |Python|Real|User|Sys| -->
<!-- |---|---|---|---|---| -->
<!-- |CPython2.7.3|24m16.494s|0m25.290s|7m18.507s| -->
<!-- |PyPy2.5.1|23m41.414s|0m16.173s|7m38.157s| -->
