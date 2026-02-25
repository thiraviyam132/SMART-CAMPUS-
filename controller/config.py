app = flask (__name__)
app.config['SECRET_KEY'] = 'smartcampus_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False