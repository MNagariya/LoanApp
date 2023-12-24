from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dependencies import register_blueprints
from db_connection import db_connection 
from datetime import timedelta
import os 
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "/.env"))

app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)  
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(minutes=120)    
app.config['JWT_ALGORITHM'] = 'HS256'
jwt = JWTManager(app)

register_blueprints(app)
db_connection(app)


if __name__ == "__main__":
    app.run(debug=True) 