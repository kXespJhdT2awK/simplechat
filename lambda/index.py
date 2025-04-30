import json
import os
import re
import urllib.request  # 追加：HTTPリクエスト用
from botocore.exceptions import ClientError  # 未使用だが元のまま保持

# Lambda コンテキストからリージョンを抽出する関数（未使用だがそのまま）
def extract_region_from_arn(arn):
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"

# 使わないけど一応そのまま残しておく
bedrock_client = None

# モデルIDも未使用になるが、元のまま保持
MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")

# 環境変数から Colab API URL を取得
COLAB_API_URL = os.getenv("COLAB_API_URL")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        print("Processing message:", message)
        print("Using model:", MODEL_ID)

        messages = conversation_history.copy()
        messages.append({
            "role": "user",
            "content": message
        })

        # 🔄 差し替え：ColabにPOSTする
        request_payload = {
            "message": message,
            "conversationHistory": messages
        }
        data = json.dumps(request_payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json"
        }
        req = urllib.request.Request(COLAB_API_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as res:
            response_body = json.loads(res.read().decode("utf-8"))

        print("Colab response:", json.dumps(response_body, default=str))

        assistant_response = response_body['response']
        messages = response_body.get("conversationHistory", messages)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }

    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
