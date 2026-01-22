# Freshchat 鉴权配置完整指南

## 📋 需要的配置信息

### 1. API Token (Bearer Token) ✅ 部分完成
**当前值：** `eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6Ik`

**问题：** 这个 Token 看起来不完整，完整的 JWT Token 应该有 3 部分，用 `.` 分隔。

**在哪里获取：**
```
Freshchat 后台 → Settings → API Settings → API Tokens
```

**Token 格式示例：**
```
eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**权限要求：**
- ✅ 读取消息
- ✅ 发送消息
- ✅ 访问会话

### 2. Actor ID (Agent ID) ⚠️ 需要提供
**当前值：** `gptbots_agent` (默认占位符)

**在哪里获取：**
```
Freshchat 后台 → Settings → Team → Agents
```

**格式：** UUID 格式
**示例：** `1de5d130-1c62-48cf-8349-1b39c60d0c28`

**作用：** 标识在 Freshchat 中发送消息的 Agent 身份

### 3. Base URL ✅ 已完成
**当前值：** `https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2`

### 4. Public Key (可选) ⚠️ 未配置
**在哪里获取：**
```
Freshchat 后台 → Settings → Webhooks → Public Key
```

**格式：** PEM 格式
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
```

**作用：** 验证 Freshchat 发送的 Webhook 签名，确保请求来自 Freshchat

---

## 🔧 API 调用格式（已实现）

### 发送消息到 Freshchat
```python
POST https://<account>.freshchat.com/v2/conversations/{conversation_id}/messages

Headers:
  - Authorization: Bearer {FRESHCHAT_TOKEN}
  - Content-Type: application/json
  - Accept: application/json
  - ASSUME-IDENTITY: false

Body:
{
  "message_parts": [
    {
      "text": {
        "content": "消息内容"
      }
    }
  ],
  "message_type": "normal",
  "actor_type": "agent",
  "actor_id": "{FRESHCHAT_ACTOR_ID}",
  "user_id": "{user_id}"
}
```

---

## ✅ 配置检查步骤

### 1. 运行配置检查脚本
```bash
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester/my-flask-webhook
source ../venv/bin/activate
python check_freshchat_config.py
```

这个脚本会：
- 检查 Token 格式
- 测试 API 连接
- 显示错误信息和建议

### 2. 预期结果

**如果配置正确：**
```
✅ Token 格式正常
✅ API 连接成功
✅ 所有检查通过！
```

**如果配置不完整：**
```
❌ Token 格式异常（可能不完整）
❌ API 连接失败 (401 Unauthorized)
```

---

## 📝 需要在 Freshchat 后台配置的内容

### Webhook 配置
```
路径: Settings → Webhooks → Add Webhook

配置项:
  - Webhook URL: https://your-domain.com/freshchat-webhook
  - Events: message_create (或 message.created)
  - Method: POST
  - Content-Type: application/json
```

### 本地测试（使用 ngrok）
```bash
# 1. 启动服务
python app.py

# 2. 在另一个终端启动 ngrok
ngrok http 5001

# 3. 复制 ngrok HTTPS URL（例如 https://abc123.ngrok.io）

# 4. 在 Freshchat 配置 Webhook
#    URL: https://abc123.ngrok.io/freshchat-webhook
```

---

## 🔍 故障排除

### 问题 1: 401 Unauthorized
**原因：**
- Token 不完整
- Token 已过期
- Token 权限不足

**解决：**
1. 在 Freshchat 后台重新复制完整的 API Token
2. 确保 Token 有发送消息的权限
3. 检查 Token 是否过期，如需要则重新生成

### 问题 2: 403 Forbidden
**原因：**
- Actor ID 不存在
- Token 没有操作该资源的权限

**解决：**
1. 确认 Actor ID 是否正确
2. 检查 Token 的权限设置

### 问题 3: 消息发送失败
**原因：**
- conversation_id 不存在
- user_id 不匹配

**解决：**
1. 确保 conversation_id 来自真实的 Freshchat 会话
2. 确保 user_id 与会话关联

---

## 📊 当前配置状态

| 配置项 | 状态 | 说明 |
|--------|------|------|
| Base URL | ✅ 完成 | `https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2` |
| API Token | ⚠️ 部分 | 需要完整的 JWT Token（包含 3 部分） |
| Actor ID | ⚠️ 需要 | 需要真实的 Agent UUID |
| Public Key | ⚠️ 可选 | 生产环境建议配置 |

---

## 🚀 下一步

1. **获取完整的 API Token**
   - 登录 Freshchat 后台
   - 复制完整的 Token（应该很长，包含 2 个 `.`）

2. **获取 Agent ID**
   - 在 Freshchat 查看或创建 Agent
   - 复制 UUID 格式的 ID

3. **更新配置**
   ```bash
   export FRESHCHAT_TOKEN="完整的Token"
   export FRESHCHAT_ACTOR_ID="真实的Agent ID"
   ```

4. **测试配置**
   ```bash
   python check_freshchat_config.py
   ```

5. **启动服务并测试完整流程**
   ```bash
   python app.py
   # 访问 http://localhost:5001/chat 测试
   ```

---

## 💡 提示

- Token 通常以 `eyJ` 开头
- 完整的 JWT Token 非常长（通常 > 200 字符）
- Actor ID 是 UUID 格式：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- 生产环境务必配置 Public Key 进行签名验证
