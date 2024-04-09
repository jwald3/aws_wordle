import uuid
from models import User, WordleHelper  
from errors import UserRegistrationError, UserLoginError, UnauthorizedUserError

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register_user(self, user_id):
        """Registers a new user."""
        user = User(user_id=user_id, token=None)
        response = self.user_repository.create_or_update_user(user)
        if not response:
            raise UserRegistrationError("Failed to register user.")
        return user

    def login_user(self, user_id):
        """Logs in a user and generates a token."""
        token = str(uuid.uuid4())
        user = User(user_id=user_id, token=token)
        response = self.user_repository.create_or_update_user(user)
        if not response:
            raise UserLoginError("Failed to login user.")
        return user

    def validate_user_token(self, user_id, token):
        """Validates a user's token."""
        user = self.user_repository.get_user_by_id(user_id)
        if not user or not user.validate_token(token):
            raise UnauthorizedUserError("Unauthorized access or invalid token.")
        return True
