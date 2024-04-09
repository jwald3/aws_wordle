from ..models.user import User
from boto3.dynamodb.conditions import Attr

class UserRepository:
    def __init__(self, table):
        self.table = table

    def create_user(self, user):
        # check if user already exists (username must be unique)
        if self.get_user_by_username(user.username):
            raise ValueError(f"User with username {user.username} already exists")
        self.table.put_item(Item=user.to_dict())

    def login_user(self, username, password):
        user: dict = self.get_user_by_username(username)
        if user and User.verify_password(user.hashed_password, password):
            return user
        return None
        
    def get_user_by_username(self, username):
        """Username is not a primary key, so we need to scan the table to find the user."""
        response = self.table.scan(FilterExpression=Attr('username').eq(username))

        # There will only be one user with the given username, so return the first item
        if response.get('Items'):
            return User.from_dict(response.get('Items')[0])
        return None
    
    def get_user_by_user_id(self, user_id):
        response = self.table.scan(FilterExpression=Attr('user_id').eq(user_id))
        return response.get('Items')