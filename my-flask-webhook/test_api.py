#!/usr/bin/env python3
"""测试 GPTBots API 连接"""
import requests
import json

BASE_URL = "https://api-sg.gptbots.ai"
API_KEY = "app-3CJGEcHeYRMJDMTku3nAKy12"

def test_create_conversation():
    """测试创建会话"""
    print("🔄 测试创建会话...")
    url = f"{BASE_URL}/v1/conversation"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"user_id": "test_user"}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        conversation_id = result.get("conversation_id")
        print(f"✅ 会话创建成功: {conversation_id}")
        print(f"📄 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return conversation_id
    except Exception as e:
        print(f"❌ 创建会话失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应内容: {e.response.text}")
        return None

def test_send_message(conversation_id, message):
    """测试发送消息"""
    print(f"\n🔄 测试发送消息到会话 {conversation_id}...")
    url = f"{BASE_URL}/v2/conversation/message"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    message_data = {
        "conversation_id": conversation_id,
        "response_mode": "blocking",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=message_data, timeout=120)
        response.raise_for_status()
        result = response.json()
        print(f"✅ 消息发送成功")
        print(f"📄 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return result
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应内容: {e.response.text}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("GPTBots API 测试")
    print("=" * 60)
    
    # 1. 创建会话
    conversation_id = test_create_conversation()
    
    if conversation_id:
        # 2. 发送消息
        test_send_message(conversation_id, "你好，这是一条测试消息")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
