#!/usr/bin/env python3
"""检查和测试 Freshchat API 配置"""
import requests
import json

# 配置信息
FRESHCHAT_BASE_URL = "https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2"
FRESHCHAT_TOKEN = "eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6Ik"

def check_token_format():
    """检查 Token 格式"""
    print("=" * 70)
    print("📋 检查 Freshchat Token 格式")
    print("=" * 70)
    
    print(f"\n当前 Token: {FRESHCHAT_TOKEN[:50]}...")
    print(f"Token 长度: {len(FRESHCHAT_TOKEN)} 字符")
    
    # JWT Token 通常有 3 部分，用 . 分隔
    parts = FRESHCHAT_TOKEN.split('.')
    print(f"Token 部分数: {len(parts)}")
    
    if len(parts) == 3:
        print("✅ Token 格式看起来正确（标准 JWT 格式）")
        print(f"   - Header: {parts[0][:30]}...")
        print(f"   - Payload: {parts[1][:30]}...")
        print(f"   - Signature: {parts[2][:30]}...")
    elif len(parts) == 1:
        print("⚠️  Token 可能不完整（缺少 . 分隔符）")
        print("   请检查是否复制了完整的 Token")
    else:
        print(f"⚠️  Token 格式异常（有 {len(parts)} 部分）")
    
    return len(parts) == 3

def test_freshchat_api():
    """测试 Freshchat API 连接"""
    print("\n" + "=" * 70)
    print("🔧 测试 Freshchat API 连接")
    print("=" * 70)
    
    # 测试 API - 尝试获取会话列表（只是测试连接）
    test_url = f"{FRESHCHAT_BASE_URL}/conversations"
    headers = {
        'Authorization': f'Bearer {FRESHCHAT_TOKEN}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'ASSUME-IDENTITY': 'false'
    }
    
    print(f"\n📡 测试 URL: {test_url}")
    print(f"📤 Headers:")
    print(f"   - Authorization: Bearer {FRESHCHAT_TOKEN[:20]}...")
    print(f"   - Accept: application/json")
    print(f"   - ASSUME-IDENTITY: false")
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        
        print(f"\n📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API 连接成功！")
            try:
                data = response.json()
                print(f"   返回数据: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                return True
            except:
                print(f"   响应内容: {response.text[:200]}...")
                return True
        elif response.status_code == 401:
            print("❌ 认证失败 (401 Unauthorized)")
            print("   可能的原因：")
            print("   1. Token 不完整或过期")
            print("   2. Token 权限不足")
            print("   3. Token 格式错误")
            print(f"\n   响应内容: {response.text}")
            return False
        elif response.status_code == 403:
            print("❌ 禁止访问 (403 Forbidden)")
            print("   可能的原因：")
            print("   1. Token 没有访问此资源的权限")
            print("   2. API 功能未启用")
            print(f"\n   响应内容: {response.text}")
            return False
        else:
            print(f"⚠️  收到意外状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：无法连接到 Freshchat 服务器")
        print("   请检查：")
        print("   1. 网络连接是否正常")
        print("   2. Base URL 是否正确")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def show_configuration_guide():
    """显示配置指南"""
    print("\n" + "=" * 70)
    print("📖 Freshchat 配置指南")
    print("=" * 70)
    
    print("\n🔑 需要的配置信息：")
    print("\n1. API Token (Bearer Token)")
    print("   在哪里找：")
    print("   - 登录 Freshchat 后台")
    print("   - Settings → API Settings → API Tokens")
    print("   - 创建或复制现有的 API Token")
    print("   - 完整的 Token 应该很长，包含 3 部分（用 . 分隔）")
    
    print("\n2. Actor ID (Agent ID)")
    print("   在哪里找：")
    print("   - Settings → Team → Agents")
    print("   - 查看或创建一个 Agent")
    print("   - 复制 Agent 的 ID（UUID 格式）")
    print("   - 示例: 1de5d130-1c62-48cf-8349-1b39c60d0c28")
    
    print("\n3. Public Key (可选，用于 Webhook 签名验证)")
    print("   在哪里找：")
    print("   - Settings → Webhooks → Verification")
    print("   - 复制 Public Key (PEM 格式)")
    
    print("\n4. Webhook URL 配置")
    print("   需要在 Freshchat 后台配置：")
    print("   - URL: https://your-domain.com/freshchat-webhook")
    print("   - Event: message_create 或 message.created")
    print("   - Method: POST")

def show_current_config():
    """显示当前配置"""
    print("\n" + "=" * 70)
    print("⚙️  当前配置")
    print("=" * 70)
    
    print(f"\nFRESHCHAT_BASE_URL: {FRESHCHAT_BASE_URL}")
    print(f"FRESHCHAT_TOKEN: {FRESHCHAT_TOKEN[:30]}...{FRESHCHAT_TOKEN[-10:]}")
    print(f"Token 完整性: {'✅ 可能完整' if '.' in FRESHCHAT_TOKEN else '❌ 可能不完整'}")

def main():
    print("\n" + "🔍 " * 20)
    print(" " * 20 + "Freshchat 配置检查工具")
    print("🔍 " * 20 + "\n")
    
    show_current_config()
    
    # 1. 检查 Token 格式
    token_ok = check_token_format()
    
    if not token_ok:
        print("\n⚠️  警告: Token 格式可能不完整")
        print("   建议: 请从 Freshchat 后台复制完整的 API Token")
    
    # 2. 测试 API 连接
    api_ok = test_freshchat_api()
    
    # 3. 显示配置指南
    if not api_ok:
        show_configuration_guide()
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 检查结果")
    print("=" * 70)
    print(f"Token 格式: {'✅ 正常' if token_ok else '❌ 异常'}")
    print(f"API 连接: {'✅ 成功' if api_ok else '❌ 失败'}")
    
    if token_ok and api_ok:
        print("\n✅ 所有检查通过！Freshchat 配置正确。")
        print("\n下一步：")
        print("1. 确保已配置 Actor ID (FRESHCHAT_ACTOR_ID)")
        print("2. 在 Freshchat 后台配置 Webhook URL")
        print("3. 启动服务并测试完整流程")
    else:
        print("\n❌ 配置检查失败，请根据上面的指引修复。")
        print("\n需要帮助？")
        print("- 确保从 Freshchat 后台复制了完整的 API Token")
        print("- 确保 Token 有发送消息的权限")
        print("- 查看上面的配置指南了解详细步骤")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
