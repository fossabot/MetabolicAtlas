from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from hma_backend.config import DefaultSettings

app = Flask(__name__)
app.config.from_object(DefaultSettings)
db = SQLAlchemy(app)

from hma_backend.models import *

import hma_backend.views

