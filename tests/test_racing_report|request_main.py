###### import tools ######
import pytest
from flask import Flask
from flask_restful import Api
from database.models import Driver, Racing, Error
from racing_report.request_main import Report, Drivers, AloneDriver
from peewee import SqliteDatabase
import datetime


###### test data ######
@pytest.fixture
def test_client(monkeypatch):
    # ---- test database -----#
    test_db = SqliteDatabase(":memory:")
    monkeypatch.setattr("config_fldr.config.DATABASE", test_db)
    test_db.bind([Driver, Racing, Error])
    test_db.connect()
    test_db.create_tables([Driver, Racing, Error])

    # ---- test data -----#
    driver1 = Driver.create(abbr="AAA", name="Driver A", team="Team A")
    driver2 = Driver.create(abbr="BBB", name="Driver B", team="Team B")

    Racing.create(
        abbr="AAA",
        start_time=datetime.datetime(2024, 1, 1, 12, 0, 0),
        end_time=datetime.datetime(2024, 1, 1, 12, 2, 0),
        time=120,
        relevant_time=True,
        position=2,
        driver=driver1,
    )
    Racing.create(
        abbr="BBB",
        start_time=datetime.datetime(2024, 1, 1, 12, 1, 0),
        end_time=datetime.datetime(2024, 1, 1, 12, 2, 0),
        time=60,
        relevant_time=True,
        position=1,
        driver=driver2,
    )
    Error.create(
        general_error="Bad driver format", error_type="wrong format of drivers`s data"
    )

    # ----- test app -----#
    app = Flask(__name__)
    app.config["TESTING"] = True
    api = Api(app)
    api.add_resource(Report, "/api/v1/report")
    api.add_resource(Drivers, "/api/v1/drivers")
    api.add_resource(AloneDriver, "/api/v1/drivers/<driver_id>")

    with app.test_client() as client:
        yield client

    test_db.drop_tables([Driver, Racing, Error])
    test_db.close()


###### TESTS ######
###### test Report ######
# ----- test Report with dest order -----#
def test_report_asc(test_client):
    response = test_client.get("/api/v1/report?order=asc&format=json")
    assert response.status_code == 200
    data = response.get_json()
    assert "drivers_with_position" in data
    assert list(data["drivers_with_position"].keys())[0] == "AAA"


# ----- test Report with ast order -----#
def test_report_desc(test_client):
    response = test_client.get("/api/v1/report?order=desc&format=json")
    assert response.status_code == 200
    data = response.get_json()
    assert list(data["drivers_with_position"].keys())[0] == "BBB"


# ----- test Report with invalid order -----#
def test_report_invalid_order(test_client):
    response = test_client.get("/api/v1/report?order=wrong&format=json")
    assert response.status_code == 200
    data = response.get_json()
    assert "errors" in data
    assert "Wrong parameter" in data["errors"]


###### test Drivers ######
# ----- test Drivers with dest order -----#
def test_drivers_desc(test_client):
    response = test_client.get("/api/v1/drivers?order=desc&format=json")
    assert response.status_code == 200
    data = response.get_json()
    assert list(data["drivers"].keys())[0] == "AAA"


# ----- test Drivers with ast order -----#
def test_drivers_asc(test_client):
    response = test_client.get("/api/v1/drivers?order=asc&format=json")
    assert response.status_code == 200
    data = response.get_json()
    assert list(data["drivers"].keys())[0] == "BBB"


# ----- test Drivers with invalid order -----#
def test_drivers_invalid_order(test_client):
    response = test_client.get("/api/v1/drivers?order=xyz&format=json")
    data = response.get_json()
    assert "errors" in data
    assert "Wrong parameter" in data["errors"]


###### test Alone_drive #######
# ----- test Alone_drive with valid driver_id -----#
def test_alone_driver_valid(test_client):
    response = test_client.get("/api/v1/drivers/AAA?format=json")
    assert response.status_code == 200
    data = response.get_json()
    assert "AAA" in data["drivers"]


# ----- test Alone_drive with invalid driver_id -----#
def test_alone_driver_invalid(test_client):
    response = test_client.get("/api/v1/drivers/ZZZ?format=json")
    data = response.get_json()
    assert "errors" in data
    assert "driver_id" in data["errors"]
