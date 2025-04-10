###### import tools #######
import pytest
from unittest.mock import patch, MagicMock
import racing_report as main_code


###### create test app ######
@pytest.fixture
def client():
    main_code.app.testing = True
    with main_code.app.test_client() as client:
        yield client


###### test Report.get ######
@patch("racing_report.request_main.get_list_info")
@patch("racing_report.tools.from_class_list_to_dict")
def test_get_report(mock_from_class_list_to_dict, mock_get_list_info, client):
    mock_driver_1 = MagicMock(position=1, abbr='AAA')
    mock_driver_2 = MagicMock(position=None, abbr='BBB')
    mock_get_list_info.return_value = ([mock_driver_1, mock_driver_2], [])
    mock_from_class_list_to_dict.side_effect = lambda x: [
        {"position": driver.position} for driver in x
    ]

    response = client.get("api/v1/report?order=asc")
    data = response.get_json()

    assert response.status_code == 200
    assert "drivers_with_position" in data
    assert "drivers_without_position" in data
    assert "errors" in data
    assert len(data["drivers_with_position"]) == 1
    assert len(data["drivers_without_position"]) == 1


@patch("racing_report.request_main.get_list_info")
def test_get_report_invalid_order(mock_get_list_info, client):
    response = client.get("api/v1/report?order=wrong_order")
    data = response.get_json()

    assert response.status_code == 200
    assert "errors" in data
    assert "Wrong parameter 'order'" in data["errors"]


###### test Drivers.get ######
@patch("racing_report.request_main.get_list_info")
@patch("racing_report.tools.sort_incorrect_data")
@patch("racing_report.tools.from_class_list_to_dict")
@patch("racing_report.tools.response_format")
def test_get_drivers(
    mock_response_format,
    mock_from_class_list_to_dict,
    mock_sort_incorrect_data,
    mock_get_list_info,
    client,
):
    # ----- mocks`s data -----#
    mock_driver_1 = MagicMock()
    mock_driver_1.abbr = "AAA"
    mock_driver_1.position = 1
    mock_driver_2 = MagicMock()
    mock_driver_2.abbr = "BBB"
    mock_driver_2.position = None
    mock_sorted_drivers = ([mock_driver_1], [mock_driver_2])
    # ----- mocks`s settings -----#
    mock_get_list_info.return_value = ([mock_driver_1, mock_driver_2], [])
    mock_sort_incorrect_data.return_value = mock_sorted_drivers
    mock_from_class_list_to_dict.side_effect = lambda x: [
        {"position": driver.position, "abbr": driver.abbr} for driver in x
    ]
    # ----- mock response -----#
    mock_response_format.return_value = {
        "drivers": [{"position": 1}],
        "drivers_incor_data": [{"position": None}],
        "errors": [],
    }
    # ----- sending GET request -----#
    response = client.get("api/v1/drivers")
    # ----- asserts -----#
    assert response.status_code == 200
    data = response.get_json()
    assert "drivers" in data
    assert "drivers_incor_data" in data
    assert "errors" in data
    assert len(data["drivers"]) == 1
    assert len(data["drivers_incor_data"]) == 1
    assert data["drivers"][0]["position"] == 1
    assert data["drivers_incor_data"][0]["position"] is None
    mock_get_list_info.assert_called_once_with("desc", "name")
    mock_sort_incorrect_data.assert_called_once_with((mock_driver_1, mock_driver_2))
    mock_from_class_list_to_dict.assert_any_call([mock_driver_1, mock_driver_2])


###### test AloneDriver.get ######
# ----- correct id -----#
@patch("racing_report.request_main.get_driver_info")
@patch("racing_report.tools.from_class_list_to_dict")
@patch("racing_report.tools.response_format")
def test_get_alone_driver(
    mock_response_format, mock_from_class_list_to_dict, mock_get_driver_info, client
):
    # ----- mocks`s data -----#
    mock_driver = MagicMock()
    mock_driver.abbr = "AAA"
    mock_driver.name = "Lewis Hamilton"
    mock_driver.position = 1
    # ----- mocks`s settings -----#
    mock_get_driver_info.return_value = mock_driver
    mock_from_class_list_to_dict.return_value = [
        {
            "abbr": mock_driver.abbr,
            "name": mock_driver.name,
            "position": mock_driver.position,
        }
    ]
    mock_response_format.return_value = {
        "drivers": [{"abbr": "AAA", "name": "Lewis Hamilton", "position": 1}],
        "errors": [],
    }
    # ----- sending GET request -----#
    driver_id = "AAA"
    response = client.get(f"api/v1/drivers/{driver_id}")
    # ----- asserts -----#
    assert response.status_code == 200
    data = response.get_json()
    assert "drivers" in data
    assert len(data["drivers"]) == 1
    assert data["drivers"]['AAA']["abbr"] == "AAA"
    assert data["drivers"]['AAA']["name"] == "Lewis Hamilton"
    assert data["drivers"]['AAA']["position"] == '1'


# ----- invalid id -----#
@patch("racing_report.request_main.get_driver_info")
@patch("racing_report.tools.response_format")
def test_get_alone_driver_invalid_id(
    mock_response_format, mock_get_driver_info, client
):
    mock_get_driver_info.side_effect = ValueError("Driver not found")
    mock_response_format.return_value = {
        "drivers": [],
        "errors": ["Wrong parameter 'driver_id' -> 'BBB'."],
    }
    # ----- sending GET request -----#
    driver_id = "BBB"
    response = client.get(f"api/v1/drivers/{driver_id}")
    # ----- asserts -----#
    assert response.status_code == 200
    data = response.get_json()
    assert "errors" in data
    assert "Wrong parameter 'driver_id' -> 'BBB'." in data["errors"]
