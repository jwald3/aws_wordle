from ..models.user import User
import uuid

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def create_user(self, username, password):
        """Create a new user with a unique username and a password (to be hashed by the application)."""
        try:
            user = User.create_new_user(username, password)
            self.user_repository.create_user(user)
            return user
        except ValueError as e:
            raise ValueError(f"Error creating user: {e}")
        
    def login_user(self, username, password):
        """Login a user with a username and password. Returns the User object if successful, otherwise None."""
        return self.user_repository.login_user(username, password)
    
    def get_user_by_username(self, username):
        """Retrieve a user by their username."""
        return self.user_repository.get_user_by_username(username)
    
    def get_user_by_user_id(self, user_id):
        """Retrieve a user by their user_id."""
        return self.user_repository.get_user_by_user_id(user_id)
