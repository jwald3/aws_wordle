from boto3.dynamodb.conditions import Attr

class WordleRepository:
    def __init__(self, table):
        self.table = table

    def create_wordle(self, wordle):
        self.table.put_item(Item=wordle)

    def get_wordle(self, game_id, user_id):
        response = self.table.get_item(Key={'game_id': game_id})

        if response.get('Item') and response['Item']['user_id'] == user_id:
            return response['Item']

        return None
    
    def get_all_wordles(self, user_id):
        response = self.table.scan(FilterExpression=Attr('user_id').eq(user_id))
        return response.get('Items')

    def update_wordle(self, game_id, updates):
        update_expression = 'SET ' + ', '.join([f'{key} = :{key}' for key in updates.keys()])
        expression_attribute_values = {f':{key}': value for key, value in updates.items()}

        response = self.table.update_item(
            Key={'game_id': game_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='UPDATED_NEW'
        )

        return response
