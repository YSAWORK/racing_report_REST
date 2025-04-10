###### import tools ######
import datetime
from config_fldr import config
from dataclasses import dataclass
from functools import lru_cache


###### class of drivers and their results ######
@dataclass
class Drivers:
    name: str
    abbr: str
    team: str
    start_time: datetime
    end_time: datetime
    position: int | None = None
    time: datetime.timedelta | None = None
    error: str | None = None

    def __hash__(self):
        return hash(
            (
                self.name,
                self.abbr,
                self.team,
                self.start_time,
                self.end_time,
                self.position,
                self.time,
                self.error,
            )
        )


###### get tuple of (1) dictionary with info about time of racing`s start/finish from source files and (2) list of errors ######
def get_datetime_info(
    time_info: list, errors: dict
) -> (
    tuple
):  # dict('driver abbreviation' : driver time os start/finish in datetime format, ...)
    datetime_dict = {}
    if type(time_info) != list:
        raise TypeError
    else:
        for item in enumerate(time_info):
            if item[1] in ("", " ", "_", None):
                continue
            elif not item[1][:3].isalpha() or len(item[1][3:]) != 23:
                errors[item[1][:3]] = (
                    f"{item[1]} not included in results -- wrong data format in line {item[0] + 1} of resource file."
                )
            else:
                datetime_dict[item[1][:3]] = datetime.datetime.fromisoformat(
                    item[1][3:].replace("_", "T").strip()
                )
        return datetime_dict, errors


###### get tuple of lists (1) of Drivers`s class objects with full info about drivers and (2) errors ######
def get_drivers_list(drivers_info: list, start_data: list, end_data: list) -> tuple:
    errors = dict()
    start_datetime, errors = get_datetime_info(start_data, errors)
    end_datetime, errors = get_datetime_info(end_data, errors)
    drivers_list = list()
    for num, item in enumerate(drivers_info):
        if item in ("", " ", "_", None):
            continue
        elif len(item.split("_")) != 3:
            errors[item.replace(" ", "_")] = (
                f"{item} not included in results -- wrong data format in line {num + 1} of resource file."
            )
        else:
            driver_data = item.split("_")
            try:
                driver = Drivers(
                    abbr=driver_data[0],
                    name=driver_data[1],
                    team=driver_data[2],
                    start_time=start_datetime[driver_data[0]],
                    end_time=end_datetime[driver_data[0]],
                )
                driver.time = driver.end_time - driver.start_time
                if int(driver.time.total_seconds()) < 0:
                    driver.error = "incorrect data"
                drivers_list.append(driver)
            except KeyError:
                errors[driver_data[0]] = (
                    f"{driver_data[1]} ({driver_data[0]}) hasn`t enough data. Not included in results"
                )
    return drivers_list, errors


###### get data from source files ######
def get_data() -> tuple:
    with (
        open(f"{config.BASE_DIR}/log_data/abbreviations.txt") as drivers,
        open(f"{config.BASE_DIR}/log_data/start.log") as start,
        open(f"{config.BASE_DIR}/log_data/end.log") as end,
    ):
        return (
            drivers.read().splitlines(),
            start.read().splitlines(),
            end.read().splitlines(),
        )


###### get drivers`s position in racing (attribute Drivers.position) ######
def get_racing_position(racing_data: list):
    index_position = 1
    for item in enumerate(racing_data):
        if item[1].error:
            index_position -= 1
        else:
            item[1].position = item[0] + index_position


###### get tuple of lists (1) of racing results/drivers and (2) errors ######
@lru_cache(maxsize=100)
def get_list_info(order: str, attr: str) -> tuple:
    if attr not in ("name", "time"):
        raise ValueError("Wrong value of order attribute")
    else:
        data = get_data()
        drivers_list = get_drivers_list(*data)
        result = sorted(drivers_list[0], key=lambda x: getattr(x, attr))
        get_racing_position(result)
        if order == "asc":
            result = tuple(reversed(result))
        return result, drivers_list[1]


###### get info about driver ######
@lru_cache(maxsize=100)
def get_driver_info(driver_id: str):
    data = get_data()
    results = get_drivers_list(*data)[0]
    result_list = list(filter(lambda el: el.abbr == driver_id, results))
    if result_list:
        return result_list[0]
    else:
        raise ValueError
