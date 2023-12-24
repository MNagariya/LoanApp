import pytest
from app import app
from db_connection import db 
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from unittest.mock import patch
from models import User, Loan
from unittest.mock import Mock, create_autospec


@pytest.fixture
def client(mocker):
    app.config['TESTING'] = True
    client = app.test_client()
    mocker.patch('router.db.session.query', return_value=mocker.Mock())

    yield client

def test_login(client, mocker):
    mocked_query = mocker.patch('router.db.session.query')
    mocked_user = User(username="testuser", password="testpassword", usertype="customer")
    mocked_query.return_value.filter.return_value.first.return_value = mocked_user

    # Test login with correct credentials
    response = client.post('/user/login', json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json
    assert "refresh_token" in response.json
    assert response.json["user_type"] == "customer"

    # Test login with incorrect credentials
    mocked_query.return_value.filter.return_value.first.return_value = None  
    response = client.post('/user/login', json={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "error" in response.json
    assert response.json["error"] == "Invalid credentials"


def test_user_create_with_correct_details(client, mocker):
    mocker.patch('router.db.session.add')
    mocker.patch('router.db.session.commit')
    response = client.post('/user/create', json={"username": "testuser", "password": "testpassword", "usertype": "custoemr"})
    assert response.status_code == 200
    assert "message" in response.json

def test_user_create_with_incorrect_details(client):
    response = client.post('/user/create', json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 400
    assert "error" in response.json

@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.decode_token')
def test_loan_create_with_correct_details(mock_decode_token, mock_verify_jwt, client, mocker):
    mock_decode_token.return_value = {'sub': 'username'}
    mock_verify_jwt.return_value = True
    mocker.patch('router.db.session.add')
    mocker.patch('router.jwt_required')
    mocked_query = mocker.patch('router.db.session.query')
    mocked_user = User(username="testuser", password="testpassword", usertype="customer")
    mocked_query.return_value.filter.return_value.first.return_value = mocked_user
    mocker.patch("router.get_jwt").return_value={'user_id': 1}
    mocker.patch('router.db.session.commit')
    response = client.post('/loan/create', json={"amount": 40000, "term": 2})
    assert response.status_code == 201
    assert "message" in response.json



@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.decode_token')
def test_loan_create_with_incorrect_details(mock_decode_token, mock_verify_jwt, client, mocker):
    mock_decode_token.return_value = {'sub': 'username'}
    mock_verify_jwt.return_value = True
    mocked_query = mocker.patch('router.db.session.query')
    mocked_query.return_value.filter.return_value.first.return_value = None
    mocker.patch("router.get_jwt").return_value={'user_id': 1}
    response = client.post('/loan/create', json={"amount": 40000, "term": 2})
    assert response.status_code == 404
    assert "error" in response.json

@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.decode_token')
def test_approve_loan(mock_decode_token, mock_verify_jwt, client, mocker):
    mock_decode_token.return_value = {'sub': 'username'}
    mock_verify_jwt.return_value = True
    mocker.patch("router.get_jwt").return_value={'usertype': 'admin'}
    mocked_query = mocker.patch('router.db.session.query')
    mocker.patch('router.db.session.commit')
    mocker.patch('router.db.session.add')
    mocked_loan = Loan(id=1, amount=4000, term=3, user_id= 1)
    mocked_query.return_value.filter.return_value.first.return_value = mocked_loan
    response = client.put('/loan/approve/2')
    assert response.status_code == 200

@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.decode_token')
def test_approve_loan_with_incorrect_detail(mock_decode_token, mock_verify_jwt, client, mocker):
    mock_decode_token.return_value = {'sub': 'username'}
    mock_verify_jwt.return_value = True
    mocker.patch("router.get_jwt").return_value={'usertype': 'admin'}
    mocked_query = mocker.patch('router.db.session.query')
    mocker.patch('router.db.session.commit')
    mocker.patch('router.db.session.add')
    mocked_query.return_value.filter.return_value.first.return_value = None
    response = client.put('/loan/approve/2')
    assert response.status_code == 404


@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.decode_token')
def test_approve_loan_when_user_not_admin(mock_decode_token, mock_verify_jwt, client, mocker):
    mock_decode_token.return_value = {'sub': 'username'}
    mock_verify_jwt.return_value = True
    mocker.patch("router.get_jwt").return_value={'usertype': 'customer'}
    mocked_query = mocker.patch('router.db.session.query')
    mocker.patch('router.db.session.commit')
    mocker.patch('router.db.session.add')
    mocked_query.return_value.filter.return_value.first.return_value = None
    response = client.put('/loan/approve/2')
    assert response.status_code == 401