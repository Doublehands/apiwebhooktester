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
FRESHCHAT_ACTOR_ID = os.environ.get('FRESHCHAT_ACTOR_ID', '2e6a98aa-5155-4b3e-9745-96a784e79eb2')  # Jacky Lee (Agent ID)

def load_freshchat_public_key():
    if not FRESHCHAT_PUBLIC_KEY_PEM:
        return None
    try:
        return load_pem_public_key(FRESHCHAT_PUBLIC_KEY_PEM.encode('utf-8'))
    except Exception:
        return None

FRESHCHAT_PUBLIC_KEY = load_freshchat_public_key()

WEBHOOK_LOGS = deque(maxlen=200)
PROCESSED_MESSAGES = {}  # 存储已处理的消息 ID，防止重复处理
CONVERSATION_MAPPING = {}  # Freshchat conversation_id -> GPTBots conversation_id 映射

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
    """接收 Freshchat Webhook"""
    print("\n" + "="*70)
    print("🔔 收到 Freshchat Webhook 请求")
    print("="*70)
    
    # 获取签名和 payload
    signature = request.headers.get('X-Freshchat-Signature')
    payload = request.get_data(as_text=True)
    test_mode = request.headers.get('X-Test-Mode') == 'true'  # 测试模式标记
    
    print(f"📋 Headers: {dict(request.headers)}")
    print(f"🔐 Signature: {signature[:50] if signature else 'None'}...")
    print(f"🧪 Test Mode: {test_mode}")

    # 验证签名（如果配置了 Public Key 且不是测试模式）
    if FRESHCHAT_PUBLIC_KEY and not test_mode:
        print("🔒 开始验证签名...")
        if not signature:
            print("❌ 缺少签名")
            return jsonify({'error': 'Missing signature', 'hint': 'Add X-Test-Mode: true header to skip signature verification for testing'}), 401
        try:
            signature_bytes = base64.b64decode(signature)
            FRESHCHAT_PUBLIC_KEY.verify(
                signature_bytes,
                payload.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            print("✅ 签名验证通过")
        except Exception as e:
            print(f"❌ 签名验证失败: {e}")
            return jsonify({'error': 'Invalid signature', 'hint': 'Add X-Test-Mode: true header to skip signature verification for testing'}), 401
    else:
        if test_mode:
            print("⚠️  测试模式：跳过签名验证")
        else:
            print("⚠️  跳过签名验证（未配置 Public Key）")

    # 解析 JSON 数据
    try:
        data = request.json
    except Exception as e:
        print(f"❌ 无法解析 JSON: {e}")
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # 记录到 webhook 日志
    log_webhook('freshchat', data, dict(request.headers))
    
    print(f"📦 Webhook 数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
    
    # 检查是否是用户消息
    try:
        action = data.get('action')
        print(f"🎬 Action: {action}")
        
        if action == 'message_create':
            message_data = data.get('data', {}).get('message', {})
            actor_type = message_data.get('actor_type')
            conversation_id = message_data.get('conversation_id')
            user_id = message_data.get('user_id')
            
            print(f"👤 Actor Type: {actor_type}")
            print(f"💬 Conversation ID: {conversation_id}")
            print(f"🆔 User ID: {user_id}")
            
            # 只处理用户发送的消息，忽略 agent 自己的消息
            if actor_type == 'user':
                message_parts = message_data.get('message_parts', [])
                message_id = message_data.get('id')  # 消息的唯一 ID
                
                print(f"📝 Message ID: {message_id}")
                print(f"📝 Message Parts: {message_parts}")
                
                # 检查是否已处理过这条消息（防止重复）
                if message_id and message_id in PROCESSED_MESSAGES:
                    print(f"⚠️  消息已处理过，跳过: {message_id}")
                    return jsonify({
                        'status': 'ignored',
                        'message': 'Message already processed',
                        'message_id': message_id
                    }), 200
                
                if message_parts and 'text' in message_parts[0]:
                    user_message = message_parts[0]['text']['content']
                    
                    print(f"\n{'='*70}")
                    print(f"✅ 成功提取消息信息:")
                    print(f"   - Message ID: {message_id}")
                    print(f"   - Conversation ID: {conversation_id}")
                    print(f"   - User ID: {user_id}")
                    print(f"   - Message: {user_message}")
                    print(f"{'='*70}\n")
                    
                    # 标记消息为已处理
                    if message_id:
                        PROCESSED_MESSAGES[message_id] = {
                            'time': utc_now_iso(),
                            'conversation_id': conversation_id
                        }
                        # 只保留最近 1000 条
                        if len(PROCESSED_MESSAGES) > 1000:
                            oldest_key = next(iter(PROCESSED_MESSAGES))
                            del PROCESSED_MESSAGES[oldest_key]
                    
                    # 获取或创建 GPTBots conversation_id（保持会话连续性）
                    gptbots_conversation_id = CONVERSATION_MAPPING.get(conversation_id)
                    
                    if gptbots_conversation_id:
                        print(f"🔗 使用已存在的 GPTBots 会话: {gptbots_conversation_id}")
                    else:
                        print(f"🆕 将为此 Freshchat 会话创建新的 GPTBots 会话")
                    
                    # 调用 AI Agent 获取回复
                    print("🤖 开始调用 AI Agent...")
                    ai_result = send_message(f"freshchat_{user_id}", user_message, gptbots_conversation_id)
                    
                    if ai_result.get('error'):
                        print(f"❌ AI Agent 调用失败: {ai_result.get('error')}")
                        return jsonify({
                            'status': 'error',
                            'message': 'AI Agent call failed',
                            'error': ai_result.get('error')
                        }), 500
                    
                    # 保存会话映射
                    new_gptbots_conv_id = ai_result.get('conversation_id')
                    if new_gptbots_conv_id and not gptbots_conversation_id:
                        CONVERSATION_MAPPING[conversation_id] = new_gptbots_conv_id
                        print(f"💾 保存会话映射: {conversation_id} → {new_gptbots_conv_id}")
                    
                    # 提取 AI 回复
                    ai_response = extract_ai_response(ai_result)
                    print(f"💡 AI 回复: {ai_response[:100]}...")
                    
                    # 发送回复到 Freshchat
                    print("📤 发送回复到 Freshchat...")
                    success = send_response_to_freshchat(conversation_id, user_id, ai_response)
                    
                    if success:
                        print("✅ Webhook 处理完成\n")
                        return jsonify({
                            'status': 'success',
                            'message': 'Message processed',
                            'conversation_id': conversation_id,
                            'gptbots_conversation_id': new_gptbots_conv_id,
                            'user_id': user_id
                        }), 200
                    else:
                        print("⚠️  回复发送失败\n")
                        return jsonify({
                            'status': 'partial_success',
                            'message': 'Message received but reply failed',
                            'conversation_id': conversation_id
                        }), 200
                else:
                    print("⚠️  消息格式不正确或不包含文本内容")
            else:
                print(f"ℹ️  忽略非用户消息 (actor_type: {actor_type})")
        else:
            print(f"ℹ️  忽略事件类型: {action}")
        
        print("="*70 + "\n")
        return jsonify({'status': 'ignored', 'action': action}), 200
        
    except Exception as e:
        print(f"\n❌ 处理 Freshchat webhook 失败:")
        print(f"   错误: {e}")
        print(f"   类型: {type(e).__name__}")
        import traceback
        print(f"   堆栈: {traceback.format_exc()}")
        print("="*70 + "\n")
        return jsonify({'status': 'error', 'message': str(e)}), 500

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

@app.route('/chat-test')
def chat_test_page():
    """Freshchat 气泡调试页面"""
    return render_template('chat_test.html')

@app.route('/webhook-test')
def webhook_test_page():
    """Webhook 测试页面"""
    return render_template('webhook_simple.html', test_result=None)

@app.route('/webhook-test/send', methods=['POST'])
def webhook_test_send():
    """发送测试 webhook"""
    conversation_id = request.form.get('conversation_id')
    user_id = request.form.get('user_id')
    message = request.form.get('message')
    
    # 构造 Freshchat webhook 格式的数据
    webhook_data = {
        'action': 'message_create',
        'data': {
            'message': {
                'actor_type': 'user',
                'conversation_id': conversation_id,
                'user_id': user_id,
                'message_parts': [
                    {
                        'text': {
                            'content': message
                        }
                    }
                ]
            }
        }
    }
    
    result = {
        'sent_data': webhook_data,
        'success': False
    }
    
    try:
        # 发送到 webhook 端点（添加测试模式 header 跳过签名验证）
        response = requests.post(
            f'{request.host_url}freshchat-webhook',
            json=webhook_data,
            headers={
                'Content-Type': 'application/json',
                'X-Test-Mode': 'true'  # 测试模式，跳过签名验证
            },
            timeout=30
        )
        
        result['webhook_response'] = response.json()
        result['status_code'] = response.status_code
        result['success'] = response.status_code == 200
        
    except Exception as e:
        result['error'] = str(e)
    
    return render_template('webhook_simple.html', test_result=result)

def extract_ai_response(ai_result):
    """从 AI Agent 的响应中提取回复内容"""
    response_data = ai_result.get('response', {})
    
    # 尝试不同的字段
    if 'answer' in response_data:
        return response_data['answer']
    elif 'message' in response_data:
        return response_data['message']
    elif 'content' in response_data:
        return response_data['content']
    elif 'data' in response_data and isinstance(response_data['data'], dict):
        if 'answer' in response_data['data']:
            return response_data['data']['answer']
        if 'message' in response_data['data']:
            return response_data['data']['message']
        if 'content' in response_data['data']:
            return response_data['data']['content']
    
    # 如果找不到标准字段，返回整个响应的字符串形式
    return f"AI 回复: {json.dumps(response_data, ensure_ascii=False)}"

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
    print(f"\n{'='*70}")
    print(f"📤 准备发送回复到 Freshchat")
    print(f"{'='*70}")
    print(f"Conversation ID: {conversation_id}")
    print(f"User ID: {user_id}")
    print(f"Response: {response[:200]}...")
    print(f"Actor ID: {FRESHCHAT_ACTOR_ID}")
    print(f"Token: {FRESHCHAT_TOKEN[:50]}...")
    
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
        'user_id': user_id,
        'actor_id': FRESHCHAT_ACTOR_ID
    }
    
    print(f"URL: {url}")
    print(f"Body: {json.dumps(body, indent=2, ensure_ascii=False)[:500]}...")
    print(f"{'='*70}\n")
    
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        print(f"✅ 成功发送回复到 Freshchat: {conversation_id}")
        try:
            print(f"   Response: {resp.json()}")
        except:
            print(f"   Response: {resp.text}")
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

# Vercel serverless function handler
app = app