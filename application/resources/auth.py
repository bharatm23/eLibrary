from flask import Blueprint, jsonify, request
from ..models import User, TokenBlockedList
from flask_jwt_extended import (create_access_token, create_refresh_token, 
                                jwt_required, get_jwt, current_user, get_jwt_identity)

auth_bp = Blueprint('auth', __name__)

@auth_bp.post('/register')
def register_student():
    data = request.get_json()
    user = User.get_user_by_usrnm(username = data.get('username'))
    if user:
        return jsonify({"error":"User already exists."}), 403

    new_user = User(
        username = data.get('username'),
        role = "Student",
        fav_genre = data.get('fav_genre'),
        fav_book = data.get('fav_book'),
        fav_author = data.get('fav_author')
    )
    new_user.password_hash(password = data.get('password'))
    new_user.save_user()
    return jsonify({"message":"User created."}), 201

@auth_bp.post('/user-login')
def user_login():
    data = request.get_json()
    user = User.get_user_by_usrnm(username = data.get('username'))
    
    if user and (user.check_password(password = data.get('password'))):
        access_token = create_access_token(identity=user.username)
        refresh_token = create_refresh_token(identity=user.username)

        return jsonify(
            {
                "message":"Logged in",
                "tokens": {
                    "access": access_token,
                    "refresh": refresh_token
                },
                "role": user.role,
                "username": user.username
            }
        ), 200
    else:
        return jsonify({"error":"Invalid login credentials"}), 400

@auth_bp.get("/whoami")
@jwt_required()
def whoami():
    return jsonify({"user_details" : {"username": current_user.username, 
                                      "role": current_user.role,
                                      "password": current_user.password}
                    })

@auth_bp.get('/refresh')
@jwt_required(refresh=True)
def refresh_access():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"new_access_token":new_access_token})


@auth_bp.post('/logout')
@jwt_required(verify_type=False)
def logout():
    jti = get_jwt()["jti"]  
    token_type = get_jwt()['type'] #Refresh or access type
    token_username = get_jwt()['sub']

    token_blocked = TokenBlockedList(jti=jti, username=token_username) 
    token_blocked.save()

    return jsonify({"message": f"Token for username {token_username}'s {token_type.title()} type revoked successfully."}), 200

# @auth_bp.get('/logout')
# @jwt_required(verify_type=False)
# def logout():
#     jwt = get_jwt()
#     jti = jwt['jti']
#     token_type = jwt['type'] #Refresh or access type
#     token_username = jwt['sub']

#     token_blocked = TokenBlockedList(jti=jti, username=token_username)
#     token_blocked.save()
#     return jsonify({"message": f"{token_type.title()} token revoked successfully."}), 200

#====================END OF FILE====================#