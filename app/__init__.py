from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'F34TF$($e34D'
app.config.from_object('config')
db = SQLAlchemy(app)

from models import *
