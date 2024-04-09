from functools import wraps
from flask import request, jsonify
import jwt

def validate_and_decode_jwt(token, secret_key):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        bearer = 'Bearer '

        token = request.headers.get('Authorization', None)
        if token and token.startswith(bearer):
            token = token.replace(bearer, '', 1)
            user_id = validate_and_decode_jwt(token, 'secret')
            if user_id:
                request.user_id = user_id
                return f(*args, **kwargs)
            else:
                return jsonify({"message": "Invalid or expired token"}), 401
        else:
            return jsonify({"message": "Missing authentication token"}), 401
    wrap.__name__ = f.__name__
    return wrap