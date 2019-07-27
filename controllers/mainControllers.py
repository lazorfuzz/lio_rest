from flask_restful import Resource, reqparse
from database import db
from models import Meme, User, AuthToken
from functools import wraps
from bs4 import BeautifulSoup
from urllib.request import urlopen
import traceback
import random
import json

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('url')
parser.add_argument('meme_auth')
parser.add_argument('temp')
parser.add_argument('user_id')
parser.add_argument('news_keyword')
parser.add_argument('X-Authorization', location='headers')

def this_user():
  token = AuthToken.query.filter_by(data=parser.parse_args()['X-Authorization']).first()
  user = User.query.filter_by(id=token.user_id).first()
  return user

def generic_400(message='Could not understand request'):
  return {'message': message}, 400

def authenticate(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    if not getattr(func, 'authenticated', True):
      return func(*args, **kwargs)
    token = parser.parse_args()['X-Authorization']
    auth_token = AuthToken.query.filter_by(data=token).first()
    if auth_token:
      return func(*args, **kwargs)
    return {'status': 'error', 'message': 'Invalid auth token.'}, 403
  return wrapper

class MemeController(Resource):
  def get(self):
    memes = Meme.query.all()
    memes_list = list(map(lambda m: { 'url': m.url, 'id': m.id, 'temp': m.temp }, memes))
    return memes_list
  
  def post(self):
    try:
      args = parser.parse_args()
      auth = args['meme_auth']
      temp = args['temp'] is '1' or args['temp'] is None
      if auth != 'certifiedmemer':
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
    memes = Meme.query.all()
    meme = memes[random.randint(0, len(memes) - 1)]
    data = {'url': meme.url, 'id': meme.id}
    temp_memes = Meme.query.filter_by(temp=True).all()
    if len(temp_memes) > 200:
      for m in temp_memes[:180]:
        db.session.delete(m)
      db.session.commit()
    return data

class NewsController(Resource):
  def get(self, news_keyword):
    try:
      news_url='https://news.google.com/news/rss/search?q=%s' % news_keyword
      with urlopen(news_url) as client:
        xml_page = client.read()
      page=BeautifulSoup(xml_page, 'xml')
      news_list=page.findAll('item')
      return list(map(lambda n: {'title': n.title.text, 'link': n.link.text, 'date': n.pubDate.text}, news_list))
    except:
      return {'status': 'error', 'message': 'News not found!'}, 404
