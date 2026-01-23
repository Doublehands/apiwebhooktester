# 🔗 Freshchat + GPTBots 集成完整指南

## 📋 系统架构

```
Freshchat (用户) → Webhook → 您的服务器 → GPTBots AI Agent
                      ↓                        ↓
                   验证签名                  处理消息
                      ↓                        ↓
                  会话映射                  生成回复
                      ↓                        ↓
            Freshchat API ← ← ← ← ← ← ← 返回结果
```

## 🎯 核心功能

### 1. 会话 ID 映射与缓存

系统使用内存缓存来维护 Freshchat 和 GPTBots 之间的会话映射：

```python
CONVERSATION_MAPPING = {}  # Freshchat conversation_id → GPTBots conversation_id
```

**工作原理：**
- 当收到第一条来自 Freshchat 的消息时，系统会创建新的 GPTBots 会话
- 会话 ID 被保存到 `CONVERSATION_MAPPING` 中
- 后续来自同一 Freshchat 会话的消息会使用相同的 GPTBots 会话 ID
- 这确保了对话上下文的连续性

### 2. 消息去重

防止同一条消息被处理多次：

```python
PROCESSED_MESSAGES = {}  # 存储已处理的消息 ID
```

**工作原理：**
- 每条 Freshchat 消息都有唯一的 `message_id`
- 在处理消息前检查 `message_id` 是否已存在
- 已处理的消息直接返回 `ignored` 状态
- 自动清理机制：只保留最近 1000 条消息记录

### 3. 完整处理流程

```
1. 接收 Webhook
   ↓
2. 验证签名（可选）
   ↓
3. 检查消息去重
   ↓
4. 提取消息内容
   ↓
5. 获取或创建 GPTBots 会话
   ↓
6. 调用 AI Agent
   ↓
7. 保存会话映射
   ↓
8. 提取 AI 回复
   ↓
9. 发送到 Freshchat
   ↓
10. 返回处理结果
```

## 🚀 部署步骤

### 本地测试

1. **启动服务：**

```bash
cd my-flask-webhook
python app.py
```

服务将运行在 `http://localhost:5001`

2. **运行完整流程测试：**

```bash
python test_full_flow.py
```

测试脚本会自动验证：
- ✅ 单条消息处理
- ✅ 会话映射创建
- ✅ 重复消息过滤
- ✅ 会话连续性（多条消息使用同一会话）

3. **查看会话映射状态：**

```bash
curl http://localhost:5001/debug/conversations
```

### Vercel 部署

1. **确保配置文件已就绪：**
   - ✅ `vercel.json`
   - ✅ `requirements.txt`
   - ✅ `runtime.txt`
   - ✅ `.vercelignore`

2. **设置环境变量（在 Vercel Dashboard）：**

```bash
AGENT_BASE_URL=https://api-sg.gptbots.ai
AGENT_API_KEY=app-你的密钥
FRESHCHAT_BASE_URL=https://你的域名.freshchat.com/v2
FRESHCHAT_TOKEN=eyJra...你的完整Token
FRESHCHAT_ACTOR_ID=2e6a98aa-5155-4b3e-9745-96a784e79eb2
FRESHCHAT_PUBLIC_KEY_PEM=-----BEGIN RSA PUBLIC KEY-----...-----END RSA PUBLIC KEY-----
```

3. **部署到 Vercel：**

```bash
# 在项目根目录
vercel --prod
```

或通过 Vercel Dashboard 导入 GitHub 仓库自动部署

4. **配置 Freshchat Webhook：**

在 Freshchat Dashboard 中设置：
- **Webhook URL**: `https://你的域名.vercel.app/freshchat-webhook`
- **Events**: 选择 `message_create`
- **保存配置** → 系统会返回 Public Key（用于签名验证）

## 🔧 环境变量说明

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `AGENT_BASE_URL` | ✅ | GPTBots API 基础 URL | `https://api-sg.gptbots.ai` |
| `AGENT_API_KEY` | ✅ | GPTBots API 密钥 | `app-xxxxx` |
| `FRESHCHAT_BASE_URL` | ✅ | Freshchat API 基础 URL | `https://xxx.freshchat.com/v2` |
| `FRESHCHAT_TOKEN` | ✅ | Freshchat API Token (JWT) | `eyJraWQiOiJj...` |
| `FRESHCHAT_ACTOR_ID` | ✅ | Freshchat Agent ID | UUID 格式 |
| `FRESHCHAT_PUBLIC_KEY_PEM` | ⚠️ | Freshchat Webhook 签名验证公钥 | PEM 格式 |

**注意：**
- `FRESHCHAT_PUBLIC_KEY_PEM` 不是必需的，但强烈推荐用于生产环境
- 如果不配置，签名验证会被跳过
- 测试时可以使用 `X-Test-Mode: true` header 跳过签名验证

## 🔍 调试工具

### 1. 查看 Webhook 日志

访问：`http://你的域名/webhooks`

显示最近 200 条 webhook 请求的详细信息

### 2. 查看会话映射

```bash
curl https://你的域名.vercel.app/debug/conversations
```

返回：
```json
{
  "conversation_mappings": {
    "count": 5,
    "mappings": [
      {
        "freshchat_conversation_id": "2669904a-...",
        "gptbots_conversation_id": "conv_abc123"
      }
    ]
  },
  "processed_messages": {
    "count": 12,
    "recent": ["msg_001", "msg_002", ...]
  }
}
```

### 3. 测试 Webhook 接收

访问：`http://你的域名/webhook-test`

可以手动构造测试数据并发送到 webhook 端点

## 📊 监控与日志

### 控制台日志格式

```
======================================================================
🔔 收到 Freshchat Webhook 请求
======================================================================
📊 当前会话映射数量: 5
📊 已处理消息数量: 12
👤 Actor Type: user
💬 Conversation ID: 2669904a-...
🆔 User ID: 29a05a7f-...
📝 Message ID: 9eb5ef67-...
📝 Message: 你好

🔗 使用已存在的 GPTBots 会话: conv_abc123
🤖 开始调用 AI Agent...
💡 AI 回复: 你好！有什么可以帮你的吗？

📤 准备发送回复到 Freshchat...
✅ 成功发送回复到 Freshchat

✅ 完整流程处理成功
   - Freshchat 会话: 2669904a-...
   - GPTBots 会话: conv_abc123
   - 用户消息: 你好
   - AI 回复: 你好！有什么可以帮你的吗？
======================================================================
```

### Vercel Function Logs

在 Vercel Dashboard → 项目 → Deployments → 点击部署 → Function Logs

可以看到实时的函数执行日志

## ⚠️ 常见问题

### 1. 消息重复发送到 AI Agent

**原因：** Freshchat 可能会重发 webhook，或者会话映射未正确保存

**解决方案：**
- ✅ 已实现消息去重机制（`PROCESSED_MESSAGES`）
- ✅ 已实现会话 ID 映射（`CONVERSATION_MAPPING`）

### 2. AI 回复未返回到 Freshchat

**检查项：**
1. `FRESHCHAT_TOKEN` 是否正确
2. `FRESHCHAT_ACTOR_ID` 是否正确（必须是真实存在的 Agent ID）
3. 查看 Vercel Function Logs 中的详细错误信息

**获取正确的 Actor ID：**
```bash
cd my-flask-webhook
python get_agents.py
```

### 3. Freshchat Webhook 签名验证失败

**测试时：** 使用 `X-Test-Mode: true` header 跳过验证

**生产环境：**
1. 确保 `FRESHCHAT_PUBLIC_KEY_PEM` 格式正确（包含完整的 `-----BEGIN/END-----` 标记）
2. 检查 Freshchat 配置中的 Public Key 与环境变量是否一致

### 4. 会话映射丢失（重启后）

**原因：** 当前使用内存缓存，服务重启后会丢失

**临时方案：** Vercel Serverless Functions 在一定时间内保持"热"状态

**长期方案（可选）：**
- 使用 Redis 等持久化存储
- 使用数据库（PostgreSQL、MongoDB）

## 🎉 验收测试清单

在 Freshchat 聊天窗口中测试以下场景：

- [ ] 发送第一条消息，AI 能正确回复
- [ ] 在同一会话中发送第二条消息，AI 回复包含上下文（证明会话连续性）
- [ ] 刷新页面重新加载聊天，发送消息仍能保持会话上下文
- [ ] 在 `/webhooks` 页面查看 webhook 日志
- [ ] 在 `/debug/conversations` 查看会话映射
- [ ] 运行 `test_full_flow.py` 全部测试通过

## 📝 下一步优化建议

1. **添加持久化存储**
   - 使用 Redis 或数据库存储会话映射
   - 防止服务重启导致会话丢失

2. **添加错误重试机制**
   - AI Agent 调用失败时自动重试
   - Freshchat 回复失败时记录并告警

3. **添加监控和告警**
   - 接入 Sentry 监控错误
   - 设置 Webhook 失败率告警

4. **性能优化**
   - 异步处理 AI 调用
   - 实现消息队列（RabbitMQ、Redis Queue）

5. **安全加固**
   - 强制启用签名验证（生产环境）
   - 添加 Rate Limiting
   - 实现 IP 白名单

---

**更新日期**: 2026-01-23  
**版本**: v2.0  
**维护者**: Cursor AI Assistant
