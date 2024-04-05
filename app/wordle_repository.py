class WordleRepository:
    def __init__(self, table):
        self.table = table

    def create_wordle(self, wordle):
        self.table.put_item(Item=wordle)

    def get_wordle(self, game_id):
        response = self.table.get_item(Key={'game_id': game_id})
        return response['Item']

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
