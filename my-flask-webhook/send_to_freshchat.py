#!/usr/bin/env python3
"""直接使用 Freshchat API 发送消息到指定 conversation"""
import requests
import json

# Freshchat 配置
FRESHCHAT_BASE_URL = "https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2"
FRESHCHAT_TOKEN = "eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmcmVzaGNoYXQiLCJhdWQiOiJmcmVzaGNoYXQiLCJpYXQiOjE3Njg5Nzc5NDEsInNjb3BlIjoiYWdlbnQ6cmVhZCBhZ2VudDpjcmVhdGUgYWdlbnQ6dXBkYXRlIGFnZW50OmRlbGV0ZSBjb252ZXJzYXRpb246Y3JlYXRlIGNvbnZlcnNhdGlvbjpyZWFkIGNvbnZlcnNhdGlvbjp1cGRhdGUgbWVzc2FnZTpjcmVhdGUgbWVzc2FnZTpnZXQgYmlsbGluZzp1cGRhdGUgcmVwb3J0czpmZXRjaCByZXBvcnRzOmV4dHJhY3QgcmVwb3J0czpyZWFkIHJlcG9ydHM6ZXh0cmFjdDpyZWFkIGFjY291bnQ6cmVhZCBkYXNoYm9hcmQ6cmVhZCB1c2VyOnJlYWQgdXNlcjpjcmVhdGUgdXNlcjp1cGRhdGUgdXNlcjpkZWxldGUgb3V0Ym91bmRtZXNzYWdlOnNlbmQgb3V0Ym91bmRtZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6bWVzc2FnZTpzZW5kIG1lc3NhZ2luZy1jaGFubmVsczptZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6dGVtcGxhdGU6Y3JlYXRlIG1lc3NhZ2luZy1jaGFubmVsczp0ZW1wbGF0ZTpnZXQgZmlsdGVyaW5ib3g6cmVhZCBmaWx0ZXJpbmJveDpjb3VudDpyZWFkIHJvbGU6cmVhZCBpbWFnZTp1cGxvYWQiLCJ0eXAiOiJCZWFyZXIiLCJjbGllbnRJZCI6ImZjLTJmMjJiNzE0LWQ4NWEtNGUzZi04MjRlLTAzOWU5ZDE0NzZjNSIsInN1YiI6ImYxM2Y0YWZhLTc1OWQtNDVhMy04NmJkLWZjZTE2MTA3Y2UyOSIsImp0aSI6ImFkNWM4ZmIxLTBkNDctNGI4OS1iMTliLTM0MGI2MzZmYmQ0ZiIsImV4cCI6MjA4NDUxMDc0MX0.ob_D4Q_Tv_77MC-p97ibA7o3SPba9H_7tawM6LPJaPw"

# 目标 conversation
CONVERSATION_ID = "2669904a-a5b5-4516-a54c-b52c03ad155d"
USER_ID = "29a05a7f-7cd5-4928-9d1b-ddca7c3d0b8a"

def send_message(conversation_id, user_id, message):
    """发送消息到 Freshchat"""
    url = f"{FRESHCHAT_BASE_URL}/conversations/{conversation_id}/messages"
    
    headers = {
        'Authorization': f'Bearer {FRESHCHAT_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'ASSUME-IDENTITY': 'false'
    }
    
    # Freshchat API 格式（根据官方文档）
    # 需要同时提供 user_id 和 actor_id
    body = {
        'message_parts': [
            {
                'text': {
                    'content': message
                }
            }
        ],
        'message_type': 'normal',
        'actor_type': 'agent',
        'user_id': user_id,  # 接收消息的用户
        'actor_id': '2e6a98aa-5155-4b3e-9745-96a784e79eb2'  # Jacky Lee (Agent ID)
    }
    
    print("="*70)
    print("📤 发送消息到 Freshchat")
    print("="*70)
    print(f"URL: {url}")
    print(f"Conversation ID: {conversation_id}")
    print(f"User ID: {user_id}")
    print(f"Message: {message}")
    print(f"\nHeaders:")
    print(f"  Authorization: Bearer {FRESHCHAT_TOKEN[:50]}...")
    print(f"  Content-Type: application/json")
    print(f"  Accept: application/json")
    print(f"  ASSUME-IDENTITY: false")
    print(f"\nBody:")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    print("="*70)
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        print(f"\n📥 响应状态码: {response.status_code}")
        print(f"响应 Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ 消息发送成功！")
            try:
                result = response.json()
                print(f"\n响应数据:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except:
                print(f"\n响应内容: {response.text}")
            return True
        else:
            print(f"❌ 消息发送失败")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"错误响应: {e.response.text}")
        return False

if __name__ == "__main__":
    print("\n🤖 Freshchat 消息发送测试")
    print("="*70)
    
    # 测试消息
    test_message = "你好！这是来自 GPTBots AI Agent 的测试回复。我已经成功接收到你的消息并通过 API 回复了！"
    
    # 发送消息
    success = send_message(CONVERSATION_ID, USER_ID, test_message)
    
    print("\n" + "="*70)
    if success:
        print("✅ 测试完成！请在 Freshchat 中查看消息。")
    else:
        print("❌ 测试失败，请检查上面的错误信息。")
    print("="*70 + "\n")
