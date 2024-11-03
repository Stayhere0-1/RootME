from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models.user import  UserModel
import os
from datetime import timedelta


app =  Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'peduliapagwbjirwkwkakujugamalas!@^^*!******00012839')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
jwt = JWTManager(app)


DB_CONFIG = {
    'user' : os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'host' : os.environ.get('DB_HOST', '127.0.0.1'),
    'database' : os.environ.get('DB_NAME', 'rootme_db')
}

user_model = UserModel(DB_CONFIG)

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        mail = data.get('mail')
        
        return user_model.create_user(username, password, mail)
        
    except Exception as e:
        return jsonify({
            "message": "Registration failed",
            "error": str(e),
            "status": "failed"
        }), 400
    

if __name__ == '__main__':
    app.run(debug=False)