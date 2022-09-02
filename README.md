# Test Containers
Experimenting with test containers and pytest

## How to Run

Create new environment and install dependencies:
```
python3 -m venv venv/test

source venv/test/bin/activate

pip install -r requirements.txt
```

Run tests with `pytest`:
```
pytest -s
```

This will run two tests and produce the following output:
```
======================================================== test session starts ========================================================
platform linux -- Python 3.8.10, pytest-7.1.2, pluggy-1.0.0
rootdir: /mnt/c/Users/Dima/Projects/python/test-containers
plugins: Faker-14.1.0
collected 2 items

test_main.py Pulling image postgres:latest
Container started: d8a8086a401a
Waiting to be ready...
Waiting to be ready...
Waiting to be ready...
Waiting to be ready...
All good, number of rows in a database: 100
.Max name in source: Deborah Hutchinson MD, and in db: Deborah Hutchinson MD
.Destroying container: postgres:latest


======================================================== 2 passed in 12.99s =========================================================
```