###### import tools ######
from flask import request
from flask_restful import Resource
from racing_report.bild_report import get_list_info, get_driver_info
from racing_report.tools import response_format, from_class_list_to_dict, sort_incorrect_data


###### racing results ######
class Report(Resource):
    @staticmethod
    def get():
        order = request.args.get("order", default="desc", type=str)
        results = dict()
        if order not in ("desc", "asc", ""):
            results["errors"] = (
                f"Wrong parameter 'order' -> '{order}'. Choose from between 'desc' and 'asc' (for example: '/drivers?order=asc')"
            )
        else:
            racing_info = get_list_info(order, "time")
            drivers_with_position = filter(lambda x: x.position, racing_info[0])
            drivers_without_position = filter(lambda x: not x.position, racing_info[0])
            results["drivers_with_position"] = from_class_list_to_dict(
                drivers_with_position
            )
            results["drivers_without_position"] = from_class_list_to_dict(
                drivers_without_position
            )
            results["errors"] = racing_info[1]
        return response_format(results)


###### all drivers`s info ######
class Drivers(Resource):
    @staticmethod
    def get():
        results = dict()
        racing_info = get_list_info("desc", "name")
        sorted_drivers = sort_incorrect_data(tuple(racing_info[0]))
        results["drivers"] = from_class_list_to_dict(sorted_drivers[0])
        results["drivers_incor_data"] = from_class_list_to_dict(sorted_drivers[1])
        results["errors"] = racing_info[1]
        return response_format(results)


###### single driver`s info ######
class AloneDriver(Resource):
    @staticmethod
    def get(driver_id):
        results = dict()
        try:
            driver = get_driver_info(driver_id)
            results["drivers"] = from_class_list_to_dict(
                [
                    driver,
                ]
            )
        except ValueError:
            results["errors"] = f"Wrong parameter 'driver_id' -> '{driver_id}'."
        return response_format(results)
