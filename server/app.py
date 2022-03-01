import sys

def handler(event, context):
    return response('Hello World!', 200)

def response(body, status_code, type='text/plain'):
    return {
        'statusCode': status_code,
        'body': body,
        'headers': {
            'Content-Type': type,
            'Access-Control-Allow-Origin': '*'
        }
    }