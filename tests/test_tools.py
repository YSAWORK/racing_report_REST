###### import tools ######
import xml.etree.ElementTree as Et
import racing_report as main_code


###### test func dict_to_xml ######
# ----- simple dict -----#
def test_dict_to_xml_basic():
    test_dict = {"name": "John", "age": 30}
    expected_xml = "<root><name>John</name><age>30</age></root>"
    result = main_code.main_public.dict_to_xml("root", test_dict)
    result_str = Et.tostring(result, encoding="unicode")
    assert result_str.strip() == expected_xml.strip()


# ----- dict with list -----#
def test_dict_to_xml_with_list():
    test_dict = {"name": "John", "contacts": ["123456789", "987654321"]}
    expected_xml = "<root><name>John</name><contacts><item>123456789</item><item>987654321</item></contacts></root>"
    result = main_code.main_public.dict_to_xml("root", test_dict)
    result_str = Et.tostring(result, encoding="unicode")
    assert result_str.strip() == expected_xml.strip()


# ----- dict with nested dict -----#
def test_dict_to_xml_with_nested_dict():
    test_dict = {"name": "John", "address": {"city": "New York", "zipcode": "10001"}}
    expected_xml = "<root><name>John</name><address><city>New York</city><zipcode>10001</zipcode></address></root>"
    result = main_code.main_public.dict_to_xml("root", test_dict)
    result_str = Et.tostring(result, encoding="unicode")
    assert result_str.strip() == expected_xml.strip()
