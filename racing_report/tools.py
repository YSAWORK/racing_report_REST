###### import tools ######
from flask import request, make_response
import xml.etree.ElementTree as Et
import json
from dicttoxml import dicttoxml


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


###### convert info from list of class_objects to dict ######
def from_class_list_to_dict_report(data_info):
    drivers = dict()
    for race in data_info:
        if race.driver_id != None:
            driver_info = race.driver_id.__data__.copy()
        else:
            driver_info = dict()
        driver_dict = driver_info | race.__data__.copy()
        del driver_dict["id"], driver_dict["driver_id"]
        drivers[driver_dict["abbr"]] = driver_dict
    return drivers


###### convert info from list of class_objects to dict ######
def from_class_list_to_dict_errors(data_info):
    errors_dict = dict()
    for i, error in enumerate(data_info):
        errors_dict[str(i)] = error.general_error
    return errors_dict


###### convert info from list of class_objects to dict ######
def from_class_list_to_dict_drivers(data_info):
    drivers = dict()
    for driver in data_info:
        driver_dict = driver.__data__.copy()
        del driver_dict["id"]
        drivers[driver_dict["abbr"]] = driver_dict
    return drivers


###### make response with choosing format ######
def response_format(data: dict):
    format_res = request.args.get("format", "json").lower()
    if format_res == "xml":
        xml_string = dicttoxml(data, custom_root="response", attr_type=False)
        return make_response(xml_string, {"Content-Type": "application/xml"})
    return make_response(
        json.dumps(data, default=str), {"Content-Type": "application/json"}
    )
