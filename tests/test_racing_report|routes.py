###### import tools ######
import pytest
from flask import Flask
from flask_restful import Api
from racing_report.routes import register_resources
from database.models import Driver, Racing, Error
from peewee import SqliteDatabase


###### create test app & database ######
@pytest.fixture
def test_app(monkeypatch):
    test_db = SqliteDatabase(":memory:")
    monkeypatch.setattr("config_fldr.config.DATABASE", test_db)
    test_db.bind([Driver, Racing, Error])
    test_db.connect()
    test_db.create_tables([Driver, Racing, Error])

    app = Flask(__name__)
    blueprint = __import__("flask").Blueprint("api", __name__)
    api = Api(blueprint)
    register_resources(api, "v1")
    app.register_blueprint(blueprint, url_prefix="/api")
    app.config["TESTING"] = True

    client = app.test_client()
    yield client

    test_db.drop_tables([Driver, Racing, Error])
    test_db.close()


###### test report route ######
def test_report_endpoint(test_app):
    response = test_app.get("/api/v1/report?format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


###### test drivers route ######
def test_drivers_endpoint(test_app):
    response = test_app.get("/api/v1/drivers")
    assert response.status_code == 200
    assert response.content_type == "application/json"


###### test drivers route with driver ID ######
def test_alone_driver_endpoint(test_app):
    response = test_app.get("/api/v1/drivers/DRR")
    assert response.status_code in [200]
