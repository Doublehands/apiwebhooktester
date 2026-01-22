from flask import Flask, request, jsonify, render_template, redirect, url_for
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import base64
import requests  # 用于调用 AI 和 Freshchat API
import os
import json
from collections import deque
from datetime import datetime, timezone

app = Flask(__name__)

# --------- Config ---------
AGENT_BASE_URL = os.environ.get('AGENT_BASE_URL', 'https://api-sg.gptbots.ai').rstrip('/')
AGENT_API_KEY = os.environ.get('AGENT_API_KEY', 'app-hhnASRDrU1qZZfSfQJICsXd1')
AGENT_CONVERSATION_PATH = os.environ.get('AGENT_CONVERSATION_PATH', '/v1/conversation')
AGENT_SEND_PATH = os.environ.get(
    'AGENT_SEND_PATH', '/v2/conversation/message'
)
AGENT_TIMEOUT = float(os.environ.get('AGENT_TIMEOUT', '120'))

# Freshchat config
FRESHCHAT_PUBLIC_KEY_PEM = os.environ.get('FRESHCHAT_PUBLIC_KEY_PEM', '')
FRESHCHAT_TOKEN = os.environ.get('FRESHCHAT_TOKEN', 'eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6Ik')
FRESHCHAT_BASE_URL = os.environ.get(
    'FRESHCHAT_BASE_URL',
    'https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2'
).rstrip('/')
FRESHCHAT_ACTOR_ID = os.environ.get('FRESHCHAT_ACTOR_ID', 'gptbots_agent')  # Agent ID in Freshchat

def load_freshchat_public_key():
    if not FRESHCHAT_PUBLIC_KEY_PEM:
        return None
    try:
        return load_pem_public_key(FRESHCHAT_PUBLIC_KEY_PEM.encode('utf-8'))
    except Exception:
        return None

FRESHCHAT_PUBLIC_KEY = load_freshchat_public_key()

WEBHOOK_LOGS = deque(maxlen=200)

def utc_now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def safe_json_dump(value):
    try:
        return json.dumps(value, indent=2, ensure_ascii=True)
    except Exception:
        return str(value)

def log_webhook(source, payload, headers):
    WEBHOOK_LOGS.appendleft({
        'time': utc_now_iso(),
        'source': source,
        'payload': safe_json_dump(payload),
        'headers': safe_json_dump(headers),
    })

def agent_headers():
    return {
        'Authorization': f'Bearer {AGENT_API_KEY}',
        'Content-Type': 'application/json',
    }

def build_agent_url(path):
    if path.startswith('http://') or path.startswith('https://'):
        return path
    return f'{AGENT_BASE_URL}{path}'

@app.route('/freshchat-webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Freshchat-Signature')
    payload = request.get_data(as_text=True)

    if FRESHCHAT_PUBLIC_KEY:
        if not signature:
            return jsonify({'error': 'Missing signature'}), 401
        try:
            signature_bytes = base64.b64decode(signature)
            FRESHCHAT_PUBLIC_KEY.verify(
                signature_bytes,
                payload.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        except Exception:
            return jsonify({'error': 'Invalid signature'}), 401

    data = request.json
    log_webhook('freshchat', data, dict(request.headers))
    
    # 检查是否是用户消息
    try:
        if data.get('action') == 'message_create':
            message_data = data.get('data', {}).get('message', {})
            actor_type = message_data.get('actor_type')
            
            # 只处理用户发送的消息，忽略 agent 自己的消息
            if actor_type == 'user':
                message_parts = message_data.get('message_parts', [])
                if message_parts and 'text' in message_parts[0]:
                    user_message = message_parts[0]['text']['content']
                    conversation_id = message_data.get('conversation_id')
                    user_id = message_data.get('user_id')
                    
                    print(f"📨 收到 Freshchat 消息: {user_message[:50]}...")
                    
                    # 调用 AI Agent 获取回复
                    ai_response = call_ai_agent(user_message, user_id=f"freshchat_{user_id}")
                    
                    # 发送回复到 Freshchat
                    send_response_to_freshchat(conversation_id, user_id, ai_response)
                    
                    return jsonify({'status': 'Message processed'}), 200
        
        return jsonify({'status': 'Event ignored'}), 200
    except Exception as e:
        print(f"❌ 处理 Freshchat webhook 失败: {e}")
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/agent/webhook', methods=['POST'])
def agent_webhook():
    data = request.json if request.is_json else {'raw': request.get_data(as_text=True)}
    log_webhook('agent', data, dict(request.headers))
    return jsonify({'status': 'ok'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def home_page():
    return render_template(
        'home.html',
        agent_base_url=AGENT_BASE_URL,
        has_agent_key=bool(AGENT_API_KEY),
        webhook_count=len(WEBHOOK_LOGS)
    )

@app.route('/agent')
def agent_page():
    return render_template(
        'agent.html',
        agent_base_url=AGENT_BASE_URL,
        has_agent_key=bool(AGENT_API_KEY),
        conversation_path=AGENT_CONVERSATION_PATH,
        send_path=AGENT_SEND_PATH,
        last_result=None
    )

@app.route('/agent/conversation', methods=['POST'])
def agent_create_conversation():
    user_id = request.form.get('user_id', 'web')
    result = create_conversation(user_id)
    return render_template(
        'agent.html',
        agent_base_url=AGENT_BASE_URL,
        has_agent_key=bool(AGENT_API_KEY),
        conversation_path=AGENT_CONVERSATION_PATH,
        send_path=AGENT_SEND_PATH,
        last_result=result
    )

@app.route('/agent/send', methods=['POST'])
def agent_send_message():
    user_id = request.form.get('user_id', 'web')
    conversation_id = request.form.get('conversation_id', '').strip()
    message = request.form.get('message', '').strip()
    if not message:
        return render_template(
            'agent.html',
            agent_base_url=AGENT_BASE_URL,
            has_agent_key=bool(AGENT_API_KEY),
            conversation_path=AGENT_CONVERSATION_PATH,
            send_path=AGENT_SEND_PATH,
            last_result={'error': 'message is required'}
        )
    result = send_message(user_id, message, conversation_id)
    return render_template(
        'agent.html',
        agent_base_url=AGENT_BASE_URL,
        has_agent_key=bool(AGENT_API_KEY),
        conversation_path=AGENT_CONVERSATION_PATH,
        send_path=AGENT_SEND_PATH,
        last_result=result
    )

@app.route('/webhooks')
def webhooks_page():
    return render_template('webhooks.html', logs=list(WEBHOOK_LOGS))

@app.route('/webhooks/clear', methods=['POST'])
def webhooks_clear():
    WEBHOOK_LOGS.clear()
    return redirect(url_for('webhooks_page'))

@app.route('/freshchat')
def freshchat_page():
    return render_template(
        'freshchat.html',
        freshchat_base_url=FRESHCHAT_BASE_URL,
        has_freshchat_token=bool(FRESHCHAT_TOKEN),
        has_freshchat_public_key=bool(FRESHCHAT_PUBLIC_KEY),
        test_result=None
    )

@app.route('/freshchat/test', methods=['POST'])
def freshchat_test():
    """测试 Freshchat AI 回复功能"""
    message = request.form.get('message', '你好')
    conversation_id = request.form.get('conversation_id', 'test_conv_123')
    user_id = request.form.get('user_id', 'test_user_456')
    
    # 调用 AI Agent
    ai_response = call_ai_agent(message, user_id=f"freshchat_{user_id}")
    
    result = {
        'input': {
            'message': message,
            'conversation_id': conversation_id,
            'user_id': user_id
        },
        'ai_response': ai_response,
        'note': '这是模拟测试，未实际发送到 Freshchat'
    }
    
    return render_template(
        'freshchat.html',
        freshchat_base_url=FRESHCHAT_BASE_URL,
        has_freshchat_token=bool(FRESHCHAT_TOKEN),
        has_freshchat_public_key=bool(FRESHCHAT_PUBLIC_KEY),
        test_result=result
    )

@app.route('/chat')
def chat_page():
    """实时聊天测试页面（嵌入 Freshchat 气泡）"""
    return render_template(
        'chat.html',
        agent_configured=bool(AGENT_BASE_URL and AGENT_API_KEY),
        freshchat_configured=bool(FRESHCHAT_BASE_URL and FRESHCHAT_TOKEN)
    )

def call_ai_agent(message, user_id='freshchat_user'):
    """调用 GPTBots Agent 获取回复"""
    try:
        # 发送消息到 Agent（会自动创建会话）
        result = send_message(user_id, message, conversation_id=None)
        
        if result.get('error'):
            return f"抱歉，AI 服务暂时不可用: {result.get('error')}"
        
        # 从响应中提取 AI 回复
        response_data = result.get('response', {})
        
        # GPTBots API 可能的响应格式
        if 'answer' in response_data:
            return response_data['answer']
        elif 'message' in response_data:
            return response_data['message']
        elif 'data' in response_data and isinstance(response_data['data'], dict):
            if 'answer' in response_data['data']:
                return response_data['data']['answer']
            if 'message' in response_data['data']:
                return response_data['data']['message']
        
        # 如果找不到标准字段，返回整个响应的字符串形式
        return f"AI 回复: {json.dumps(response_data, ensure_ascii=False)}"
    except Exception as e:
        return f"抱歉，处理您的消息时出错: {str(e)}"

def send_response_to_freshchat(conversation_id, user_id, response):
    """发送回复到 Freshchat - 使用官方 API 格式"""
    url = f"{FRESHCHAT_BASE_URL}/conversations/{conversation_id}/messages"
    headers = {
        'Authorization': f'Bearer {FRESHCHAT_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'ASSUME-IDENTITY': 'false'
    }
    
    # Freshchat 官方 API 格式
    body = {
        'message_parts': [
            {
                'text': {
                    'content': response
                }
            }
        ],
        'message_type': 'normal',
        'actor_type': 'agent',
        'actor_id': FRESHCHAT_ACTOR_ID,
        'user_id': user_id
    }
    
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        print(f"✅ 成功发送回复到 Freshchat: {conversation_id}")
        print(f"   Response: {resp.json()}")
        return True
    except Exception as e:
        print(f"❌ 发送回复到 Freshchat 失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   状态码: {e.response.status_code}")
            print(f"   响应内容: {e.response.text}")
        return False

def create_conversation(user_id):
    if not AGENT_BASE_URL or not AGENT_API_KEY:
        return {'error': 'AGENT_BASE_URL or AGENT_API_KEY not set'}
    url = build_agent_url(AGENT_CONVERSATION_PATH)
    payload = {'user_id': user_id}
    headers = agent_headers()
    
    result = {
        'request': {
            'url': url,
            'method': 'POST',
            'headers': {k: v for k, v in headers.items() if k != 'Authorization'} | {'Authorization': 'Bearer ***'},
            'body': payload
        }
    }
    
    try:
        response = requests.post(
            url, headers=headers, json=payload, timeout=AGENT_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        conversation_id = data.get('conversation_id') or data.get('id')
        result.update({
            'conversation_id': conversation_id,
            'response': data,
            'status_code': response.status_code
        })
        return result
    except Exception as exc:
        result['error'] = str(exc)
        if hasattr(exc, 'response') and exc.response is not None:
            try:
                result['response'] = exc.response.json()
                result['status_code'] = exc.response.status_code
            except:
                result['response'] = exc.response.text
        return result

def send_message(user_id, message, conversation_id=None):
    if not AGENT_BASE_URL or not AGENT_API_KEY:
        return {'error': 'AGENT_BASE_URL or AGENT_API_KEY not set'}
    
    # 如果没有 conversation_id，先创建会话
    created_conversation = None
    if not conversation_id:
        conversation_result = create_conversation(user_id)
        if conversation_result.get('error'):
            return conversation_result
        conversation_id = conversation_result.get('conversation_id')
        created_conversation = conversation_result
    
    url = build_agent_url(AGENT_SEND_PATH)
    headers = agent_headers()
    # GPTBots API 格式
    payload = {
        'conversation_id': conversation_id,
        'response_mode': 'blocking',
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': message
                    }
                ]
            }
        ]
    }
    
    result = {
        'request': {
            'url': url,
            'method': 'POST',
            'headers': {k: v for k, v in headers.items() if k != 'Authorization'} | {'Authorization': 'Bearer ***'},
            'body': payload
        }
    }
    
    if created_conversation:
        result['created_conversation'] = created_conversation
    
    try:
        response = requests.post(
            url, headers=headers, json=payload, timeout=AGENT_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        result.update({
            'conversation_id': conversation_id,
            'response': data,
            'status_code': response.status_code
        })
        return result
    except Exception as exc:
        result['error'] = str(exc)
        result['conversation_id'] = conversation_id
        if hasattr(exc, 'response') and exc.response is not None:
            try:
                result['response'] = exc.response.json()
                result['status_code'] = exc.response.status_code
            except:
                result['response'] = exc.response.text
                result['status_code'] = exc.response.status_code if hasattr(exc.response, 'status_code') else None
        return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)