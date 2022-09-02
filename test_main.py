#
# This module implements a trivial test example with pytest and testcontainers.
# First, three fixtures are defined:
#   get_source_db_postgres():
#       creates an empty Postgres container
#   generate_source_data():
#       generates 100 rows using Faker of the following structure {id, name}
#   setup_source_db():
#        creates a new table and populates it with the test data
#
# Next, we run a couple of tests:
#   test_db_count(): verify the number of rows in the database is the same as the generated list
#   test_db_max_name(): verify the longes name in the database is the same as in the source data

from typing import Tuple
import pytest
import sqlalchemy
from testcontainers.postgres import PostgresContainer
from faker import Faker

# table name that will be created during the test session
SOURCE_TABLE = "test_table"


# need to redefine this to change the scope of the fixture
@pytest.fixture(scope="module")
def faker() -> Faker:
    return Faker()


@pytest.fixture(scope="module")
def get_source_db_postgres():
    """Fixture to create an empty Postgres container for the test session."""
    with PostgresContainer("postgres:latest") as pgc:
        yield pgc.get_connection_url()
        print(f"Destroying container: {pgc.image}")


@pytest.fixture(scope="module")
def generate_source_data(faker, num_lines: int = 100) -> Tuple:
    """
    Fixture to generate source data for the test.

    Parameters:
        faker: Instance of Faker().
        num_lines (int): Number of lines to generate (default is 100).

    Returns:
        Tuple: Generated data for the test.
    """

    data = tuple()
    for i in range(num_lines):
        data = data + ({"id": i, "name": faker.name()},)
    return data


@pytest.fixture(scope="module")
def setup_source_db(generate_source_data: Tuple, get_source_db_postgres: str) -> str:
    """
    Fixture to initialize the source db before the test session. It creates
    a new table and populates it with the generated source data.

    Parameters:
        generate_source_data: Fixture returning a Tuple representing
            generated test data.
        get_source_db_postgres (str): Fixture returning the connection
            string to an empty Postgres database in a test container.

    Returns:
        str: Connection string to a populated database.
    """

    engine = sqlalchemy.create_engine(get_source_db_postgres)
    with engine.connect() as conn:
        conn.execute(
            f"CREATE TABLE {SOURCE_TABLE}(id INTEGER PRIMARY KEY, name TEXT)")
        # TODO: Need to optimize, I know there is a better way to insert bulk data
        for line in generate_source_data:
            conn.execute(
                f"INSERT INTO {SOURCE_TABLE}(id, name) \
                    VALUES({line['id']}, \'{line['name']}\')")
    return get_source_db_postgres


class TestDB:
    """This class is to simply group the tests together"""

    def test_db_count(self, setup_source_db):
        """Check the count of lines in the populated database."""
        engine = sqlalchemy.create_engine(setup_source_db)
        with engine.connect() as conn:
            result = conn.execute(
                f"SELECT count(*) FROM {SOURCE_TABLE}").first()
            if result is not None:
                assert result[0] == 100   # should be 100 rows
                print(f"All good, number of rows in a database: {result[0]}")
            else:
                pytest.fail(
                    "Something went wrong: database did not return any value...")

    def test_db_max_name(self, generate_source_data, setup_source_db):
        """Check the longest name value in the source list and compares to the DB."""

        # get the list of names from the generated data
        names_list = [x['name'] for x in generate_source_data]
        # get the max by len since we need the longest name
        max_list_name = max(names_list, key=lambda x: len(x))

        engine = sqlalchemy.create_engine(setup_source_db)
        with engine.connect() as conn:
            result = conn.execute(
                f"SELECT name FROM {SOURCE_TABLE} WHERE length(name) = \
                    (SELECT max(length(name)) FROM {SOURCE_TABLE})").all()
            max_db_name = result[0][0]
            print(
                f"Max name in source: {max_list_name}, and in db: {max_db_name}")
            assert max_db_name == max_list_name  # should be the same
