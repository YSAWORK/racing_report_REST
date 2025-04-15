###### import tools ######
from peewee import *
from config_fldr.config import DATABASE


###### create base model with database ######
class BaseModel(Model):
    class Meta:
        database = DATABASE


###### CLASSES ######
# ----- create class Drivers ------#
class Driver(BaseModel):
    name = CharField()
    abbr = CharField()
    team = CharField()


# ----- create class Racings -----#
class Racing(BaseModel):
    driver_id = ForeignKeyField(Driver, backref="races", null=True)
    abbr = CharField()
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    time = DateTimeField(null=True)
    position = IntegerField(null=True)
    relevant_time = BooleanField(null=True)


##---- create classErrors -----#
class Error(BaseModel):
    error_type = CharField()
    general_error = CharField()
