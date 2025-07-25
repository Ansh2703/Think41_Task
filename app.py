# app.py

from flask import Flask
from models import db
from routes import api_blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(api_blueprint)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
