###### registrate resources ######
def register_resources(api, version):
    from racing_report.request_main import Report, Drivers, AloneDriver

    api.add_resource(Report, f"/{version}/report", endpoint="v1_report")
    api.add_resource(Drivers, f"/{version}/drivers", endpoint="v1_drivers")
    api.add_resource(
        AloneDriver, f"/{version}/drivers/<driver_id>", endpoint="v1_alone_driver"
    )
