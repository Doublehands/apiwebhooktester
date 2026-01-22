# 🚀 完整部署检查清单

## ✅ 第一步：更新 Vercel 环境变量

登录 Vercel Dashboard → 项目 `apiwebhooktester-z83n` → Settings → Environment Variables

### 必需的环境变量：

```bash
# GPTBots Agent API（已配置）
AGENT_BASE_URL=https://api-sg.gptbots.ai
AGENT_API_KEY=app-hhnASRDrU1qZZfSfQJICsXd1
AGENT_CONVERSATION_PATH=/v1/conversation
AGENT_SEND_PATH=/v2/conversation/message
AGENT_TIMEOUT=120

# Freshchat API（需要更新这些！）
FRESHCHAT_BASE_URL=https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2
FRESHCHAT_TOKEN=eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmcmVzaGNoYXQiLCJhdWQiOiJmcmVzaGNoYXQiLCJpYXQiOjE3Njg5Nzc5NDEsInNjb3BlIjoiYWdlbnQ6cmVhZCBhZ2VudDpjcmVhdGUgYWdlbnQ6dXBkYXRlIGFnZW50OmRlbGV0ZSBjb252ZXJzYXRpb246Y3JlYXRlIGNvbnZlcnNhdGlvbjpyZWFkIGNvbnZlcnNhdGlvbjp1cGRhdGUgbWVzc2FnZTpjcmVhdGUgbWVzc2FnZTpnZXQgYmlsbGluZzp1cGRhdGUgcmVwb3J0czpmZXRjaCByZXBvcnRzOmV4dHJhY3QgcmVwb3J0czpyZWFkIHJlcG9ydHM6ZXh0cmFjdDpyZWFkIGFjY291bnQ6cmVhZCBkYXNoYm9hcmQ6cmVhZCB1c2VyOnJlYWQgdXNlcjpjcmVhdGUgdXNlcjp1cGRhdGUgdXNlcjpkZWxldGUgb3V0Ym91bmRtZXNzYWdlOnNlbmQgb3V0Ym91bmRtZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6bWVzc2FnZTpzZW5kIG1lc3NhZ2luZy1jaGFubmVsczptZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6dGVtcGxhdGU6Y3JlYXRlIG1lc3NhZ2luZy1jaGFubmVsczp0ZW1wbGF0ZTpnZXQgZmlsdGVyaW5ib3g6cmVhZCBmaWx0ZXJpbmJveDpjb3VudDpyZWFkIHJvbGU6cmVhZCBpbWFnZTp1cGxvYWQiLCJ0eXAiOiJCZWFyZXIiLCJjbGllbnRJZCI6ImZjLTJmMjJiNzE0LWQ4NWEtNGUzZi04MjRlLTAzOWU5ZDE0NzZjNSIsInN1YiI6ImYxM2Y0YWZhLTc1OWQtNDVhMy04NmJkLWZjZTE2MTA3Y2UyOSIsImp0aSI6ImFkNWM4ZmIxLTBkNDctNGI4OS1iMTliLTM0MGI2MzZmYmQ0ZiIsImV4cCI6MjA4NDUxMDc0MX0.ob_D4Q_Tv_77MC-p97ibA7o3SPba9H_7tawM6LPJaPw
FRESHCHAT_ACTOR_ID=2e6a98aa-5155-4b3e-9745-96a784e79eb2
FRESHCHAT_PUBLIC_KEY_PEM=-----BEGIN RSA PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAusYrcp2XwG5A0B5V+D3niiJR5LDU+d6/UFBNdl9nUr1H2rkkKZaw3UOZKCumR8XPmqjD+YBE9uhJ63DT5RKgJAIpIqpIpJDgQvGszg3ELnPIO9BJ23vrNUljIpD2Wt/ojmvVu0T+cbBgf4hUL15g9Q0RFJbyH9ynbWC2PNQa+ajQOz39n2hwzQJ4TxxOALUs5zARW9RH8Vc/EtjrrXIOGfPDIw9+EdB8wH+IsXcDHkIDvOuQxegTxGMV1vecAAbe6VOOGlRSXkpeY0/8NNOJBYDp41nhPKwMK3mAA6NSO6LqeM1xNPvGb7vjm1IaL18mI9ltNlFixuWwgkEGNW3SOwIDAQAB
-----END RSA PUBLIC KEY-----
```

**⚠️ 重要：** Public Key 是多行的，在 Vercel 中直接粘贴（包含所有换行符）

---

## ✅ 第二步：重新部署

更新环境变量后：

1. 进入 Vercel Dashboard
2. 项目 → Deployments 标签
3. 最新部署 → 点击 `...` → Redeploy

---

## ✅ 第三步：测试完整流程

### 1. 在 Freshchat 发送新消息

发送一条新消息，比如：
```
你好，请介绍一下你自己
```

### 2. 查看 Vercel Function Logs

在 Vercel Dashboard 中：
- Deployments → 选择最新部署 → View Function Logs

应该看到详细的日志：
```
==================================================================
🔔 收到 Freshchat Webhook 请求
==================================================================
✅ 签名验证通过
...
✅ 成功提取消息信息:
   - Conversation ID: xxx
   - User ID: xxx
   - Message: 你好，请介绍一下你自己
==================================================================

🤖 开始调用 AI Agent...
💡 AI 回复: [Agent 的回复]

==================================================================
📤 准备发送回复到 Freshchat
==================================================================
Conversation ID: xxx
User ID: xxx
Response: [Agent 的回复]
Actor ID: 2e6a98aa-5155-4b3e-9745-96a784e79eb2
Token: eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI...
URL: https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2/conversations/xxx/messages
Body: {...}
==================================================================

✅ 成功发送回复到 Freshchat: xxx
```

### 3. 在 Freshchat 中查看

应该能看到 AI 的回复出现在对话中！

### 4. 查看 Webhook 日志

访问：`https://apiwebhooktester-z83n.vercel.app/webhooks`

查看完整的 webhook 数据和处理结果。

---

## 🐛 如果还是失败

查看 Vercel Function Logs 中的错误信息，特别是：

```
❌ 发送回复到 Freshchat 失败: [错误]
   状态码: [xxx]
   响应内容: [详细错误]
```

把这个错误信息发给我，我可以帮你排查。

---

## 📊 检查环境变量是否生效

部署后，访问：`https://apiwebhooktester-z83n.vercel.app/freshchat`

应该看到：
- FRESHCHAT_TOKEN: ✅ Set
- FRESHCHAT_ACTOR_ID: ✅ Set (如果配置了)
- FRESHCHAT_PUBLIC_KEY_PEM: ✅ Set (验证已启用)

---

现在去 Vercel 更新环境变量并重新部署，然后测试！告诉我结果！🚀