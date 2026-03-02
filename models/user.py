from database import db
from flask_login import UserMixin

# modelo de usuario
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    
    def to_dict(self):
        return {"id": self.id, "username": self.username, "role": self.role}
