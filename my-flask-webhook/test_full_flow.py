#!/usr/bin/env python3
"""
完整流程测试脚本
模拟 Freshchat 发送消息 → 接收 webhook → 调用 AI Agent → 发送回复到 Freshchat
"""

import requests
import json
import time

# 配置
WEBHOOK_URL = "http://localhost:5001/freshchat-webhook"
DEBUG_URL = "http://localhost:5001/debug/conversations"

# 模拟的 Freshchat 会话和用户
FRESHCHAT_CONVERSATION_ID = "test_conv_flow_001"
FRESHCHAT_USER_ID = "test_user_flow_001"

def send_test_message(message, message_id):
    """发送测试消息到 webhook"""
    print(f"\n{'='*70}")
    print(f"📤 发送测试消息: {message}")
    print(f"{'='*70}")
    
    webhook_data = {
        'action': 'message_create',
        'data': {
            'message': {
                'id': message_id,  # 唯一消息 ID
                'actor_type': 'user',
                'conversation_id': FRESHCHAT_CONVERSATION_ID,
                'user_id': FRESHCHAT_USER_ID,
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
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={
                'Content-Type': 'application/json',
                'X-Test-Mode': 'true'  # 测试模式，跳过签名验证
            },
            timeout=30
        )
        
        print(f"✅ Webhook 响应状态码: {response.status_code}")
        print(f"📦 响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        return response.json()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   响应内容: {e.response.text}")
        return None

def check_conversation_mappings():
    """检查当前的会话映射状态"""
    print(f"\n{'='*70}")
    print("🔍 检查会话映射状态")
    print(f"{'='*70}")
    
    try:
        response = requests.get(DEBUG_URL, timeout=10)
        print(f"✅ 获取会话映射状态成功")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json()
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_duplicate_message():
    """测试重复消息是否被正确忽略"""
    print(f"\n{'='*70}")
    print("🧪 测试重复消息处理")
    print(f"{'='*70}")
    
    message_id = "duplicate_test_msg_001"
    
    # 第一次发送
    print("\n第一次发送...")
    result1 = send_test_message("这是重复测试消息", message_id)
    
    time.sleep(2)
    
    # 第二次发送相同的 message_id
    print("\n第二次发送（应该被忽略）...")
    result2 = send_test_message("这是重复测试消息", message_id)
    
    if result2 and result2.get('status') == 'ignored':
        print("\n✅ 重复消息被正确忽略")
    else:
        print("\n⚠️  重复消息未被正确处理")
    
    return result1, result2

def test_conversation_continuity():
    """测试会话连续性"""
    print(f"\n{'='*70}")
    print("🧪 测试会话连续性（同一个 Freshchat 会话多条消息）")
    print(f"{'='*70}")
    
    messages = [
        ("你好，我是第一条消息", "continuity_msg_001"),
        ("这是第二条消息", "continuity_msg_002"),
        ("这是第三条消息", "continuity_msg_003")
    ]
    
    results = []
    gptbots_conversation_ids = []
    
    for i, (message, message_id) in enumerate(messages, 1):
        print(f"\n--- 第 {i} 条消息 ---")
        result = send_test_message(message, message_id)
        results.append(result)
        
        if result and result.get('gptbots_conversation_id'):
            gptbots_conversation_ids.append(result['gptbots_conversation_id'])
        
        time.sleep(3)  # 等待 AI 处理
    
    # 检查所有消息是否使用同一个 GPTBots 会话
    print(f"\n{'='*70}")
    print("📊 会话连续性检查结果:")
    print(f"{'='*70}")
    print(f"GPTBots 会话 IDs: {gptbots_conversation_ids}")
    
    if len(set(gptbots_conversation_ids)) == 1:
        print("✅ 所有消息使用同一个 GPTBots 会话（会话连续性正常）")
    else:
        print("⚠️  不同消息使用了不同的 GPTBots 会话（会话连续性异常）")
    
    return results

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 开始完整流程测试")
    print("="*70)
    
    # 1. 检查初始状态
    print("\n1️⃣ 检查初始状态")
    check_conversation_mappings()
    
    time.sleep(2)
    
    # 2. 测试单条消息
    print("\n2️⃣ 测试单条消息")
    send_test_message("你好，这是测试消息", "test_msg_001")
    
    time.sleep(5)
    
    # 3. 检查会话映射是否建立
    print("\n3️⃣ 检查会话映射")
    check_conversation_mappings()
    
    time.sleep(2)
    
    # 4. 测试重复消息
    print("\n4️⃣ 测试重复消息处理")
    test_duplicate_message()
    
    time.sleep(2)
    
    # 5. 测试会话连续性
    print("\n5️⃣ 测试会话连续性")
    test_conversation_continuity()
    
    time.sleep(2)
    
    # 6. 最终检查
    print("\n6️⃣ 最终状态检查")
    check_conversation_mappings()
    
    print("\n" + "="*70)
    print("✅ 所有测试完成")
    print("="*70)
