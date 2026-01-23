#!/usr/bin/env python3
"""
诊断脚本：检查 AI 回复为什么没有发送到 Freshchat
"""

import requests
import json
import os

# 配置（从环境变量或默认值获取）
FRESHCHAT_BASE_URL = os.environ.get(
    'FRESHCHAT_BASE_URL',
    'https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2'
).rstrip('/')
FRESHCHAT_TOKEN = os.environ.get('FRESHCHAT_TOKEN', 'eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6Ik')
FRESHCHAT_ACTOR_ID = os.environ.get('FRESHCHAT_ACTOR_ID', '2e6a98aa-5155-4b3e-9745-96a784e79eb2')

# 测试参数（从你的 webhook 日志中获取）
TEST_CONVERSATION_ID = "2669904a-a5b5-4516-a54c-b52c03ad155d"
TEST_USER_ID = "29a05a7f-7cd5-4928-9d1b-ddca7c3d0b8a"
TEST_MESSAGE = "这是测试回复消息"

def check_environment():
    """检查环境变量配置"""
    print("\n" + "="*70)
    print("🔍 步骤 1: 检查环境变量")
    print("="*70)
    
    issues = []
    
    print(f"✓ FRESHCHAT_BASE_URL: {FRESHCHAT_BASE_URL}")
    
    if len(FRESHCHAT_TOKEN) < 100:
        print(f"⚠️  FRESHCHAT_TOKEN 可能不完整: {FRESHCHAT_TOKEN[:50]}... (长度: {len(FRESHCHAT_TOKEN)})")
        issues.append("Token 长度异常")
    else:
        print(f"✓ FRESHCHAT_TOKEN: {FRESHCHAT_TOKEN[:50]}... (长度: {len(FRESHCHAT_TOKEN)})")
    
    print(f"✓ FRESHCHAT_ACTOR_ID: {FRESHCHAT_ACTOR_ID}")
    
    return len(issues) == 0, issues

def test_freshchat_api_connectivity():
    """测试 Freshchat API 连接"""
    print("\n" + "="*70)
    print("🔍 步骤 2: 测试 Freshchat API 连接")
    print("="*70)
    
    # 尝试获取 agents 列表来测试 API 连接
    url = f"{FRESHCHAT_BASE_URL}/agents"
    headers = {
        'Authorization': f'Bearer {FRESHCHAT_TOKEN}',
        'Content-Type': 'application/json',
    }
    
    print(f"请求 URL: {url}")
    print(f"Headers: Authorization: Bearer {FRESHCHAT_TOKEN[:30]}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API 连接成功")
            try:
                data = response.json()
                print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            except:
                print(f"响应内容: {response.text[:500]}")
            return True
        elif response.status_code == 401:
            print("❌ 认证失败 (401)")
            print(f"响应: {response.text}")
            print("\n可能的原因：")
            print("  1. Token 不正确或已过期")
            print("  2. Token 格式错误（应该是完整的 JWT，包含 3 部分用 . 分隔）")
            return False
        else:
            print(f"⚠️  API 返回错误状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_send_message():
    """测试发送消息到 Freshchat"""
    print("\n" + "="*70)
    print("🔍 步骤 3: 测试发送消息到 Freshchat")
    print("="*70)
    
    url = f"{FRESHCHAT_BASE_URL}/conversations/{TEST_CONVERSATION_ID}/messages"
    headers = {
        'Authorization': f'Bearer {FRESHCHAT_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'ASSUME-IDENTITY': 'false'
    }
    
    body = {
        'message_parts': [
            {
                'text': {
                    'content': TEST_MESSAGE
                }
            }
        ],
        'message_type': 'normal',
        'actor_type': 'agent',
        'user_id': TEST_USER_ID,
        'actor_id': FRESHCHAT_ACTOR_ID
    }
    
    print(f"请求 URL: {url}")
    print(f"Headers:")
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"  {key}: Bearer {FRESHCHAT_TOKEN[:30]}...")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n请求 Body:")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ 消息发送成功")
            try:
                data = response.json()
                print(f"响应数据:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print(f"响应内容: {response.text}")
            return True
        elif response.status_code == 404:
            print("❌ 找不到资源 (404)")
            print(f"响应: {response.text}")
            print("\n可能的原因：")
            print(f"  1. Conversation ID 不存在或已关闭: {TEST_CONVERSATION_ID}")
            print(f"  2. User ID 不正确: {TEST_USER_ID}")
            print(f"  3. Actor ID 不正确: {FRESHCHAT_ACTOR_ID}")
            return False
        elif response.status_code == 400:
            print("❌ 请求格式错误 (400)")
            print(f"响应: {response.text}")
            print("\n可能的原因：")
            print("  1. 请求 body 格式不正确")
            print("  2. 缺少必需字段")
            return False
        elif response.status_code == 401:
            print("❌ 认证失败 (401)")
            print(f"响应: {response.text}")
            return False
        else:
            print(f"⚠️  返回错误状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def get_conversation_details():
    """获取对话详情"""
    print("\n" + "="*70)
    print("🔍 步骤 4: 获取对话详情")
    print("="*70)
    
    url = f"{FRESHCHAT_BASE_URL}/conversations/{TEST_CONVERSATION_ID}"
    headers = {
        'Authorization': f'Bearer {FRESHCHAT_TOKEN}',
        'Content-Type': 'application/json',
    }
    
    print(f"请求 URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 获取对话详情成功")
            try:
                data = response.json()
                print(f"对话详情:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
                
                # 检查对话状态
                status = data.get('status')
                if status:
                    print(f"\n对话状态: {status}")
                    if status == 'resolved':
                        print("⚠️  对话已关闭！需要重新打开才能发送消息")
                
            except:
                print(f"响应内容: {response.text}")
            return True
        else:
            print(f"⚠️  无法获取对话详情: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("\n" + "🔬 Freshchat 消息发送诊断工具")
    print("="*70)
    
    # 检查环境变量
    env_ok, env_issues = check_environment()
    if not env_ok:
        print(f"\n⚠️  环境变量配置有问题: {', '.join(env_issues)}")
    
    # 测试 API 连接
    api_ok = test_freshchat_api_connectivity()
    if not api_ok:
        print("\n❌ API 连接失败，请先解决认证问题")
        return
    
    # 获取对话详情
    get_conversation_details()
    
    # 测试发送消息
    send_ok = test_send_message()
    
    print("\n" + "="*70)
    print("📊 诊断总结")
    print("="*70)
    print(f"环境变量配置: {'✅ 正常' if env_ok else '⚠️  有问题'}")
    print(f"API 连接: {'✅ 正常' if api_ok else '❌ 失败'}")
    print(f"消息发送: {'✅ 成功' if send_ok else '❌ 失败'}")
    
    if send_ok:
        print("\n✅ 一切正常！请检查 Freshchat 对话中是否收到消息")
        print(f"   对话 ID: {TEST_CONVERSATION_ID}")
    else:
        print("\n❌ 存在问题，请根据上面的错误信息进行排查")
        print("\n🔧 常见问题解决方案：")
        print("1. Token 错误 → 重新从 Freshchat 后台复制完整的 API Token")
        print("2. Conversation ID 不存在 → 使用最新的对话 ID（从 webhook 日志获取）")
        print("3. Actor ID 错误 → 运行 get_agents.py 获取正确的 Agent ID")
        print("4. 对话已关闭 → 在 Freshchat 中重新打开对话")

if __name__ == '__main__':
    main()
