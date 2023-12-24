from router import loan_router, user_router, html_form_router
from flask_sqlalchemy import SQLAlchemy

def register_blueprints(app):
    app.register_blueprint(user_router, url_prefix="/user")
    app.register_blueprint(loan_router, url_prefix="/loan")
    app.register_blueprint(html_form_router, url_prefix="/")

