# 🚀 Vercel 部署快速参考

## 📋 部署配置

### Root Directory
```
my-flask-webhook
```

### Framework Preset
```
Other 或 Python
```

---

## 🔑 环境变量（在 Vercel Dashboard 中配置）

```bash
# GPTBots Agent API
AGENT_BASE_URL=https://api-sg.gptbots.ai
AGENT_API_KEY=app-hhnASRDrU1qZZfSfQJICsXd1
AGENT_CONVERSATION_PATH=/v1/conversation
AGENT_SEND_PATH=/v2/conversation/message
AGENT_TIMEOUT=120

# Freshchat API
FRESHCHAT_BASE_URL=https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2
FRESHCHAT_TOKEN=你的完整JWT_Token
FRESHCHAT_ACTOR_ID=你的Agent_UUID
```

可选（签名验证）：
```bash
FRESHCHAT_PUBLIC_KEY_PEM=-----BEGIN PUBLIC KEY-----
MIIBIjAN...
-----END PUBLIC KEY-----
```

---

## 🌐 部署后的 Webhook URL

假设你的项目部署到：`https://your-project.vercel.app`

### Freshchat Webhook（在 Freshchat 后台配置）
```
https://your-project.vercel.app/freshchat-webhook
```

### Agent Webhook（在 GPTBots 后台配置，可选）
```
https://your-project.vercel.app/agent/webhook
```

---

## 📄 访问页面

- 首页: `https://your-project.vercel.app/`
- Agent 测试: `https://your-project.vercel.app/agent`
- Live Chat: `https://your-project.vercel.app/chat`
- Freshchat 配置: `https://your-project.vercel.app/freshchat`
- Webhook 日志: `https://your-project.vercel.app/webhooks`
- 健康检查: `https://your-project.vercel.app/health`

---

## ✅ 部署检查步骤

1. ☐ 访问首页，确认服务运行正常
2. ☐ 访问 `/agent` 测试发送消息功能
3. ☐ 在 Freshchat 后台配置 Webhook URL
4. ☐ 在 Freshchat 发送测试消息
5. ☐ 访问 `/webhooks` 查看是否收到 webhook
6. ☐ 确认 AI 回复是否发送到 Freshchat

---

## 🐛 快速故障排除

| 问题 | 解决方法 |
|------|----------|
| 部署失败 | 检查 `requirements.txt` 和 `runtime.txt` |
| 404 错误 | 确认 Root Directory 设置为 `my-flask-webhook` |
| 环境变量无效 | 在 Vercel 重新部署项目 |
| Webhook 无响应 | 检查 Vercel 函数日志和 URL 配置 |
| AI 超时 | Vercel Hobby 限制 10 秒，考虑升级计划 |

---

## 📞 需要的 Freshchat 信息

从 Freshchat 后台获取：

1. **完整 API Token** (JWT 格式，包含 2 个 `.`)
   - 位置: Settings → API Settings → API Tokens
   
2. **Agent ID** (UUID 格式)
   - 位置: Settings → Team → Agents
   - 示例: `1de5d130-1c62-48cf-8349-1b39c60d0c28`

3. **Public Key** (可选，PEM 格式)
   - 位置: Settings → Webhooks
