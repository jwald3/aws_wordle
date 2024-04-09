import uuid
import bcrypt
import base64

class User:
    """The User class enables creating a user with a username and password, and generating a user_id to associate a user with their Wordle games."""
    def __init__(self, username, hashed_password, user_id=None):
        self.username = username
        self.hashed_password = hashed_password  # Assume this is already hashed if coming from storage
        self.user_id = str(uuid.uuid4()) if user_id is None else user_id

    def __repr__(self):
        return f"User(username={self.username}, user_id={self.user_id})"
    
    def __str__(self):
        return f"User(username={self.username}, user_id={self.user_id})"
    
    def to_dict(self):
        return {
            "username": self.username,
            "hashed_password": self.hashed_password,
            "user_id": self.user_id
        }
    
    def get_user_id(self):
        return self.user_id
    
    def get_username(self):
        return self.username

    def get_hashed_password(self):
        return self.hashed_password 

    @staticmethod
    def from_dict(user_dict: dict):
        return User(user_dict['username'], user_dict['hashed_password'], user_dict['user_id'])
   
    @staticmethod
    def hash_password(password):
        """Returns a hashed password for storing."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @classmethod
    def create_new_user(cls, username, password):
        """Hashes the password and returns a new User instance."""
        hashed_password = cls.hash_password(password)
        return cls(username, hashed_password)

    @staticmethod
    def verify_password(stored_hashed_password, provided_password):
        """Verifies if the provided password matches the stored hashed password."""
        # Check if stored_hashed_password is a Binary object or a base64 string
        if hasattr(stored_hashed_password, 'value'):
            # Assuming .value is the correct attribute for accessing the Binary content
            hashed_password_bytes = stored_hashed_password.value
        elif isinstance(stored_hashed_password, str):
            # If the hashed password is somehow stored as a base64 string, decode it
            hashed_password_bytes = base64.b64decode(stored_hashed_password)
        else:
            # If already in bytes, no action needed
            hashed_password_bytes = stored_hashed_password

        # Verify the provided password against the stored hash
        return bcrypt.checkpw(provided_password.encode('utf-8'), hashed_password_bytes)


