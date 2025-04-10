###### import tools ######
import json, pytest, datetime
from flask import request, make_response
import xml.etree.ElementTree as Et
from collections import namedtuple
from dataclasses import dataclass
import racing_report as main_code


###### create test-class ######
@dataclass
class DriversTest:
    name: str
    abbr: str
    team: str
    start_time: datetime
    end_time: datetime
    position: int | None = None
    time: datetime.timedelta | None = None
    error: str | None = None


###### convert dict to xml format ######
def dict_to_xml(elem: str, dict_data: dict):
    el = Et.Element(elem)
    for key, val in dict_data.items():
        if isinstance(val, dict):
            el.append(dict_to_xml(key, val))
        elif isinstance(val, list):
            list_tag = Et.SubElement(el, key)
            for i in val:
                subchild = Et.SubElement(list_tag, "item")
                if isinstance(i, dict):
                    subchild.append(dict_to_xml("item", i))
                else:
                    subchild.text = str(i)
        else:
            child = Et.SubElement(el, key)
            child.text = str(val)
    return el


###### make response with choosing format ######
def response_format(data: dict):
    format_res = request.args.get("format", "json").lower()
    if format_res == "xml":
        xml_data = dict_to_xml("response", data)
        xml_string = Et.tostring(xml_data).decode()
        return make_response(xml_string, {"Content-Type": "application/xml"})
    return make_response(json.dumps(data), {"Content-Type": "application/json"})


###### convert info from list of class_objects to dict ######
def from_class_list_to_dict(data):
    if not data:
        return {}
    drivers_list = dict()
    for driver in data:
        drivers_list[driver.abbr] = vars(driver)
        for key in drivers_list[driver.abbr].keys():
            if type(drivers_list[driver.abbr][key]) != str:
                drivers_list[driver.abbr][key] = str(drivers_list[driver.abbr][key])
    return drivers_list


###### sort drivers`s data: correct/incorrect ######
def sort_incorrect_data(data):
    incorrect_data_drivers = tuple(
        filter(lambda el: el.error == "incorrect data", data)
    )
    correct_data_drivers = tuple(set(data) - set(incorrect_data_drivers))
    return correct_data_drivers, incorrect_data_drivers




###### test func from_class_list_to_dict ######
@pytest.mark.parametrize(
    "driver, driver_dict",
    [
        (
            DriversTest(
                "Lewis Hamilton",
                "HAM",
                "RENAULT",
                datetime.datetime.strptime(
                    "2018-05-24 12:03:15.145000", "%Y-%m-%d %H:%M:%S.%f"
                ),
                datetime.datetime.strptime(
                    "2018-05-24 12:04:28.095000", "%Y-%m-%d %H:%M:%S.%f"
                ),
                1,
                None,
                None,
            ),
            {
                "HAM": {
                    "name": "Lewis Hamilton",
                    "abbr": "HAM",
                    "team": "RENAULT",
                    "start_time": "2018-05-24 12:03:15.145000",
                    "end_time": "2018-05-24 12:04:28.095000",
                    "position": "1",
                    "time": "None",
                    "error": "None",
                }
            },
        ),
    ],
)
def test_from_class_list_to_dict(driver, driver_dict):
    expected = main_code.from_class_list_to_dict((driver,))
    assert driver_dict == expected


###### test func sort_incorrect_data ######
Driver = namedtuple("Driver", ["name", "error"])
@pytest.mark.parametrize(
    "drivers, expected_correct_data, expected_incorrect_data",
    [
        (
            (
                Driver("Driver1", "incorrect data"),
                Driver("Driver2", "correct data"),
                Driver("Driver3", "incorrect data"),
                Driver("Driver4", "correct data"),
            ),
            (
                Driver(name="Driver4", error="correct data"),
                Driver(name="Driver2", error="correct data"),
            ),
            (
                Driver(name="Driver1", error="incorrect data"),
                Driver(name="Driver3", error="incorrect data"),
            ),
        ),
    ],
)
def test_sort_incorrect_data(drivers, expected_correct_data, expected_incorrect_data):
    correct_data, incorrect_data = main_code.sort_incorrect_data(drivers)
    assert set(correct_data) == set(expected_correct_data)
    assert set(incorrect_data) == set(expected_incorrect_data)
