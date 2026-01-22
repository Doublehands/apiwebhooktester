#!/usr/bin/env python3
"""测试不同的 Freshchat API 消息格式"""
import requests
import json

FRESHCHAT_BASE_URL = "https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2"
FRESHCHAT_TOKEN = "eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmcmVzaGNoYXQiLCJhdWQiOiJmcmVzaGNoYXQiLCJpYXQiOjE3Njg5Nzc5NDEsInNjb3BlIjoiYWdlbnQ6cmVhZCBhZ2VudDpjcmVhdGUgYWdlbnQ6dXBkYXRlIGFnZW50OmRlbGV0ZSBjb252ZXJzYXRpb246Y3JlYXRlIGNvbnZlcnNhdGlvbjpyZWFkIGNvbnZlcnNhdGlvbjp1cGRhdGUgbWVzc2FnZTpjcmVhdGUgbWVzc2FnZTpnZXQgYmlsbGluZzp1cGRhdGUgcmVwb3J0czpmZXRjaCByZXBvcnRzOmV4dHJhY3QgcmVwb3J0czpyZWFkIHJlcG9ydHM6ZXh0cmFjdDpyZWFkIGFjY291bnQ6cmVhZCBkYXNoYm9hcmQ6cmVhZCB1c2VyOnJlYWQgdXNlcjpjcmVhdGUgdXNlcjp1cGRhdGUgdXNlcjpkZWxldGUgb3V0Ym91bmRtZXNzYWdlOnNlbmQgb3V0Ym91bmRtZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6bWVzc2FnZTpzZW5kIG1lc3NhZ2luZy1jaGFubmVsczptZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6dGVtcGxhdGU6Y3JlYXRlIG1lc3NhZ2luZy1jaGFubmVsczp0ZW1wbGF0ZTpnZXQgZmlsdGVyaW5ib3g6cmVhZCBmaWx0ZXJpbmJveDpjb3VudDpyZWFkIHJvbGU6cmVhZCBpbWFnZTp1cGxvYWQiLCJ0eXAiOiJCZWFyZXIiLCJjbGllbnRJZCI6ImZjLTJmMjJiNzE0LWQ4NWEtNGUzZi04MjRlLTAzOWU5ZDE0NzZjNSIsInN1YiI6ImYxM2Y0YWZhLTc1OWQtNDVhMy04NmJkLWZjZTE2MTA3Y2UyOSIsImp0aSI6ImFkNWM4ZmIxLTBkNDctNGI4OS1iMTliLTM0MGI2MzZmYmQ0ZiIsImV4cCI6MjA4NDUxMDc0MX0.ob_D4Q_Tv_77MC-p97ibA7o3SPba9H_7tawM6LPJaPw"

CONVERSATION_ID = "2669904a-a5b5-4516-a54c-b52c03ad155d"
USER_ID = "29a05a7f-7cd5-4928-9d1b-ddca7c3d0b8a"

def test_format(format_name, body):
    """测试特定格式"""
    url = f"{FRESHCHAT_BASE_URL}/conversations/{CONVERSATION_ID}/messages"
    headers = {
        'Authorization': f'Bearer {FRESHCHAT_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"\n{'='*70}")
    print(f"🧪 测试格式: {format_name}")
    print(f"{'='*70}")
    print(f"Body: {json.dumps(body, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        print(f"\n状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code in [200, 201]:
            print(f"✅ 成功！使用格式: {format_name}")
            return True
        else:
            print(f"❌ 失败")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    print("🔍 测试不同的 Freshchat API 消息格式")
    
    test_message = "测试消息 - 格式测试"
    
    # 格式 1: 最简单的格式（只有必需字段）
    format1 = {
        'message_parts': [
            {
                'text': {
                    'content': test_message
                }
            }
        ]
    }
    
    # 格式 2: 添加 message_type 和 actor_type
    format2 = {
        'message_parts': [
            {
                'text': {
                    'content': test_message
                }
            }
        ],
        'message_type': 'normal',
        'actor_type': 'agent'
    }
    
    # 格式 3: 添加 actor_id（使用 token 中的 sub）
    format3 = {
        'message_parts': [
            {
                'text': {
                    'content': test_message
                }
            }
        ],
        'message_type': 'normal',
        'actor_type': 'agent',
        'actor_id': 'f13f4afa-759d-45a3-86bd-fce16107ce29'  # 从 token sub 字段
    }
    
    # 格式 4: 使用 user_id
    format4 = {
        'message_parts': [
            {
                'text': {
                    'content': test_message
                }
            }
        ],
        'message_type': 'normal',
        'actor_type': 'agent',
        'user_id': USER_ID
    }
    
    # 格式 5: 使用 actor_type: system
    format5 = {
        'message_parts': [
            {
                'text': {
                    'content': test_message
                }
            }
        ],
        'message_type': 'normal',
        'actor_type': 'system'
    }
    
    # 依次测试
    formats = [
        ("格式1: 最简单", format1),
        ("格式2: 带 message_type 和 actor_type", format2),
        ("格式3: 带 actor_id", format3),
        ("格式4: 带 user_id", format4),
        ("格式5: actor_type=system", format5),
    ]
    
    for name, body in formats:
        success = test_format(name, body)
        if success:
            print(f"\n🎉 找到可用格式: {name}")
            print("请在 Freshchat 中检查消息是否出现")
            break
        input("\n按 Enter 继续测试下一个格式...")
    
    print("\n" + "="*70)
    print("测试完成")
    print("="*70)
