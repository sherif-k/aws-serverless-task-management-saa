import json
import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

def lambda_handler(event, context):
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
    }
    
    try:
        # Parse request body
        if event.get('body'):
            body = json.loads(event['body'])
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        # Validate required fields
        if not body.get('title') or not body['title'].strip():
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Title is required'})
            }
        
        # Create task object
        task_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        task = {
            'taskId': task_id,
            'title': body['title'].strip(),
            'description': body.get('description', ''),
            'status': body.get('status', 'pending'),
            'createdAt': timestamp,
            'updatedAt': timestamp
        }
        
        # Save to DynamoDB
        table.put_item(Item=task)
        
        # Return success response
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({
                'message': 'Task created successfully',
                'task': task
            })
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
