# test_app.py

import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data  # Check for HTML structure
    assert b"<title>Home</title>" in response.data  # Check for the title tag
    assert b"Welcome to the Flask App" in response.data  # Updated specific content




def test_login(client):
    response = client.post('/login', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data  # Check for HTML structure
    assert b"<title>Login</title>" in response.data  # Check for the title tag
    assert b"Logged in successfully" in response.data  # Updated specific content




def test_invalid_login(client):
    response = client.post('/login', data=dict(
        username='invalid_user',
        password='invalid_password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


# Add more tests as needed




