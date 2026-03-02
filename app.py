import os
import bcrypt
from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/flask-crud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
db.init_app(app) # conecta ao banco de dados
login_manager.init_app(app)

# view login
login_manager.login_view = 'login'
# session 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            return jsonify({"message": "Login successful"}), 200

    return jsonify({"message": "Invalid username or password"}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/user', methods=['POST'])

def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password, role='user') # role='user' é o default
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201

    return jsonify({"message": "Invalid username or password"}), 400

@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
def read_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"user": user.to_dict()}), 200
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if user_id != current_user.id and current_user.role == 'user':
        return jsonify({"message": "User not authorized to update this user"}), 403
    
    if username and password:
        
        user = User.query.get(user_id)
        if user:
            hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
            user.username = username
            user.password = hashed_password
            db.session.commit()
            return jsonify({"message": "User updated successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    
    return jsonify({"message": "Invalid username or password"}), 400

@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user_id != current_user.id and current_user.role != 'admin':
        return jsonify({"message": "User not authorized to delete this user"}), 403
    
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200

@app.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)