from flask import jsonify, request
from .user_service import user_service
from .errors import UnauthorizedUserError

def create_user_routes(app):
    @app.route('/user/register', methods=['POST'])
    def register_user():
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({"message": "User ID is required"}), 400

        try:
            user = user_service.register_user(user_id)
            return jsonify({"user_id": user.user_id, "token": user.token}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @app.route('/user/login', methods=['POST'])
    def login_user():
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({"message": "User ID is required"}), 400

        try:
            user = user_service.login_user(user_id)
            return jsonify({"user_id": user.user_id, "token": user.token}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @app.route('/user/validate', methods=['POST'])
    def validate_token():
        user_id = request.json.get('user_id')
        token = request.json.get('token')
        if not user_id or not token:
            return jsonify({"message": "User ID and token are required"}), 400

        try:
            is_valid = user_service.validate_user_token(user_id, token)
            if is_valid:
                return jsonify({"message": "Token is valid"}), 200
            else:
                return jsonify({"message": "Token is invalid"}), 401
        except UnauthorizedUserError as e:
            return jsonify({"message": str(e)}), 401
        except Exception as e:
            return jsonify({"message": "An unexpected error occurred"}), 500

    return app