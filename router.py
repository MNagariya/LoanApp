from flask import request, jsonify, Blueprint, render_template
from datetime import datetime, timedelta
from db_connection import db 
from models import User,Loan,Repayment
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from service import (get_loan_serive, make_repayment_service, 
                     get_user_loans_service, approve_loan_service, 
                     create_loan_service, create_user_service, login_service)

user_router = Blueprint("USER",__name__)
loan_router = Blueprint("LOAN",__name__)
html_form_router= Blueprint("HTMLFORM", __name__)


@html_form_router.get('create_loan')
def create_loan_form():
    return render_template('loan_form.html')


@html_form_router.get('/my_loans')
def my_loans():
    
    return render_template('customer_loans.html')

@html_form_router.get('/signup')
def sign_up():

    return render_template('signup_form.html')

@html_form_router.get('/login')
def login_page():
    return render_template('login_form.html')

@html_form_router.get('/admin/loans')
def admin_approval():
    return render_template('admin_approval.html')

@user_router.post('/login')
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    response, status_code = login_service(username, password)
    return jsonify(response), status_code

@user_router.post('/token/refresh')
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200

@user_router.post("/create")
def create_user():
    data= request.get_json()

    response, status_code = create_user_service(data)
    return jsonify(response), status_code

@loan_router.post("/create")
@jwt_required()
def create_loan():
    data = request.json
    user_id = get_jwt()['user_id'] 
    amount = int(data.get('amount'))
    term = int(data.get('term'))

    response, status_code = create_loan_service(user_id, amount, term)
    return jsonify(response), status_code


@loan_router.put("/approve/<int:loan_id>") 
@jwt_required()
def approve_loan(loan_id):
    usertype = get_jwt()['usertype']
    response,status_code = approve_loan_service(loan_id,usertype)
    return jsonify(response), status_code


@user_router.get("/loans") 
@jwt_required()
def get_user_loans():
    user_id = get_jwt()['user_id']
    response,status_code = get_user_loans_service(user_id)

    return jsonify(response), status_code

@loan_router.post("/<int:loan_id>/repayments") 
@jwt_required()
def add_repayment(loan_id):
    user_id = get_jwt()['user_id']
    data = request.json
    amount_paid = data.get('amount_paid')

    response,status_code = make_repayment_service(amount_paid, user_id, loan_id)
    return jsonify(response),status_code


@user_router.get("/admin/loans") 
@jwt_required()
def get_loans(): 
    loan_data = get_loan_serive() 
    return jsonify(loan_data)
