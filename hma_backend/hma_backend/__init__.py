import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from hma_backend.config import config


app = Flask(__name__)
app.config.from_object(config[os.getenv("FLASK_CONFIG", 'default')])
db = SQLAlchemy(app)

from hma_backend.models import *

import hma_backend.views

