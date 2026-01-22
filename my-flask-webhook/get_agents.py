#!/usr/bin/env python3
"""获取 Freshchat Agents 列表，找到正确的 actor_id"""
import requests
import json

FRESHCHAT_BASE_URL = "https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2"
FRESHCHAT_TOKEN = "eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmcmVzaGNoYXQiLCJhdWQiOiJmcmVzaGNoYXQiLCJpYXQiOjE3Njg5Nzc5NDEsInNjb3BlIjoiYWdlbnQ6cmVhZCBhZ2VudDpjcmVhdGUgYWdlbnQ6dXBkYXRlIGFnZW50OmRlbGV0ZSBjb252ZXJzYXRpb246Y3JlYXRlIGNvbnZlcnNhdGlvbjpyZWFkIGNvbnZlcnNhdGlvbjp1cGRhdGUgbWVzc2FnZTpjcmVhdGUgbWVzc2FnZTpnZXQgYmlsbGluZzp1cGRhdGUgcmVwb3J0czpmZXRjaCByZXBvcnRzOmV4dHJhY3QgcmVwb3J0czpyZWFkIHJlcG9ydHM6ZXh0cmFjdDpyZWFkIGFjY291bnQ6cmVhZCBkYXNoYm9hcmQ6cmVhZCB1c2VyOnJlYWQgdXNlcjpjcmVhdGUgdXNlcjp1cGRhdGUgdXNlcjpkZWxldGUgb3V0Ym91bmRtZXNzYWdlOnNlbmQgb3V0Ym91bmRtZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6bWVzc2FnZTpzZW5kIG1lc3NhZ2luZy1jaGFubmVsczptZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6dGVtcGxhdGU6Y3JlYXRlIG1lc3NhZ2luZy1jaGFubmVsczp0ZW1wbGF0ZTpnZXQgZmlsdGVyaW5ib3g6cmVhZCBmaWx0ZXJpbmJveDpjb3VudDpyZWFkIHJvbGU6cmVhZCBpbWFnZTp1cGxvYWQiLCJ0eXAiOiJCZWFyZXIiLCJjbGllbnRJZCI6ImZjLTJmMjJiNzE0LWQ4NWEtNGUzZi04MjRlLTAzOWU5ZDE0NzZjNSIsInN1YiI6ImYxM2Y0YWZhLTc1OWQtNDVhMy04NmJkLWZjZTE2MTA3Y2UyOSIsImp0aSI6ImFkNWM4ZmIxLTBkNDctNGI4OS1iMTliLTM0MGI2MzZmYmQ0ZiIsImV4cCI6MjA4NDUxMDc0MX0.ob_D4Q_Tv_77MC-p97ibA7o3SPba9H_7tawM6LPJaPw"

def get_agents():
    """获取 Agents 列表"""
    url = f"{FRESHCHAT_BASE_URL}/agents"
    headers = {
        'Authorization': f'Bearer {FRESHCHAT_TOKEN}',
        'Accept': 'application/json'
    }
    
    print("="*70)
    print("📋 获取 Freshchat Agents 列表")
    print("="*70)
    print(f"URL: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 成功获取 Agents 列表:\n")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 提取 agent IDs
            if 'agents' in data:
                print("\n" + "="*70)
                print("📝 可用的 Agent IDs:")
                print("="*70)
                for agent in data['agents']:
                    agent_id = agent.get('id')
                    agent_name = agent.get('first_name', '') + ' ' + agent.get('last_name', '')
                    print(f"  - ID: {agent_id}")
                    print(f"    Name: {agent_name.strip()}")
                    print(f"    Email: {agent.get('email', 'N/A')}")
                    print()
            return data
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def get_conversation_details(conversation_id):
    """获取会话详情，看看里面有什么信息"""
    url = f"{FRESHCHAT_BASE_URL}/conversations/{conversation_id}"
    headers = {
        'Authorization': f'Bearer {FRESHCHAT_TOKEN}',
        'Accept': 'application/json'
    }
    
    print("\n" + "="*70)
    print(f"📋 获取 Conversation 详情")
    print("="*70)
    print(f"URL: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 会话详情:\n")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"❌ 请求失败")
            print(f"响应: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

if __name__ == "__main__":
    print("\n🔍 Freshchat API 信息查询")
    print("="*70)
    
    # 1. 获取 Agents 列表
    agents = get_agents()
    
    # 2. 获取会话详情
    conversation_id = "2669904a-a5b5-4516-a54c-b52c03ad155d"
    conv_details = get_conversation_details(conversation_id)
    
    print("\n" + "="*70)
    print("查询完成")
    print("="*70)
    print("\n💡 提示:")
    print("  - 使用上面列出的 Agent ID 作为 actor_id")
    print("  - 确保 user_id 来自 webhook 数据")
    print("="*70 + "\n")
