from flaskblog import db, login_manager
from datetime import datetime, timedelta
from flask_login import UserMixin
import app
import jwt


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    post = db.relationship("Post", backref="author", lazy=True)

    def get_rest_token(self, expires_sec=1800):
        payload = {
            "user_id": self.id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_sec),
        }
        token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
        return token.decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except (jwt.InvalidTokenError, KeyError):
            return None  # Invalid token or missing user_id
        return User.query.get(user_id)

    def __repr__(self):
        return f"{self.username}"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    def __repr__(self):
        return f"{self.title}"
