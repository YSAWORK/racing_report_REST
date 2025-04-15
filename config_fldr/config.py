###### import tools ######
import os, sys
from peewee import SqliteDatabase
from flask import Flask, Blueprint
from flask_restful import Api
from flasgger import Swagger

###### API version ######
VERSION = "v1"

###### base APP dir ######
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")

###### database ######
DATABASE = SqliteDatabase(f"{BASE_DIR}/database/monaco_racing.db")

###### create APP with template and static folders #####
APP = Flask(
    __name__,
    template_folder=f"{BASE_DIR}/templates",
    static_folder=f"{BASE_DIR}/static",
)

###### create Blueprint ######
BLUEPRINT = Blueprint("api", __name__)

###### create Api ######
API = Api(BLUEPRINT, default_mediatype="application/json")

###### create swagger ######
SWAGGER = Swagger(APP, template_file=f"{BASE_DIR}/config_fldr/swagger_config.yml")

###### key paths config #######
sys.path.append("racing_report")
sys.path.append("config")

####### app debug config #######
debug = True
passthrough_errors = True
use_debugger = False
use_reloader = False
