from db_connection import db 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    usertype = db.Column(db.String(20), default='customer')
    loans = db.relationship('Loan', backref='user', lazy=True)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    term = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    repayments = db.relationship('Repayment', backref='loan', lazy=True)

class Repayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=False)


