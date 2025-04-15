###### import tools ######
import pytest
from peewee import SqliteDatabase
from database.models import Driver, Racing, Error
import datetime


###### create test database ######
@pytest.fixture(scope="function")
def test_db(monkeypatch):
    test_db = SqliteDatabase(":memory:")
    monkeypatch.setattr("config_fldr.config.DATABASE", test_db)
    test_db.bind([Driver, Racing, Error])
    test_db.connect()
    test_db.create_tables([Driver, Racing, Error])
    yield test_db
    test_db.drop_tables([Driver, Racing, Error])
    test_db.close()


###### TESTS ######
###### test Driver ######
def test_create_driver(test_db):
    driver = Driver.create(name="Lewis Hamilton", abbr="HAM", team="Mercedes")
    assert driver.name == "Lewis Hamilton"
    assert driver.abbr == "HAM"
    assert driver.team == "Mercedes"


###### test Racing ######
def test_create_racing(test_db):
    driver = Driver.create(name="Max Verstappen", abbr="VER", team="Red Bull")
    race = Racing.create(
        abbr="VER",
        start_time=datetime.datetime(2024, 1, 1, 12, 0),
        end_time=datetime.datetime(2024, 1, 1, 12, 2),
        time=datetime.datetime(1900, 1, 1, 0, 2, 0),  # 2 хв як дата
        relevant_time=True,
        position=1,
        driver_id=driver,
    )
    assert race.driver_id == driver
    assert race.abbr == "VER"
    assert race.position == 1


###### test Error ######
def test_create_error(test_db):
    error = Error.create(error_type="format", general_error="Invalid line format")
    assert error.error_type == "format"
    assert "format" in error.error_type
    assert "Invalid" in error.general_error
