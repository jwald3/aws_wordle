from flask import jsonify, request

def create_user_routes(app):
    @app.route('/register', methods=['POST'])
    def register_user():
        username = request.json['username']
        password = request.json['password']
        try:
            user = app.config['user_service'].create_user(username, password)
            return jsonify({"user_id": user.user_id})
        except ValueError as e:
            return jsonify({"message": str(e)}), 400
        
    @app.route('/login', methods=['POST'])
    def login_user():
        username = request.json['username']
        password = request.json['password']
        user = app.config['user_service'].login_user(username, password)

        print(user)
        if user:
            return jsonify({"user_id": user.get('user_id'), "token": user.get('token')})
        return jsonify({"message": "Invalid username or password"}), 400
    
    @app.route('/user/<user_id>', methods=['GET'])
    def get_user(user_id):
        user = app.config['user_service'].get_user_by_user_id(user_id)
        if user:
            return jsonify(user.to_dict())
        return jsonify({"message": "User not found"}), 404
    
    return app