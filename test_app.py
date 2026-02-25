"""Minimal test of Flask app"""
from flask import Flask
from database import db
from models import User, Issue

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/test')
def test():
    return 'Hello'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
