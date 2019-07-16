from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import json
from controllers import mainControllers
from database import db
from models import Meme

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/db/leonflix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
CORS(app)
db.init_app(app)
# db.drop_all(app=app)
db.create_all(app=app)
api = Api(app)

api.add_resource(mainControllers.MemeController, '/memes')
api.add_resource(mainControllers.RandomMemeController, '/memes/random')
api.add_resource(mainControllers.NewsController, '/news/<news_keyword>')

def populate_db():
  with open('memes.json', 'r') as f:
    with app.app_context():
      memes = json.loads(f.read())
      for meme in memes:
        try:
          db.session.add(Meme(url=meme['url']))
          db.session.commit()
        except: pass

populate_db()

if __name__ == '__main__':
    app.run(debug=True)
