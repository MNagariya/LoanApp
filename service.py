from models import User, Loan, Repayment
from db_connection import db 
from http import HTTPStatus
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token

def get_loan_serive():
    """
    This function will return all the pending loans which admin can approve. 
    """
    response = db.session.query(Loan.id, Loan.amount, Loan.term, 
                                User.username).join(User, User.id == Loan.user_id).filter(Loan.status == "PENDING").all()
    loan_data = []
    for loan_id, amount, term, username in response:
        loan_data.append({
            'loan_id': loan_id,
            'person_name':username,
            'amount': amount,
            'term': term
        })
    return loan_data

def make_repayment_service(amount_paid, user_id, loan_id):
    """
    This function make repayments.
    It throws error if the paying amount is less than repayment amount.
    It adjusts the remaining repayments if the paying amount is greater than the repayment amount.
    """
    user = db.session.query(User).filter(User.id == user_id)
    loan = db.session.query(Loan).filter(Loan.id==loan_id, 
                                         Loan.user_id == user_id , Loan.status== "APPROVED").first()

    if not user or not loan:
        return {'error': 'User or Loan not found or loan is not approved'}, HTTPStatus.NOT_FOUND.value

    
    next_repayment = Repayment.query.filter(Repayment.loan_id==loan_id, 
                                            Repayment.status== "PENDING").order_by(Repayment.due_date).first()

    if not next_repayment:
        return {'error': 'No pending repayments for this loan'}, HTTPStatus.BAD_REQUEST.value

    if amount_paid < next_repayment.amount: 
        return {'error': 'Amount paid is less than the pending repayment amount'}, HTTPStatus.BAD_REQUEST.value
    
    refundable_amount = None 

    if amount_paid > next_repayment.amount:
        total_amount= amount_paid - next_repayment.amount 
        repay_objs= Repayment.query.filter(Repayment.loan_id==loan_id , Repayment.status== "PENDING").all()
        if len(repay_objs) > 1:
            diff_amount= total_amount/(len(repay_objs)-1)
        else:
            refundable_amount =  amount_paid - next_repayment.amount 
        for repay_obj in repay_objs:
            if  next_repayment.id != repay_obj.id:
                if repay_obj.amount < diff_amount:
                    exceed_amount = diff_amount - repay_obj.amount
                    refundable_amount = exceed_amount * (len(repay_objs) - 1)
                    repay_obj.status= 'PAID'
                elif repay_obj.amount == diff_amount:
                    repay_obj.status = 'PAID'
                else:
                    repay_obj.amount = round(repay_obj.amount,2) -round(diff_amount,2)

    next_repayment.status = 'PAID'
    db.session.commit()


    if all(repayment.status == 'PAID' for repayment in loan.repayments):
        loan.status = 'PAID'
        db.session.commit()
    
    response = dict(message = 'Repayment added successfully.')
    if refundable_amount:
        response['message'] = response['message']+ f'\nyour repayment amount exceeding the pending amount. \
            \nPlease collect INR {round(refundable_amount,1)} from counter'
    return response, HTTPStatus.OK.value


def get_user_loans_service(user_id):
    """
    This function returns all the applied loans of a user. 
    """
    user = User.query.get(user_id)

    if not user:
        return {'error': 'User not found'}, HTTPStatus.NOT_FOUND.value

    loans = Loan.query.filter_by(user=user).all()

    loan_data = []
    for loan in loans:
        repayments = Repayment.query.filter_by(loan=loan).all()
        loan_data.append({
            'loan_id': loan.id,
            'amount': loan.amount,
            'term': loan.term,
            'status': loan.status,
            'repayments': [{'amount': round(r.amount,2), 
                            'due_date': str(r.due_date), 'status': r.status} for r in repayments]
        })
    return {'loans': loan_data}, HTTPStatus.OK.value

def approve_loan_service(loan_id, usertype):
    """
    This function approves given loan. 
    It also make sure the approver is an admin. 
    """
    if usertype!='admin':
        return {'error': 'unauthoried access'}, HTTPStatus.UNAUTHORIZED.value

    loan = db.session.query(Loan).filter(Loan.id == loan_id).first()

    if not loan:
        return {'error': 'Loan not found'}, HTTPStatus.NOT_FOUND.value

    loan.status = 'APPROVED'
    db.session.commit()

    return {'message': 'Loan approved successfully'}, HTTPStatus.OK.value

def create_loan_service(user_id, amount, term):
    """
    This function create loans. 
    """
    user = db.session.query(User).filter(User.id == user_id).first()

    if not user:
        return {'error': 'User not found'}, HTTPStatus.NOT_FOUND.value

    loan = Loan(amount=amount, term=term, user_id=user.id)
    db.session.add(loan)

 
    today = datetime.now().date()
    for i in range(1, term + 1):
        due_date = today + timedelta(weeks=i)
        repayment = Repayment(amount=amount / term, due_date=due_date, loan=loan)
        db.session.add(repayment)

    db.session.commit()

    return {'message': f'Loan created successfully. Loan id: {loan.id}'}, HTTPStatus.CREATED.value

def create_user_service(data):
    """
    This function creates new user account.
    """
    if not data.get('usertype') or not data.get('password') or not data.get('username'):
        return {'error': 'username or id or password or usertype is missing'}, HTTPStatus.BAD_REQUEST.value
    
    user=User(username= data["username"], password= data["password"], usertype=data["usertype"])
    db.session.add(user)
    db.session.commit()
    return {"message": f"Account created successfully. User ID: {user.id}"}, HTTPStatus.OK.value 

def login_service(username, password):
    user = db.session.query(User).filter(User.username==username and User.password == password).first()

    if not user:
        return {'error': 'Invalid credentials'}, HTTPStatus.UNAUTHORIZED.value
    
    access_token = create_access_token(identity=username, additional_claims={'user_id': 
                                                                             user.id, 'usertype': user.usertype})
    refresh_token = create_refresh_token(identity=username, additional_claims={'user_id': 
                                                                               user.id, 'usertype': user.usertype})
    return dict(access_token=access_token, refresh_token=refresh_token, user_type= user.usertype), HTTPStatus.OK.value