from errors import ResourceNotFoundError, UnauthorizedUserError
from boto3.dynamodb.conditions import Key

class WordleRepository:
    def __init__(self, table):
        self.table = table

    def create_wordle(self, wordle):
        self.table.put_item(Item=wordle)

    def get_all_wordles(self, user_token=None):
        """Get all wordle games belonging to a user. If there is no user_token, throw an error."""
        if not user_token:
            raise UnauthorizedUserError("User token is required to get wordle games.")

        response = self.table.query(IndexName='user_token-index', KeyConditionExpression=Key('user_token').eq(user_token))
        return response['Items']

    def get_wordle(self, game_id, user_token=None):
        if not user_token:
            raise UnauthorizedUserError("User token is required to get wordle games.")
        response = self.table.get_item(Key={'game_id': game_id})
        if 'Item' not in response or response['Item']['user_token'] != user_token:
            raise ResourceNotFoundError(f"Game with game_id {game_id} not found for user.")
        return response['Item']

    def update_wordle(self, game_id, user_token, updates):
        update_expression = 'SET ' + ', '.join([f'{key} = :{key}' for key in updates.keys()])
        expression_attribute_values = {f':{key}': value for key, value in updates.items()}

        # Adding a condition expression for user_token validation
        condition_expression = 'user_token = :user_token'
        expression_attribute_values[':user_token'] = user_token

        try:
            response = self.table.update_item(
                Key={'game_id': game_id},
                UpdateExpression=update_expression,
                ConditionExpression=condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='UPDATED_NEW'
            )
            return response
        except self.table.meta.client.exceptions.ConditionalCheckFailedException:
            raise ResourceNotFoundError(f"Game with game_id {game_id} not found for user.")

