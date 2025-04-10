###### import tools ######
import os, sys


###### API version ######
version = "v1"


###### base APP dir ######
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")


###### key paths config #######
sys.path.append("racing_report")
sys.path.append("config")


####### app debug config #######
debug = True
passthrough_errors = True
use_debugger = False
use_reloader = False
