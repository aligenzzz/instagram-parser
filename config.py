import os
from dotenv import load_dotenv
from constants import CHROMEDRIVER_PATH, HOST, PORT

load_dotenv()

HOST = os.getenv('FLASK_RUN_HOST', HOST)
PORT = int(os.getenv('FLASK_RUN_PORT', PORT))

CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', CHROMEDRIVER_PATH)
