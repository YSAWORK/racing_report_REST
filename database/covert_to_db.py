###### import tools #######
from peewee import DoesNotExist
from database.models import Driver, Racing, Error
from config_fldr import config
import datetime
from config_fldr.config import DATABASE


###### check tables in data base ######
def check_databases_exists():
    if not Driver.table_exists():
        DATABASE.create_tables([Driver])
    if not Racing.table_exists():
        DATABASE.create_tables([Racing])
    if not Error.table_exists():
        DATABASE.create_tables([Error])


###### create Drivers database ######
def create_drivers_database(file):
    global errors_list
    drivers_info = (
        open(f"{config.BASE_DIR}/database/log_data/{file}").read().splitlines()
    )
    if type(drivers_info) != list:
        raise TypeError
    else:
        for num, item in enumerate(drivers_info):
            split_driver_data = item.split("_")
            if item in ("", " ", "_", None):
                continue
            elif len(split_driver_data) != 3:
                errors_list.append(
                    (
                        f"{item} not included in results -- wrong data format in line {num + 1} of resource file.",
                        "wrong format of drivers`s data",
                    ),
                )
            else:
                driver, created = Driver.get_or_create(
                    abbr=split_driver_data[0],
                    name=split_driver_data[1],
                    team=split_driver_data[2],
                )
                driver.save()


###### create start_time & end_time in Racings database ######
def create_racing_database(file, field: str):
    global errors_list
    time_info = open(f"{config.BASE_DIR}/database/log_data/{file}").read().splitlines()
    if type(time_info) != list:
        raise TypeError
    else:
        for item in enumerate(time_info):
            if item[1] in ("", " ", "_", None):
                continue
            elif not item[1][:3].isalpha() or len(item[1][3:]) != 23:
                errors_list.append(
                    (
                        f"{item[1]} not included in results -- wrong data format in line {item[0] + 1} of resource file.",
                        "wrong format of racing`s data",
                    ),
                )
            else:
                if field == "start":
                    try:
                        time_data = Racing.get(abbr=item[1][:3])
                    except DoesNotExist:
                        time_data = Racing(abbr=item[1][:3])
                    time_data.start_time = datetime.datetime.fromisoformat(
                        item[1][3:].replace("_", "T").strip()
                    )
                    try:
                        time_data.driver_id = Driver.get(abbr=item[1][:3])
                    except DoesNotExist:
                        time_data.driver_id = None
                    time_data.save()
                elif field == "end":
                    time_data = Racing.get(abbr=item[1][:3])
                    time_data.end_time = datetime.datetime.fromisoformat(
                        item[1][3:].replace("_", "T").strip()
                    )
                    time_data.save()
                    time_data.save()
                else:
                    raise ValueError


###### create time in Racings database ######
def create_time_in_racing_database():
    for item in Racing.select():
        time = item.end_time - item.start_time
        item.time = float(time.total_seconds())
        if item.time >= 0:
            item.relevant_time = True
        else:
            item.relevant_time = False
        item.save()


###### check drivers racing info ######
def check_results_exist():
    global errors_list
    for race in Racing.select().where(Racing.driver_id.is_null(True)):
        errors_list.append(
            (f"{race.abbr} hasn`t enough data. Not included in results", "no driver"),
        )


###### get drivers position in racing ######
def get_position():
    for i, race in enumerate(
        Racing.select()
        .where((Racing.relevant_time == True) & (Racing.driver_id.is_null(False)))
        .order_by(Racing.time)
    ):
        race.position = i + 1
        race.save()


###### create Errors database ######
def create_errors_database():
    global errors_list
    for error in errors_list:
        error_item, created = Error.get_or_create(
            general_error=error[0], error_type=error[1]
        )
        error_item.save()


##### create error list ######
errors_list = list()


if __name__ == "__main__":
    drivers_log = "abbreviations.txt"
    start_log = "start.log"
    end_log = "end.log"
    check_databases_exists()
    create_drivers_database(drivers_log)
    create_racing_database(start_log, "start")
    create_racing_database(end_log, "end")
    create_time_in_racing_database()
    check_results_exist()
    get_position()
    create_errors_database()
    if not DATABASE.is_closed():
        DATABASE.close()
