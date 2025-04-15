###### import tools ######
from flask import request
from flask_restful import Resource
from peewee import DoesNotExist, JOIN

from database.models import Driver, Racing, Error
from racing_report.tools import (
    response_format,
    from_class_list_to_dict_report,
    from_class_list_to_dict_errors,
    from_class_list_to_dict_drivers,
)


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
            order_by_arg = -Racing.position if order == "asc" else Racing.position
            drivers_with_position = list(
                Racing.select()
                .where(Racing.position.is_null(False))
                .order_by(order_by_arg)
            )
            drivers_without_position = (
                Racing.select()
                .join(Driver, JOIN.INNER)
                .where(
                    (Racing.position.is_null(True)) & (Racing.driver_id.is_null(False))
                )
            )
            errors = list(Error.select())
            results["drivers_with_position"] = from_class_list_to_dict_report(
                drivers_with_position
            )
            results["drivers_without_position"] = from_class_list_to_dict_report(
                drivers_without_position
            )
            results["errors"] = from_class_list_to_dict_errors(errors)
        return response_format(results)


###### all drivers`s info ######
class Drivers(Resource):
    @staticmethod
    def get():
        results = dict()
        order = request.args.get("order", default="desc", type=str)
        if order not in ("desc", "asc", ""):
            results["errors"] = (
                f"Wrong parameter 'order' -> '{order}'. Choose from between 'desc' and 'asc' (for example: '/drivers?order=asc')"
            )
        else:
            order_by_arg = -Driver.abbr if order == "asc" else Driver.abbr
            drivers = list(Driver.select().order_by(order_by_arg))
            errors = list(
                Error.select().where(
                    Error.error_type == "wrong format of drivers`s data"
                )
            )
            results["drivers"] = from_class_list_to_dict_drivers(drivers)
            results["errors"] = from_class_list_to_dict_errors(errors)
        return response_format(results)


###### single driver`s info ######
class AloneDriver(Resource):
    @staticmethod
    def get(driver_id):
        results = dict()
        try:
            race = [
                Racing.get(abbr=driver_id),
            ]
            results["drivers"] = from_class_list_to_dict_report(race)
        except DoesNotExist:
            results["errors"] = f"Wrong parameter 'driver_id' -> '{driver_id}'."
        return response_format(results)
