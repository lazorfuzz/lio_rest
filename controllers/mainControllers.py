from flask_restful import Resource, reqparse
from database import db
from secrets import auth_key
from models import Meme, User
from functools import wraps
from bs4 import BeautifulSoup
from urllib.request import urlopen
import traceback
import random
import json
import hmac
from hashlib import sha256
from base64 import b64decode, b64encode
from datetime import datetime

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('url')
parser.add_argument('meme_auth')
parser.add_argument('temp')
parser.add_argument('user_id')
parser.add_argument('news_keyword')
parser.add_argument('X-Authorization', location='headers')

def generate_token(user):
  """Generates a JWT-like auth token
  
  Arguments:
      user {User} -- A SequelAlchemy user object
  
  Returns:
      str -- The token
  """
  data = {'id': user.id, 'username': user.username, 'role': user.role, 'org_id': user.org_id, 'created': str(datetime.now())}
  # Serialize user data to JSON, then encode to base64
  b64_data = b64encode(json.dumps(data).encode())
  # Generate a signature with SHA256, then encode to base64
  dig = hmac.new(secret.encode(), msg=b64_data, digestmod=sha256).digest()
  signature = b64encode(dig)
  # Return the token in the format: {user_data}.{signature}
  return '%s.%s' % (b64_data.decode(), signature.decode())


def read_token(token):
  """Validates the token payload with the signature, and returns 
  a dict containing the user data in the payload
  
  Arguments:
      token {str} -- The token passed in the HTTP header
  
  Returns:
      dict -- The decoded user data
  """
  try:
    token = token.split('.')
    payload = token[0].encode()
    # Hash the payload and get the signature
    dig = hmac.new(secret.encode(), msg=payload, digestmod=sha256).digest()
    signature = b64encode(dig)
    # If the signature matches the one provided, return the user data
    if signature.decode() == token[1]:
      data = b64decode(payload).decode()
      user_data = json.loads(data)
      return user_data
    return None
  except: return None

def this_user():
  """Gets the current user's info from token
  
  Returns:
      dict -- The user's data
  """
  token = parser.parse_args()['Authorization']
  user = read_token(token)
  return user

def generic_400(message='Could not understand request'):
  return {'message': message}, 400

def authenticate(func):
  """A decorator method that checks that the user's auth token is valid
  
  Arguments:
      func {func} -- The target method
  
  Returns:
      func -- The target method
  """
  @wraps(func)
  def wrapper(*args, **kwargs):
    if not getattr(func, 'authenticated', True):
      return func(*args, **kwargs)
    token = parser.parse_args()['Authorization']
    user = read_token(token)
    if user != None:
      return func(*args, **kwargs)
    return {'message': 'Invalid auth token.'}, 403
  return wrapper

class MemeController(Resource):
  def get(self):
    """Handles GET request for /memes endpoint
    
    Returns:
        list -- A list of memes
    """
    memes = Meme.query.all()
    memes_list = list(map(lambda m: { 'url': m.url, 'id': m.id, 'temp': m.temp }, memes))
    return memes_list
  
  def post(self):
    """Handles POST requests for /memes endpoint
    
    Returns:
        dict -- Status or error message
    """
    try:
      args = parser.parse_args()
      auth = args['meme_auth']
      temp = args['temp'] is '1' or args['temp'] is None
      if auth != auth_key:
        return {'message': 'Bad meme authentication'}, 401
      meme_url = args['url']
      existing = Meme.query.filter_by(url=meme_url).first()
      if not existing:
        meme = Meme(url=meme_url, temp=temp)
        db.session.add(meme)
        db.session.commit()
        return {'status': 'success'}
      return {'message': 'Meme already exists!'}, 401
    except Exception as e:
      traceback.print_exc()
      return generic_400(e)


class RandomMemeController(Resource):
  def get(self):
    """Handles GET request for /memes/random endpoint
    
    Returns:
        dict -- A random meme
    """
    memes = Meme.query.all()
    meme = memes[random.randint(0, len(memes) - 1)]
    data = {'url': meme.url, 'id': meme.id}
    temp_memes = Meme.query.filter_by(temp=True).all()
    if len(temp_memes) > 300:
      for m in temp_memes[:250]:
        db.session.delete(m)
      db.session.commit()
    return data

class NewsController(Resource):
  def get(self, news_keyword):
    """Handles GET requests for /news/<news_keyword> endpoint
    
    Arguments:
        news_keyword {str} -- The query to search for
    
    Returns:
        list -- A list of news items
    """
    try:
      news_url='https://news.google.com/news/rss/search?q=%s' % news_keyword
      with urlopen(news_url) as client:
        xml_page = client.read()
      page=BeautifulSoup(xml_page, 'xml')
      news_list=page.findAll('item')
      return list(map(lambda n: {'title': n.title.text, 'link': n.link.text, 'date': n.pubDate.text}, news_list))
    except:
      return {'status': 'error', 'message': 'News not found!'}, 404
