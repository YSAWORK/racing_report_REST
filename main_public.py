###### import tools ######
from config_fldr import config
from racing_report.routes import register_resources

###### APP ######
app = config.APP

###### api #######
api = config.API

###### Blueprint ######
blueprint = config.BLUEPRINT

###### add resources ######
register_resources(api, config.VERSION)
app.register_blueprint(blueprint, url_prefix="/api")


if __name__ == "__main__":  # pragma: no cover
    app.run(
        debug=config.debug,
        passthrough_errors=config.passthrough_errors,
        use_debugger=config.use_debugger,
        use_reloader=config.use_reloader,
    )
