import boto3
from botocore.exceptions import ClientError
from models import User

class UserRepository:
    def __init__(self, table):
        self.table = table

    def create_or_update_user(self, user):
        """Creates a new user token record or updates an existing one."""
        try:
            response = self.table.put_item(Item=user.to_dict())
            return response
        except ClientError as e:
            print(f"Failed to create/update user: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Retrieves a user token record by the user ID."""
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            if 'Item' in response:
                return User.from_dict(response['Item'])
            return None
        except ClientError as e:
            print(f"Failed to get user: {e}")
            return None
        
    def get_user_by_token(self, token):
        response = self.table.query(
            IndexName='TokenIndex',
            KeyConditionExpression=Key('token').eq(token)
        )
        items = response.get('Items', [])
        if items:
            return User.from_dict(items[0])  # Assuming the token uniquely identifies the user
        return None