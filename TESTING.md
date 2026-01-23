# 🧪 测试指南

## 测试工具概览

| 工具 | 用途 | 运行环境 |
|------|------|----------|
| `test_full_flow.py` | 完整流程测试 | 本地 → 本地服务 |
| `diagnose_freshchat.py` | Freshchat API 诊断 | 本地 → Freshchat API |
| `get_agents.py` | 获取 Freshchat Agents | 本地 → Freshchat API |

---

## 1. 本地测试

### 前提条件

```bash
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester/my-flask-webhook

# 确保服务正在运行
python3 app.py  # 在另一个终端运行
```

### 测试 1: 完整流程测试

**用途**: 测试消息接收、AI 处理、回复发送、会话映射、消息去重

**运行**:
```bash
python3 test_full_flow.py
```

**测试内容**:
1. ✅ 检查初始状态
2. ✅ 发送单条消息
3. ✅ 检查会话映射创建
4. ✅ 测试重复消息处理
5. ✅ 测试会话连续性（3条消息）

**预期输出**:
```
🚀 开始完整流程测试
======================================================================

1️⃣ 检查初始状态
✅ 获取会话映射状态成功
...

2️⃣ 测试单条消息
✅ Webhook 响应状态码: 200
...

5️⃣ 测试会话连续性
✅ 所有消息使用同一个 GPTBots 会话（会话连续性正常）

✅ 所有测试完成
```

### 测试 2: Freshchat API 诊断

**用途**: 诊断 Freshchat API 连接、Token、发送消息功能

**运行**:
```bash
python3 diagnose_freshchat.py
```

**测试内容**:
1. ✅ 检查环境变量配置
2. ✅ 测试 Freshchat API 连接
3. ✅ 获取对话详情
4. ✅ 测试发送消息到 Freshchat

**预期输出**:
```
🔬 Freshchat 消息发送诊断工具
======================================================================

🔍 步骤 1: 检查环境变量
✓ FRESHCHAT_BASE_URL: https://...
✓ FRESHCHAT_TOKEN: ... (长度: 500+)
✓ FRESHCHAT_ACTOR_ID: 2e6a98aa-...

🔍 步骤 2: 测试 Freshchat API 连接
✅ API 连接成功

🔍 步骤 3: 测试发送消息到 Freshchat
✅ 消息发送成功

📊 诊断总结
✅ 环境变量配置: 正常
✅ API 连接: 正常
✅ 消息发送: 成功
```

**常见错误**:

| 错误 | 原因 | 解决 |
|------|------|------|
| `401 Unauthorized` | Token 错误 | 重新复制完整 Token |
| `404 Not Found` | Conversation/Actor ID 错误 | 检查 ID 是否正确 |
| `JWT signature does not match` | Token 格式错误 | 确保复制完整，不要多余字符 |

---

## 2. Vercel 部署后测试

### 方式 1: Web 界面测试

#### 健康检查

访问: `https://你的域名.vercel.app/health`

预期: `{"status":"ok"}`

#### 会话映射状态

访问: `https://你的域名.vercel.app/debug/conversations`

预期显示当前会话映射和已处理消息数

#### Webhook 日志

访问: `https://你的域名.vercel.app/webhooks`

查看最近 200 条 webhook 请求

### 方式 2: 命令行测试

#### 健康检查

```bash
curl https://你的域名.vercel.app/health
```

预期: `{"status":"ok"}`

#### 会话映射状态

```bash
curl https://你的域名.vercel.app/debug/conversations | jq
```

预期:
```json
{
  "conversation_mappings": {
    "count": 0,
    "mappings": []
  },
  "processed_messages": {
    "count": 0,
    "recent": []
  }
}
```

#### 模拟 Webhook 测试

```bash
curl -X POST https://你的域名.vercel.app/freshchat-webhook \
  -H "Content-Type: application/json" \
  -H "X-Test-Mode: true" \
  -d '{
    "action": "message_create",
    "data": {
      "message": {
        "id": "test_msg_001",
        "actor_type": "user",
        "conversation_id": "test_conv_001",
        "user_id": "test_user_001",
        "message_parts": [
          {
            "text": {
              "content": "你好，这是测试消息"
            }
          }
        ]
      }
    }
  }'
```

预期: 返回包含 `status: success` 和 AI 回复内容

---

## 3. 端到端测试（Freshchat）

### 测试步骤

1. **打开 Freshchat 聊天窗口**
   - 访问集成了 Freshchat 的网站
   - 点击聊天图标

2. **发送测试消息**
   ```
   你好，这是测试
   ```

3. **观察响应时间**
   - 应该在 3-5 秒内收到 AI 回复

4. **发送第二条消息**
   ```
   我刚才问了什么？
   ```

5. **验证会话连续性**
   - AI 应该能记住之前的对话内容

### 查看日志

#### Vercel Function Logs

1. Vercel Dashboard → 项目
2. Deployments → 最新部署
3. Function Logs 标签

**成功的日志示例**:
```
======================================================================
🔔 收到 Freshchat Webhook 请求
======================================================================
📊 当前会话映射数量: 0
📊 已处理消息数量: 0
👤 Actor Type: user
💬 Conversation ID: 2669904a-...
🆔 User ID: 29a05a7f-...
📝 Message: 你好，这是测试

🆕 为 Freshchat 会话创建新的 GPTBots 会话
🤖 开始调用 AI Agent...
💡 AI 回复: 你好！有什么可以帮你的吗？

📤 准备发送回复到 Freshchat...
🔄 正在发送 HTTP POST 请求...
📥 收到响应:
   HTTP 状态码: 200
✅ 成功发送回复到 Freshchat

✅ 完整流程处理成功
======================================================================
```

#### 命令行查看日志

```bash
vercel logs https://你的域名.vercel.app --follow
```

---

## 4. 故障排查

### 问题 1: AI 回复未发送到 Freshchat

**诊断步骤**:

1. **运行 Freshchat 诊断**:
```bash
python3 diagnose_freshchat.py
```

2. **检查 Vercel Function Logs**:
- 查找 `❌ 发送回复到 Freshchat 失败`
- 查看详细错误信息

3. **常见错误处理**:

| 日志关键词 | 原因 | 解决 |
|-----------|------|------|
| `401 Unauthorized` | Token 错误 | 更新 `FRESHCHAT_TOKEN` 环境变量 |
| `404 Not Found` | Conversation/Actor ID 错误 | 检查 `FRESHCHAT_ACTOR_ID` |
| `400 Bad Request` | 请求格式错误 | 检查日志中的请求 body |
| `Function timeout` | AI 响应慢 | 升级 Vercel Pro 或优化 AI |

### 问题 2: Webhook 未触发

**检查项**:
- Freshchat Webhook 配置中是否选择了 `message_create` 事件
- Webhook URL 是否正确: `https://你的域名.vercel.app/freshchat-webhook`
- Webhook 状态是否为 Active

### 问题 3: 会话连续性问题

**测试步骤**:

1. 发送第一条消息: `你好`
2. 查看会话映射:
```bash
curl https://你的域名.vercel.app/debug/conversations
```
3. 发送第二条消息: `我刚才说了什么？`
4. 再次查看会话映射

**预期**: 两条消息使用同一个 GPTBots conversation_id

**说明**: Vercel Serverless 环境下，内存缓存可能不稳定。如需完美的会话连续性，参考 DEPLOYMENT.md 中的 Vercel KV 方案。

---

## 5. 工具脚本说明

### get_agents.py

**用途**: 获取 Freshchat 中所有 Agents 的 ID

**运行**:
```bash
python3 get_agents.py
```

**输出示例**:
```
Freshchat Agents:
==================
1. Jacky Lee
   ID: 2e6a98aa-5155-4b3e-9745-96a784e79eb2
   Email: jacky@example.com
   Status: active

2. Support Bot
   ID: 1de5d130-1c62-48cf-8349-1b39c60d0c28
   Email: bot@example.com
   Status: active
```

**使用**: 复制你的 Agent ID 作为 `FRESHCHAT_ACTOR_ID` 环境变量

---

## 6. 测试清单

### 部署前（本地测试）

- [ ] 本地服务启动成功 (`python3 app.py`)
- [ ] `test_full_flow.py` 全部通过
- [ ] `diagnose_freshchat.py` 显示连接正常
- [ ] 获取正确的 `FRESHCHAT_ACTOR_ID`

### 部署到 Vercel 后

- [ ] 代码已推送到 GitHub
- [ ] Vercel 已连接 GitHub 仓库
- [ ] Root Directory 设置为 `my-flask-webhook`
- [ ] 所有环境变量已配置
- [ ] 触发部署成功，无构建错误

### 部署验证

- [ ] `/health` 返回 200
- [ ] `/debug/conversations` 正常工作
- [ ] 模拟 webhook 测试成功（curl 命令）
- [ ] Freshchat Webhook 已配置（URL、Events、Active）

### 端到端测试

- [ ] 从 Freshchat 发送消息收到 AI 回复
- [ ] 连续对话会话连续性正常
- [ ] Vercel Function Logs 无错误
- [ ] `/webhooks` 页面显示日志记录

---

## 7. 监控建议

### 日常监控

```bash
# 健康检查
curl https://你的域名.vercel.app/health

# 会话映射状态
curl https://你的域名.vercel.app/debug/conversations

# 查看最近日志
vercel logs https://你的域名.vercel.app --since 1h
```

### Vercel 监控

在 Vercel Dashboard 查看：
- Function 错误率
- Function 响应时间
- Function 调用次数

---

**更新日期**: 2026-01-23
