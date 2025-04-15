###### import tools #####
import pytest
from flask import Flask
from racing_report import tools


###### create test app ######
@pytest.fixture
def test_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


###### TESTS ######
###### test response format ######
# ----- test response format with json -----#
def test_response_format_json(test_app):
    with test_app.test_request_context("/fake?format=json"):
        data = {"test": "value"}
        response = tools.response_format(data)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert b'"test": "value"' in response.data


# ----- test response format with xml -----#
def test_response_format_xml(test_app):
    with test_app.test_request_context("/fake?format=xml"):
        data = {"message": "hello", "list": [1, 2]}
        response = tools.response_format(data)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/xml"
        assert b"<response>" in response.data
        assert b"<message>hello</message>" in response.data
        assert b"<list>" in response.data


###### test dict_to_xml ######
def test_dict_to_xml():
    data = {"greeting": "hello", "numbers": [1, 2, 3], "nested": {"a": "b"}}
    xml_elem = tools.dict_to_xml("root", data)
    assert xml_elem.tag == "root"
    assert any(child.tag == "greeting" for child in xml_elem)
    assert any(child.tag == "numbers" for child in xml_elem)
    assert any(child.tag == "nested" for child in xml_elem)


###### test rom_class_list_to_dict_errors #######
class MockError:
    def __init__(self, msg):
        self.general_error = msg


def test_from_class_list_to_dict_errors():
    errors = [MockError("e1"), MockError("e2")]
    result = tools.from_class_list_to_dict_errors(errors)
    assert result == {"0": "e1", "1": "e2"}


###### test rom_class_list_to_dict_drivers #######
class MockDriver:
    def __init__(self, abbr, name, team):
        self.__data__ = {"abbr": abbr, "name": name, "team": team, "id": 99}


def test_from_class_list_to_dict_drivers():
    drivers = [MockDriver("ABC", "Test Name", "Test Team")]
    result = tools.from_class_list_to_dict_drivers(drivers)
    assert "ABC" in result
    assert result["ABC"]["name"] == "Test Name"


###### test rom_class_list_to_dict_report #######
class MockDriverID:
    def __init__(self, abbr, name):
        self.__data__ = {"abbr": abbr, "name": name, "team": "Some Team", "id": 1}


class MockRace:
    def __init__(self, abbr, position, driver=None):
        self.__data__ = {
            "abbr": abbr,
            "start_time": "now",
            "end_time": "later",
            "time": 90,
            "relevant_time": True,
            "position": position,
            "driver_id": driver,
            "id": 10,
        }
        self.driver_id = driver


def test_from_class_list_to_dict_report():
    mock_driver = MockDriverID("XYZ", "Driver X")
    race = MockRace("XYZ", 1, driver=mock_driver)
    result = tools.from_class_list_to_dict_report([race])
    assert "XYZ" in result
    assert result["XYZ"]["abbr"] == "XYZ"
    assert result["XYZ"]["position"] == 1
