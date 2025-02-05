# you can disable/enable features in the config.py file
# or add new features by adding import statements
# e.g. from . import feature_file
from config import FEATURES
from logger import app_logger as logging
logging.info("Loading features...")
if FEATURES.GMAIL:
    logging.info("Loading gmail module...")
    from . import gmail
if FEATURES.WINDOW_TOOLS:
    logging.info("Loading window tools module...")
    from . import window_tools
if FEATURES.BROWSER:
    logging.info("Loading browser module...")
    from . import browser
if FEATURES.WEATHER:
    logging.info("Loading weather module...")
    from . import weather
if FEATURES.GOOGLE:
    logging.info("Loading google module...")
    from . import google_search
if FEATURES.WIKIPEDIA:
    logging.info("Loading wikipedia module...")
    from . import wikipedia
if FEATURES.SHORT_COMMS:
    logging.info("Loading short comms module...")
    from . import short_comm
if FEATURES.PYTHON:
    logging.info("Loading python module...")
    from . import python
if FEATURES.SYSTEM_STATS:
    logging.info("Loading system stats module...")
    from . import system_stats
if FEATURES.INSTAGRAM:
    logging.info("Loading instagram module...")
    from . import instagram
if FEATURES.URL_SHORTENER:
    logging.info("Loading url shortener module...")
    from . import url_shortner
if FEATURES.LLM_WORKFLOW:
    logging.info("Loading llm workflow module...")
    from . import llm_workflow

logging.info("Features loaded successfully!")