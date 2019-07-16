# gameofde_rest
Flask Rest API for Capstone project.

## Getting Started
```
pip3 install -r requirements.txt
python3 api.py
```

## Test Commands
Using [httpie](https://httpie.org/)
```python
# Getting organizations list:
http GET http://127.0.0.1:5000/orgs
# Creating a user:
http POST http://127.0.0.1:5000/create_account username="USERNAME" password="PASSWORD" email="EMAIL" role="admin"
# Logging in:
http POST http://127.0.0.1:5000/login username="USERNAME" password="PASSWORD"
# Submitting a cipher:
http POST http://127.0.0.1:5000/caesar 'Authorization:AUTH_TOKEN_HERE' cipher='hello' lang='en'
# Getting a specific organization:
http GET http://127.0.0.1:5000/orgs/NSA 'Authorization:AUTH_TOKEN_HERE'
# Creating a new organization:
http POST http://127.0.0.1:5000/orgs/GCHQ 'Authorization:AUTH_TOKEN_HERE'

```
# lio_rest
