from flask import request, jsonify
from functools import wraps
from firebase_admin import auth
import api.auth_server


def verify_user(jwt_token: str) -> dict:
    """
    INPUT:
    id_token: A JWT token given by the user

    PURPOSE:
    Verifies a JWT token and returns the decoded token. 
    """
    # verify_id_token throws an exception when the auth token is invalid or old
    try:
        decoded_token = auth.verify_id_token(jwt_token)
    except:
        return {
            "error": "Invalid ID token"
        }

    return {
        "success": decoded_token
    }


def user_authentication():
    def _user_authentication(f):
        @wraps(f)
        def __user_authentication(*args, **kwargs):
            given_token = request.headers.get('Authorization')
            user_token = verify_user(given_token)

            if ("error" in user_token):
                return jsonify({
                    "status": "error",
                    "response": {
                        "code": 401,
                        "body": None,
                        "message": "User authentication failed"
                    }
                })

            result = f(user_token['success'], *args, **kwargs)

            return result
        return __user_authentication
    return _user_authentication
