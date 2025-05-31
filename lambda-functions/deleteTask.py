import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

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
        
        # Check if task exists before deleting
        try:
            response = table.get_item(Key={'taskId': task_id})
            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({'error': 'Task not found'})
                }
        except ClientError:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Task not found'})
            }
        
        # Delete the task
        table.delete_item(Key={'taskId': task_id})
        
        return {
            'statusCode': 204,
            'headers': headers,
            'body': ''  # No content for successful deletion
        }
        
    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Database error'})
        }
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }
