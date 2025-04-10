###### import tools ######
from config_fldr import config
from flasgger import Swagger
from flask import Flask, Blueprint
from flask_restful import Api
from racing_report.request_main import Report, Drivers, AloneDriver


###### create Blueprint ######
blueprint = Blueprint("api", __name__)


###### create api #######
api = Api(blueprint, default_mediatype="application/json")


###### add resources ######
api.add_resource(Report, f"/{config.version}/report")
api.add_resource(Drivers, f"/{config.version}/drivers")
api.add_resource(AloneDriver, f"/{config.version}/drivers/<driver_id>")


###### create APP with template and static folders ######
app = Flask(
    __name__,
    template_folder=f"{config.BASE_DIR}/templates",
    static_folder=f"{config.BASE_DIR}/static",
)
app.register_blueprint(blueprint, url_prefix="/api")


###### create swagger ######
swagger = Swagger(
    app, template_file=f"{config.BASE_DIR}/config_fldr/swagger_config.yml"
)


if __name__ == "__main__":  # pragma: no cover
    app.run(
        debug=config.debug,
        passthrough_errors=config.passthrough_errors,
        use_debugger=config.use_debugger,
        use_reloader=config.use_reloader,
    )
