# API Webhook Tester

用于测试 AI Agent API 和 Webhook 的 Web 应用

## ✨ 新功能（v2.0）

### 🔗 会话 ID 映射与缓存
- ✅ 自动维护 Freshchat 和 GPTBots 之间的会话映射
- ✅ 确保同一 Freshchat 会话的多条消息使用同一 GPTBots 会话
- ✅ 保持对话上下文连续性

### 🚫 消息去重
- ✅ 防止重复消息被多次处理
- ✅ 基于 `message_id` 的去重机制
- ✅ 自动清理历史记录（保留最近 1000 条）

### 🔍 调试工具
- ✅ `/debug/conversations` - 查看当前会话映射状态
- ✅ `/webhooks` - 查看 webhook 日志
- ✅ 详细的控制台日志输出

## 快速启动

```bash
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester/my-flask-webhook
source ../venv/bin/activate
python app.py
```

服务启动后访问：
- **首页**: http://localhost:5001/
- **Agent 测试页**: http://localhost:5001/agent
- **实时聊天页**: http://localhost:5001/chat （嵌入 Freshchat 气泡）
- **Freshchat 配置页**: http://localhost:5001/freshchat
- **Webhook 日志页**: http://localhost:5001/webhooks
- **🆕 会话映射调试**: http://localhost:5001/debug/conversations

## 🧪 完整流程测试

运行自动化测试脚本：

```bash
cd my-flask-webhook
python test_full_flow.py
```

测试内容：
- ✅ 单条消息处理
- ✅ 会话映射创建
- ✅ 重复消息过滤
- ✅ 会话连续性验证

## 已配置的服务

### GPTBots API（新加坡节点）
- **Base URL**: `https://api-sg.gptbots.ai`
- **API Key**: `app-hhnASRDrU1qZZfSfQJICsXd1`
- **创建会话**: `/v1/conversation`
- **发送消息**: `/v2/conversation/message`

### Freshchat
- **Base URL**: `https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2`
- **Token**: `eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6Ik` (需要完整 Token)
- **Actor ID**: `gptbots_agent` (默认值，需替换为实际的 Freshchat Agent ID)
- **Webhook**: `/freshchat-webhook`

**⚠️ 重要：需要在 Freshchat 后台获取完整信息**
- 完整的 API Token（JWT 格式，包含 3 部分用 `.` 分隔）
- Agent ID（UUID 格式，如 `1de5d130-1c62-48cf-8349-1b39c60d0c28`）
- Public Key（可选，用于 Webhook 签名验证）

## 环境变量（可选覆盖）

```bash
export AGENT_BASE_URL="https://api-sg.gptbots.ai"
export AGENT_API_KEY="app-hhnASRDrU1qZZfSfQJICsXd1"
export AGENT_CONVERSATION_PATH="/v1/conversation"
export AGENT_SEND_PATH="/v2/conversation/message"
export AGENT_TIMEOUT="120"

# Freshchat 配置
export FRESHCHAT_BASE_URL="https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2"
export FRESHCHAT_TOKEN="your-complete-jwt-token"
export FRESHCHAT_ACTOR_ID="your-agent-id-uuid"
export FRESHCHAT_PUBLIC_KEY_PEM="-----BEGIN PUBLIC KEY-----..."  # 可选
```

## 检查 Freshchat 配置

运行配置检查脚本：

```bash
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester/my-flask-webhook
source ../venv/bin/activate
python check_freshchat_config.py
```

这个脚本会：
- ✅ 检查 Token 格式是否正确
- ✅ 测试 Freshchat API 连接
- ✅ 显示详细的配置指南
- ✅ 提供故障排除建议

## Webhook 回调地址

部署后需要在 Agent 后台配置：
- **Agent Webhook URL**: `https://your-domain.com/agent/webhook`
- **Freshchat Webhook URL**: `https://your-domain.com/freshchat-webhook`

## 使用流程

### 测试 Agent API
1. 访问 `/agent` 页面
2. 输入 `user_id` 和消息内容
3. 点击"发送消息"会自动创建会话并发送
4. 查看详细的请求和响应信息

### 测试 Freshchat 集成
1. 访问 `/freshchat` 页面
2. 在测试表单中输入消息
3. 点击"测试 AI 回复"查看 GPTBots Agent 的响应
4. 部署后在 Freshchat 后台配置 Webhook URL

### 查看 Webhook 日志
- 访问 `/webhooks` 页面查看所有接收到的 webhook 请求

## 本地测试 Freshchat 聊天气泡

由于 Freshchat 需要公网 URL 才能触发 webhook，本地测试需要使用 ngrok：

```bash
# 1. 安装 ngrok
brew install ngrok

# 2. 启动 ngrok（在另一个终端）
ngrok http 5001

# 3. 复制 ngrok 提供的 HTTPS URL，例如：
# https://abc123.ngrok.io

# 4. 在 Freshchat 后台配置 Webhook：
# URL: https://abc123.ngrok.io/freshchat-webhook
# Event: message_create
```

然后访问 http://localhost:5001/chat 测试聊天气泡。

## 注意事项

- 端口 5001（避免与 macOS AirPlay Receiver 冲突）
- 消息发送使用 `blocking` 模式，超时 120 秒
- Webhook 日志最多保留 200 条
- Freshchat 聊天气泡已嵌入 `/chat` 页面
- 本地测试需要 ngrok 等内网穿透工具

## 📚 详细文档

- **[完整集成指南](./INTEGRATION_GUIDE.md)** - 详细的架构说明、部署步骤、调试技巧
- **[Freshchat 认证指南](./FRESHCHAT_AUTH_GUIDE.md)** - Freshchat 配置和 API 使用
- **[Vercel 部署指南](./VERCEL_DEPLOYMENT.md)** - 部署到 Vercel 的完整步骤

## 🎯 工作流程

```
用户在 Freshchat 发送消息
    ↓
Freshchat Webhook → /freshchat-webhook
    ↓
验证签名 & 检查重复
    ↓
获取或创建 GPTBots 会话 ID（会话映射）
    ↓
调用 GPTBots API → 获取 AI 回复
    ↓
保存会话映射
    ↓
发送回复到 Freshchat → 用户收到 AI 回复
```

## 🔧 故障排查

### 查看会话映射状态
```bash
curl http://localhost:5001/debug/conversations
```

### 查看 Webhook 日志
访问 http://localhost:5001/webhooks

### 运行完整测试
```bash
cd my-flask-webhook
python test_full_flow.py
```
