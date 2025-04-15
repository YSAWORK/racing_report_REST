###### import tools ######
import pytest
from peewee import SqliteDatabase
from database.models import Driver, Racing, Error
from database.covert_to_db import (
    check_databases_exists,
    create_drivers_database,
    errors_list,
    create_time_in_racing_database,
    create_racing_database,
    check_results_exist,
    get_position,
    create_errors_database,
)
from config_fldr import config
import datetime


###### create test database ######
@pytest.fixture
def in_memory_db(monkeypatch):
    db = SqliteDatabase(":memory:")
    monkeypatch.setattr(config, "DATABASE", db)
    Driver._meta.database = db
    Racing._meta.database = db
    Error._meta.database = db
    db.bind([Driver, Racing, Error])
    db.connect()
    db.create_tables([Driver, Racing, Error])  # <--- автоматично створюємо
    yield db
    db.drop_tables([Driver, Racing, Error])
    db.close()


###### TESTS ######
###### test check_databases_exists ######
def test_check_databases_exists(in_memory_db):
    in_memory_db.drop_tables([Driver, Racing, Error])
    # ----- check absence of tables -----#
    assert not Driver.table_exists()
    assert not Racing.table_exists()
    assert not Error.table_exists()
    # ----- run check_databases_exists -----#
    check_databases_exists()
    # ----- check creation of tables ------#
    assert Driver.table_exists()
    assert Racing.table_exists()
    assert Error.table_exists()


###### test create_drivers_database ######
# ----- create temporary data_file -----#
@pytest.fixture
def temp_driver_file(tmp_path):
    log_dir = tmp_path / "database" / "log_data"
    log_dir.mkdir(parents=True)
    content = "\n".join(
        [
            "ABC_John_Doe",  # valid
            "XYZ_Mary_Smith",  # valid
            "BADENTRY",  # invalid
            "",  # empty
            "BAD_FORMAT_TOO_LONG_ENTRY",  # invalid
            "QQQ_Joe",  # invalid
        ]
    )
    file_path = log_dir / "abbreviations.txt"
    file_path.write_text(content)
    config.BASE_DIR = str(tmp_path)
    return "abbreviations.txt"


# ----- test create_drivers_database with test data_file -----#
def test_create_drivers_database(in_memory_db, temp_driver_file):
    errors_list.clear()
    check_databases_exists()
    create_drivers_database(temp_driver_file)
    # ----- check valid -----#
    drivers = list(Driver.select())
    assert len(drivers) == 2
    assert {d.abbr for d in drivers} == {"ABC", "XYZ"}
    # ----- check invalid -----#
    assert len(errors_list) == 3
    assert all("not included in results" in e[0] for e in errors_list)
    assert all(e[1] == "wrong format of drivers`s data" for e in errors_list)


###### test create_drivers_database ######
# ----- create temporary data_file -----#
@pytest.fixture
def temp_racing_file(tmp_path):
    log_dir = tmp_path / "database" / "log_data"
    log_dir.mkdir(parents=True)
    # ---- start.log -----#
    start_log = log_dir / "start.log"
    start_log.write_text(
        "\n".join(
            [
                "ABC2024-01-01_12:00:00.000",  # valid
                "BADFORMAT",  # invalid
                "",  # empty
                "XYZ2024-01-01_12:01:00.000",  # no such driver
            ]
        )
    )
    # ---- end.log -----#
    end_log = log_dir / "end.log"
    end_log.write_text(
        "\n".join(
            [
                "ABC2024-01-01_12:02:00.000",  # valid
                "XYZ2024-01-01_12:03:00.000",  # no such driver
            ]
        )
    )
    config.BASE_DIR = str(tmp_path)
    return "start.log", "end.log"


# ----- test create_racing_database -----#
def test_create_racing_database(in_memory_db, temp_racing_file):
    # ----- driver`s creation -----#
    Driver.create(name="Test Name", abbr="ABC", team="Test Team")

    errors_list.clear()
    start_log, end_log = temp_racing_file

    # ----- test start_time -----#
    create_racing_database(start_log, "start")
    races = list(Racing.select())
    assert len(races) == 2  # ABC + XYZ
    abc = Racing.get(Racing.abbr == "ABC")
    assert abc.start_time == datetime.datetime(2024, 1, 1, 12, 0, 0)
    assert abc.driver_id.abbr == "ABC"
    xyz = Racing.get(Racing.abbr == "XYZ")
    assert xyz.driver_id is None

    # ----- check errors -----#
    assert len(errors_list) == 1
    assert "BADFORMAT not included in results" in errors_list[0][0]

    # ----- test end_time -----#
    create_racing_database(end_log, "end")
    abc = Racing.get(Racing.abbr == "ABC")
    assert abc.end_time == datetime.datetime(2024, 1, 1, 12, 2, 0)
    xyz = Racing.get(Racing.abbr == "XYZ")
    assert xyz.end_time == datetime.datetime(2024, 1, 1, 12, 3, 0)


###### test create_time_in_racing_database ######
def test_create_time_in_racing_database(in_memory_db):
    # ----- create driver -----#
    driver = Driver.create(name="Test Driver", abbr="TST", team="Team X")
    # ----- valid data -----#
    race1 = Racing.create(
        driver_id=driver,
        abbr="TST",
        start_time=datetime.datetime(2024, 1, 1, 12, 0, 0),
        end_time=datetime.datetime(2024, 1, 1, 12, 2, 0),
    )
    # ----- invalid data -----#
    race2 = Racing.create(
        driver_id=driver,
        abbr="ERR",
        start_time=datetime.datetime(2024, 1, 1, 13, 0, 0),
        end_time=datetime.datetime(2024, 1, 1, 12, 59, 59),
    )
    # ----- check data -----#
    create_time_in_racing_database()
    race1 = Racing.get(Racing.id == race1.id)
    assert race1.time == 120.0
    assert race1.relevant_time is True
    race2 = Racing.get(Racing.id == race2.id)
    assert race2.time == -1.0
    assert race2.relevant_time is False


###### test check_results_exist ######
def test_check_results_exist(in_memory_db):
    errors_list.clear()
    # ----- create valid driver -----#
    valid_driver = Driver.create(name="Valid One", abbr="VAL", team="Alpha")
    Racing.create(
        driver_id=valid_driver,
        abbr="VAL",
        start_time=datetime.datetime(2024, 1, 1, 10, 0, 0),
        end_time=datetime.datetime(2024, 1, 1, 10, 1, 0),
    )
    # ----- create invalid driver -----#
    Racing.create(
        driver_id=None,
        abbr="XXX",
        start_time=datetime.datetime(2024, 1, 1, 11, 0, 0),
        end_time=datetime.datetime(2024, 1, 1, 11, 1, 0),
    )
    # ----- check data -----#
    check_results_exist()
    assert len(errors_list) == 1
    assert errors_list[0][0] == "XXX hasn`t enough data. Not included in results"
    assert errors_list[0][1] == "no driver"


###### test get_position ######
def test_get_position(in_memory_db):
    # ----- create drivers -----#
    driver1 = Driver.create(name="Driver A", abbr="AAA", team="Team A")
    driver2 = Driver.create(name="Driver B", abbr="BBB", team="Team B")
    driver3 = Driver.create(name="Driver C", abbr="CCC", team="Team C")

    # ----- create races -----#
    Racing.create(
        driver_id=driver1,
        abbr="AAA",
        start_time=datetime.datetime(2024, 1, 1, 12, 0, 0),
        end_time=datetime.datetime(2024, 1, 1, 12, 2, 0),
        time=120.0,
        relevant_time=True,
    )
    Racing.create(
        driver_id=driver2,
        abbr="BBB",
        start_time=datetime.datetime(2024, 1, 1, 12, 0, 0),
        end_time=datetime.datetime(2024, 1, 1, 12, 1, 0),
        time=60.0,
        relevant_time=True,
    )
    Racing.create(
        driver_id=driver3,
        abbr="CCC",
        start_time=datetime.datetime(2024, 1, 1, 12, 0, 0),
        end_time=datetime.datetime(2024, 1, 1, 12, 3, 0),
        time=180.0,
        relevant_time=True,
    )

    # ----- check data -----#
    get_position()
    results = list(Racing.select().order_by(Racing.position))
    assert results[0].abbr == "BBB"
    assert results[0].position == 1
    assert results[1].abbr == "AAA"
    assert results[1].position == 2
    assert results[2].abbr == "CCC"
    assert results[2].position == 3


###### test create_errors_database ######
def test_create_errors_database(in_memory_db):
    # ----- create erroors`s list -----#
    errors_list.clear()
    errors_list.extend(
        [
            ("Driver X missing", "no driver"),
            ("Wrong format in row 3", "wrong format of drivers`s data"),
            ("Driver X missing", "no driver"),
        ]
    )
    # ----- check data -----#
    create_errors_database()
    all_errors = list(Error.select())
    assert len(all_errors) == 2  # має бути тільки 2 записи, без дублів
    error_messages = {(e.general_error, e.error_type) for e in all_errors}
    assert ("Driver X missing", "no driver") in error_messages
    assert ("Wrong format in row 3", "wrong format of drivers`s data") in error_messages
