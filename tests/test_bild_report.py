###### import tools ######
import datetime, pytest
from config_fldr import config
import racing_report as code


####### test func get_data ######
def test_get_data():
    with (
        open(f"{config.BASE_DIR}/log_data/abbreviations.txt") as drivers,
        open(f"{config.BASE_DIR}/log_data/start.log") as start,
        open(f"{config.BASE_DIR}/log_data/end.log") as end,
    ):
        assert code.get_data() == (
            drivers.read().splitlines(),
            start.read().splitlines(),
            end.read().splitlines(),
        )


###### test func get_datetime_info #######
@pytest.mark.parametrize(
    "time_info, errors, result",
    [
        (
            [
                "SVF2018-05-24_12:02:58.917",
                "NHR2018-05-24_12:02:49.914",
                "FAM 2018-05-24_12:13:04.512",  # fail (add to errors)
                "",
            ],  # fail (ignore)
            {},
            (
                (
                    {
                        "SVF": datetime.datetime.fromisoformat(
                            "2018-05-24T12:02:58.917"
                        ),
                        "NHR": datetime.datetime.fromisoformat(
                            "2018-05-24T12:02:49.914"
                        ),
                    }
                ),
                {
                    "FAM": "FAM 2018-05-24_12:13:04.512 not included in results -- wrong data format in line 3 of resource file."
                },
            ),
        ),
    ],
)
def test_get_datetime_info(time_info, errors, result):
    assert code.get_datetime_info(time_info, errors) == result


###### test func get_datetime_info ######
@pytest.mark.parametrize(
    "time_info, errors",
    [
        (
            ("SVF2018-05-24_12:02:58.917",),
            {},
        ),
        (
            123,
            {},
        ),
        (
            {
                "SVF": "2018-05-24_12:02:58.917",
            },
            {},
        ),
    ],
)
def test_get_datetime_info_fail_type(time_info, errors):
    with pytest.raises(TypeError):
        code.get_datetime_info(time_info, errors)


###### test func get_drivers_list ######
@pytest.mark.parametrize(
    "drivers_info, start_data, end_data, drivers_data, error_list",
    [
        (
            [
                "SVF_Sebastian Vettel_FERRARI",
                "DRR_Daniel Ricciardo_RED BULL RACING TAG HEUER",
                "BRT_Brendon Hartley_SCUDERIA TORO ROSSO HONDA",
                " ",
                "FAM 2018-05-24_12:13:04.512",
            ],
            [
                "SVF2018-05-24_12:02:58.917",
                "DRR2018-05-24_12:14:12.054",
                "BHS2018-05-24_12:14:51.985",
            ],
            [
                "SVF2018-05-24_12:04:03.332",
                "DRR2018-05-24_12:11:24.067",
                "BHS2018-05-24_12:16:05.164",
            ],
            [
                (
                    "SVF",
                    "Sebastian Vettel",
                    "FERRARI",
                    {
                        "SVF": (
                            datetime.datetime.fromisoformat("2018-05-24T12:02:58.917"),
                            datetime.datetime.fromisoformat("2018-05-24T12:04:03.332"),
                        )
                    },
                ),
                (
                    "DRR",
                    "Daniel Ricciardo",
                    "RED BULL RACING TAG HEUER",
                    {
                        "DRR": (
                            datetime.datetime.fromisoformat("2018-05-24T12:14:12.054"),
                            datetime.datetime.fromisoformat("2018-05-24T12:11:24.067"),
                        )
                    },
                ),
            ],
            {
                "BRT": "Brendon Hartley (BRT) hasn`t enough data. Not included in results",
                "FAM_2018-05-24_12:13:04.512": "FAM 2018-05-24_12:13:04.512 not included in results -- wrong data format in line 5 of resource file.",
            },
        ),
    ],
)
def test_get_drivers_list(drivers_info, start_data, end_data, drivers_data, error_list):
    drivers_list = []
    for data in drivers_data:
        object_t = code.Drivers()
        object_t.abbr = data[0]
        object_t.name = data[1]
        object_t.team = data[2]
        object_t.start_time = data[3][data[0][:3]][0]
        object_t.end_time = data[3][data[0][:3]][1]
        object_t.time = object_t.end_time - object_t.start_time
        if int(object_t.time.total_seconds()) < 0:
            object_t.error = "incorrect data"
        drivers_list.append(object_t)
    assert [
        (d.name, d.abbr, d.team, d.start_time, d.end_time, d.time)
        for d in code.get_drivers_list(drivers_info, start_data, end_data)[0]
    ] == [
        (d.name, d.abbr, d.team, d.start_time, d.end_time, d.time) for d in drivers_list
    ]


###### test func get_list_info (fail case) ######
@pytest.mark.parametrize("attr", ["game", 4, ("name",), ""])
def test_get_list_info_fail_value(attr):
    with pytest.raises(ValueError):
        code.get_list_info("desc", attr)
