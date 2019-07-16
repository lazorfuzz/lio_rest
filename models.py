from database import db

class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(240), unique=True, nullable=False)

    def __init__(self, url):
        self.url = url;
    
    def __repr__(self):
        return '<Meme %r' % self.url

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(80))

    def __init__(self, username, password, email, role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return '<User %r>' % self.username

class AuthToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    data = db.Column(db.String(64), unique=True, nullable=False)

    def __init__(self, user, data):
        self.user_id = user.id
        self.data = data
    
    def __repr__(self):
        return '<AuthToken %r>' % self.data

if __name__ == '__main__':
    db.create_all()
    db.session.commit()
