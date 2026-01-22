#!/usr/bin/env python3
"""测试完整的 Freshchat → GPTBots → Freshchat 流程"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_full_flow():
    """测试完整流程"""
    print("=" * 70)
    print("测试 Freshchat → GPTBots Agent → Freshchat 完整流程")
    print("=" * 70)
    
    # 1. 测试 Agent API 是否工作
    print("\n📍 步骤 1: 测试 GPTBots Agent API")
    print("-" * 70)
    
    agent_test_data = {
        'user_id': 'test_user',
        'message': '你好，请介绍一下你自己'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/agent/send",
            data=agent_test_data,
            timeout=130
        )
        
        if response.status_code == 200:
            print("✅ Agent API 测试成功")
            # 注意：这是 HTML 响应，不是 JSON
            print(f"   状态码: {response.status_code}")
        else:
            print(f"❌ Agent API 测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent API 测试失败: {e}")
        return False
    
    # 2. 测试 Freshchat 模拟
    print("\n📍 步骤 2: 测试 Freshchat AI 回复功能")
    print("-" * 70)
    
    freshchat_test_data = {
        'message': '你好，这是来自 Freshchat 的测试消息',
        'conversation_id': 'test_conv_123',
        'user_id': 'test_user_456'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/freshchat/test",
            data=freshchat_test_data,
            timeout=130
        )
        
        if response.status_code == 200:
            print("✅ Freshchat 测试成功")
            print(f"   状态码: {response.status_code}")
        else:
            print(f"❌ Freshchat 测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Freshchat 测试失败: {e}")
        return False
    
    # 3. 模拟 Freshchat Webhook 推送
    print("\n📍 步骤 3: 模拟 Freshchat Webhook 推送")
    print("-" * 70)
    
    webhook_payload = {
        "action": "message_create",
        "data": {
            "message": {
                "actor_type": "user",
                "conversation_id": "conv_test_12345",
                "user_id": "user_67890",
                "message_parts": [
                    {
                        "text": {
                            "content": "这是一条模拟的 Freshchat 用户消息"
                        }
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/freshchat-webhook",
            json=webhook_payload,
            headers={'Content-Type': 'application/json'},
            timeout=130
        )
        
        if response.status_code == 200:
            print("✅ Webhook 处理成功")
            result = response.json()
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Webhook 处理失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook 处理失败: {e}")
        return False
    
    # 4. 检查 Webhook 日志
    print("\n📍 步骤 4: 检查 Webhook 日志")
    print("-" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/webhooks", timeout=10)
        if response.status_code == 200:
            print("✅ Webhook 日志页面可访问")
            print(f"   访问 {BASE_URL}/webhooks 查看详细日志")
        else:
            print(f"⚠️  Webhook 日志页面状态: {response.status_code}")
    except Exception as e:
        print(f"⚠️  无法访问 Webhook 日志: {e}")
    
    print("\n" + "=" * 70)
    print("✅ 所有测试完成！")
    print("=" * 70)
    print(f"\n💡 提示:")
    print(f"   - 访问 {BASE_URL}/agent 测试 Agent API")
    print(f"   - 访问 {BASE_URL}/freshchat 测试 Freshchat 集成")
    print(f"   - 访问 {BASE_URL}/webhooks 查看 webhook 日志")
    print(f"\n📝 部署后需要在 Freshchat 后台配置:")
    print(f"   Webhook URL: https://your-domain.com/freshchat-webhook")
    print(f"   Event: message_create")
    print()
    
    return True

if __name__ == "__main__":
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务未运行，请先启动:")
            print("   cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester/my-flask-webhook")
            print("   source ../venv/bin/activate")
            print("   python app.py")
            exit(1)
    except Exception as e:
        print(f"❌ 无法连接到服务 ({BASE_URL})")
        print("   请确保服务已启动:")
        print("   cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester/my-flask-webhook")
        print("   source ../venv/bin/activate")
        print("   python app.py")
        exit(1)
    
    # 运行测试
    success = test_full_flow()
    exit(0 if success else 1)
