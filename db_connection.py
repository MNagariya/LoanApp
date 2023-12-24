from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def db_connection(app):
    db.init_app(app)
    migrate = Migrate(app, db)
