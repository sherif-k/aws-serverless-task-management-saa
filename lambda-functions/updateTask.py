import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
    }
    
    try:
        # Get task ID from path parameters
        path_params = event.get('pathParameters') or {}
        task_id = path_params.get('id')
        
        if not task_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Task ID is required'})
            }
        
        # Parse request body
        if event.get('body'):
            body = json.loads(event['body'])
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        # Get existing task
        try:
            response = table.get_item(Key={'taskId': task_id})
            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({'error': 'Task not found'})
                }
            existing_task = response['Item']
        except ClientError as e:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Task not found'})
            }
        
        # Update only the fields provided, keep existing values for others
        updated_task = existing_task.copy()
        updated_task['updatedAt'] = datetime.utcnow().isoformat() + 'Z'
        
        # Update only provided fields
        if 'title' in body:
            updated_task['title'] = body['title']
        if 'description' in body:
            updated_task['description'] = body['description']
        if 'status' in body:
            updated_task['status'] = body['status']
        
        # Ensure status always exists (DynamoDB reserved word issue)
        if 'status' not in updated_task:
            updated_task['status'] = existing_task.get('status', 'pending')
        
        # Put the updated item back (this replaces the entire item)
        table.put_item(Item=updated_task)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Task updated successfully',
                'task': updated_task
            }, cls=DecimalEncoder)
        }
        
    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Database error'})
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }
