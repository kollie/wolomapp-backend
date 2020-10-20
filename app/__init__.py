from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager
from flask_cors import CORS
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
oauth = OAuth(app)
login = LoginManager(app)
login.login_view = 'login'
CORS(app)



from app import routes, models, tokens, api
