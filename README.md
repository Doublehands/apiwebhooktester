# 🚀 Freshchat + GPTBots 集成

## 📋 项目概述

这是一个将 Freshchat 与 GPTBots AI Agent 集成的 Webhook 服务。用户在 Freshchat 中发送消息后，系统会自动调用 AI Agent 并将回复发送回 Freshchat。

### 核心功能

- ✅ 接收 Freshchat Webhook 消息
- ✅ 调用 GPTBots AI Agent 获取回复
- ✅ 自动维护会话映射（Freshchat ↔ GPTBots）
- ✅ 消息去重（防止重复处理）
- ✅ 发送 AI 回复到 Freshchat
- ✅ 详细日志和调试工具

### 📚 文档导航

- **[README.md](./README.md)** - 项目概述和快速开始（本文档）
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - 详细部署指南（Vercel/本地）
- **[TESTING.md](./TESTING.md)** - 测试指南和工具说明

---

## ⚡ 快速部署（5分钟）

### 步骤 1: 部署到 Vercel

```bash
# 安装 Vercel CLI
npm install -g vercel

# 进入项目目录
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester

# 部署
vercel --prod

# 重要：Root Directory 选择 my-flask-webhook
```

### 步骤 2: 配置环境变量

在 **Vercel Dashboard** → 项目 → **Settings** → **Environment Variables** 添加：

```bash
# GPTBots 配置
AGENT_BASE_URL=https://api-sg.gptbots.ai
AGENT_API_KEY=app-hhnASRDrU1qZZfSfQJICsXd1

# Freshchat 配置
FRESHCHAT_BASE_URL=https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2
FRESHCHAT_TOKEN=你的完整JWT Token
FRESHCHAT_ACTOR_ID=2e6a98aa-5155-4b3e-9745-96a784e79eb2
FRESHCHAT_PUBLIC_KEY_PEM=-----BEGIN RSA PUBLIC KEY-----...（可选）
```

**添加后务必点击 Redeploy！**

### 步骤 3: 配置 Freshchat Webhook

1. Freshchat Dashboard → **Settings** → **Webhooks**
2. 添加 Webhook：
   - URL: `https://你的域名.vercel.app/freshchat-webhook`
   - Events: ✅ `message_create`
   - Status: Active
3. 保存

### 步骤 4: 测试

在 Freshchat 聊天窗口发送消息，应该在 3-5 秒内收到 AI 回复。

---

## 📁 项目结构

```
apiwebhooktester/
├── my-flask-webhook/           # 主应用目录
│   ├── app.py                  # Flask 应用主文件
│   ├── vercel.json             # Vercel 配置
│   ├── requirements.txt        # Python 依赖
│   ├── runtime.txt             # Python 版本
│   ├── templates/              # HTML 模板
│   │   ├── home.html           # 主页
│   │   ├── agent.html          # Agent 测试页
│   │   ├── webhooks.html       # Webhook 日志页
│   │   ├── freshchat.html      # Freshchat 配置页
│   │   └── chat.html           # 聊天测试页
│   ├── test_full_flow.py       # 完整流程测试（本地）
│   ├── diagnose_freshchat.py   # Freshchat API 诊断
│   └── get_agents.py           # 获取 Freshchat Agents
├── README.md                   # 项目概述（本文档）
├── DEPLOYMENT.md               # 部署指南
├── TESTING.md                  # 测试指南
└── QUICK_REFERENCE.md          # 快速参考
```

---

## 🔧 环境变量说明

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `AGENT_BASE_URL` | ✅ | GPTBots API 地址 |
| `AGENT_API_KEY` | ✅ | GPTBots API 密钥 |
| `FRESHCHAT_BASE_URL` | ✅ | Freshchat API 地址 |
| `FRESHCHAT_TOKEN` | ✅ | Freshchat JWT Token |
| `FRESHCHAT_ACTOR_ID` | ✅ | Freshchat Agent ID |
| `FRESHCHAT_PUBLIC_KEY_PEM` | ⚠️ | Webhook 签名验证公钥（推荐） |

---

## 🌐 可用端点

部署后可访问以下端点：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/freshchat-webhook` | POST | Freshchat Webhook 接收 |
| `/debug/conversations` | GET | 查看会话映射状态 |
| `/webhooks` | GET | 查看 Webhook 日志 |
| `/` | GET | 主页 |
| `/agent` | GET | Agent API 测试页面 |
| `/chat` | GET | Freshchat 聊天测试页面 |

---

## 🔍 监控和调试

### 查看实时日志

**Vercel Dashboard**:
1. 项目 → Deployments → 最新部署 → Function Logs

**命令行**:
```bash
vercel logs https://你的域名.vercel.app --follow
```

### 查看会话映射

```bash
curl https://你的域名.vercel.app/debug/conversations | jq
```

### 查看 Webhook 日志

访问: `https://你的域名.vercel.app/webhooks`

---

## ⚠️ 常见问题

### 1. AI 回复未发送到 Freshchat

**症状**: AI 能处理消息但 Freshchat 未收到回复

**解决方案**:
```bash
# 运行诊断工具
cd my-flask-webhook
python3 diagnose_freshchat.py
```

常见原因：
- Token 不完整或错误 → 重新复制完整 Token
- Conversation 已关闭 → 在 Freshchat 中重新打开
- Actor ID 错误 → 运行 `python3 get_agents.py` 获取正确 ID

### 2. Webhook 未触发

**检查**:
- Freshchat Webhook 配置中是否选择了 `message_create` 事件
- Webhook URL 是否正确
- Webhook 状态是否为 Active

### 3. 会话连续性问题

**说明**: Vercel Serverless 环境下，内存缓存可能不稳定

**影响**: 同一用户可能创建多个 GPTBots 会话

**解决**: 参考 `DEPLOYMENT.md` 中的 Vercel KV 持久化方案（可选）

---

## 📚 详细文档

需要更多信息？查看以下文档：

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - 详细部署指南
  - Vercel 部署步骤
  - 本地部署方法
  - 环境变量配置
  - Vercel KV 持久化设置
  - 配置文件说明

- **[TESTING.md](./TESTING.md)** - 测试指南
  - 本地测试工具
  - Vercel 部署测试
  - 端到端测试流程
  - 故障排查步骤
  - 性能测试方法

---

## 🎯 工作流程

```
用户在 Freshchat 发送消息
    ↓
Freshchat Webhook → /freshchat-webhook
    ↓
验证签名 & 检查消息去重
    ↓
获取或创建 GPTBots 会话 ID（会话映射）
    ↓
调用 GPTBots AI Agent → 获取回复
    ↓
保存会话映射
    ↓
发送回复到 Freshchat
    ↓
用户收到 AI 回复
```

---

## 🆘 需要帮助？

如果遇到问题，请提供：
1. Vercel 部署 URL
2. Vercel Function Logs 输出
3. 运行诊断工具的结果

---

**版本**: v2.0  
**更新日期**: 2026-01-23
