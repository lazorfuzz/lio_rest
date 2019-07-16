from flask_restful import Resource, reqparse
from uuid import uuid4
from hashlib import sha256
from database import db
from models import User, AuthToken
from controllers.mainControllers import authenticate

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('Authorization', location='headers')
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('email')
parser.add_argument('role')

class LoginController(Resource):
  # Handle login
  def post(self):
    # Get post arguments
    args = parser.parse_args()
    user = User.query.filter_by(username=args['username']).first()
    # Handle incorrect username or password
    if not user:
      return {'status': 'error', 'message': 'Incorrect username or password.'}, 403
    elif not args['username'] or not args['password']:
        return { 'status': 'error', 'message': 'Invalid user. Please fill in each field!'}, 401
    # Handle login success
    elif user.password == sha256(args['password'].encode()).hexdigest():
      # Delete user's old auth tokens
      old_tokens = AuthToken.query.filter_by(user_id=user.id).all()
      for old_token in old_tokens:
        db.session.delete(old_token)
      token_data = str(uuid4())
      # Create new auth token
      auth_token = AuthToken(user, token_data)
      db.session.add(auth_token)
      db.session.commit()
      return {'token': token_data, 'user': {'username': user.username, 'id': user.id, 'email': user.email, 'role': user.role}}, 200
    else:
      return {'status': 'error', 'message': 'Invalid username or password.'}

class CreateAccountController(Resource):
  # Handle create account
  def post(self):
      args = parser.parse_args()
      # Check if user exists
      user = User.query.filter_by(username=args['username']).first()
      if user:
        return {'status': 'error', 'message': 'User already exists!'}, 401
      if not args['username'] or not args['password'] or not args['email']:
        return {'status': 'error', 'message': 'Please fill in all fields!'}, 401
      # Create user
      new_user = User(args['username'], sha256(args['password'].encode()).hexdigest(), args['email'], args['role'])
      db.session.add(new_user)
      db.session.commit()
      return {'status': 'success'}, 201
class UserList(Resource):
  method_decorators = [authenticate]
  def get(self):
    users = User.query.all()
    users_list = list(map(lambda u: {'id': u.id, 'username': u.username, 'role': u.role}, users))
    return users_list

class UserController(Resource):
  method_decorators = [authenticate]
  def get(self, user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    return {'id': user.id, 'username': user.username, 'role': user.role}
  
  def put(self, user_id):
    args = parser.parse_args()
    token = AuthToken.query.filter_by(data=args['Authorization']).first()
    target_user = User.query.filter_by(id=user_id).first_or_404()
    req_user = User.query.filter_by(id=token.user_id).first()
    # Only allow update if the user is modifying self or is admin
    if int(req_user.id) == int(user_id) or req_user.role == 'admin':
      if args['username']: target_user.username = args['username']
      if args['email']: target_user.email = args['email']
      if args['password']: target_user.email = args['password']
      db.session.commit()
      return {'id': target_user.id, 'username': target_user.username, 'email': target_user.email, 'role': target_user.role}, 200
    return {'status': 'error', 'message': 'You do not have permission to modify this user!'}, 401
  
  def delete(self, user_id):
    args = parser.parse_args()
    token = AuthToken.query.filter_by(data=args['Authorization']).first()
    target_user = User.query.filter_by(id=user_id).first_or_404()
    req_user = User.query.filter_by(id=token.user_id).first()
    # Only allow delete if the user is deleting self, or the user is an admin
    if int(req_user.id) == int(user_id) or req_user.role == 'admin':
      db.session.delete(target_user)
      # Delete the target user's token
      token = AuthToken.query.filter_by(user_id=user_id).first()
      db.session.delete(token)
      db.session.commit()
      return {'status': 'success'}
    return {'status': 'error', 'message': 'You do not have permission to delete this user!'}, 401
