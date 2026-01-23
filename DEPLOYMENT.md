# 🚀 部署指南

## 📋 部署方式

支持两种部署方式：
1. **Vercel Serverless** (推荐) - 自动扩展、全球CDN
2. **本地/服务器部署** - 完全控制、持久化缓存

---

## 方式 1: Vercel 部署（推荐）

### 准备工作

确保以下文件存在：
- ✅ `my-flask-webhook/vercel.json`
- ✅ `my-flask-webhook/requirements.txt`
- ✅ `my-flask-webhook/runtime.txt`

### 部署步骤

#### 选项 A: 命令行部署

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 进入项目目录
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester

# 3. 部署
vercel --prod

# 4. 按提示操作
# - Root directory: my-flask-webhook  ← 重要！
# - 其他保持默认
```

#### 选项 B: Dashboard 部署

1. 访问 https://vercel.com/new
2. 导入项目（GitHub 或上传文件）
3. **Root Directory** 设置为 `my-flask-webhook`
4. **Framework Preset** 选择 `Other`
5. 点击 **Deploy**

### 配置环境变量

部署完成后，在 Vercel Dashboard 中配置：

**路径**: 项目 → Settings → Environment Variables

**必需变量**:
```bash
AGENT_BASE_URL=https://api-sg.gptbots.ai
AGENT_API_KEY=app-hhnASRDrU1qZZfSfQJICsXd1
FRESHCHAT_BASE_URL=https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2
FRESHCHAT_TOKEN=你的完整JWT Token
FRESHCHAT_ACTOR_ID=2e6a98aa-5155-4b3e-9745-96a784e79eb2
```

**可选变量**:
```bash
FRESHCHAT_PUBLIC_KEY_PEM=-----BEGIN RSA PUBLIC KEY-----...
```

**重要**: 添加环境变量后，触发 **Redeploy**！

### 获取必需信息

#### 1. Freshchat Token

1. Freshchat Dashboard → Settings → API Tokens
2. 创建或查看现有 Token
3. 复制完整的 JWT Token（很长，包含3部分用`.`分隔）

#### 2. Freshchat Actor ID

```bash
cd my-flask-webhook
python3 get_agents.py
```

从输出中找到你的 Agent（如 Jacky Lee），复制其 ID。

#### 3. Freshchat Public Key（可选）

配置 Webhook 后，Freshchat 会返回 Public Key 用于签名验证。

---

## 方式 2: 本地/服务器部署

### 1. 安装依赖

```bash
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
cd my-flask-webhook
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件或导出环境变量：

```bash
export AGENT_BASE_URL="https://api-sg.gptbots.ai"
export AGENT_API_KEY="app-hhnASRDrU1qZZfSfQJICsXd1"
export FRESHCHAT_BASE_URL="https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2"
export FRESHCHAT_TOKEN="你的完整Token"
export FRESHCHAT_ACTOR_ID="2e6a98aa-5155-4b3e-9745-96a784e79eb2"
```

### 3. 启动服务

```bash
python3 app.py
```

服务将在 `http://localhost:5001` 启动。

### 4. 公网访问（使用 ngrok）

本地开发时需要公网 URL 供 Freshchat 调用：

```bash
# 安装 ngrok
brew install ngrok  # macOS
# 或访问 https://ngrok.com 下载

# 启动 ngrok
ngrok http 5001
```

使用 ngrok 提供的 HTTPS URL 配置 Freshchat Webhook。

---

## 配置 Freshchat Webhook

### 步骤

1. 登录 Freshchat Dashboard
2. 导航到 **Settings** → **Webhooks**
3. 点击 **Create Webhook** 或编辑现有 Webhook

### 配置

- **Name**: GPTBots Integration
- **URL**: 
  - Vercel: `https://你的域名.vercel.app/freshchat-webhook`
  - 本地: `https://your-ngrok-id.ngrok.io/freshchat-webhook`
- **Events**: ✅ `message_create`
- **Status**: Active

### 保存

保存后，Freshchat 会返回 Public Key，用于 Webhook 签名验证。

---

## Vercel 特殊配置

### 1. 持久化存储（可选）

**问题**: Vercel Serverless 环境下，内存缓存不稳定

**影响**: 会话映射可能丢失，导致创建多个 GPTBots 会话

**解决**: 使用 Vercel KV (Redis)

#### 设置 Vercel KV

1. Vercel Dashboard → Storage → Create Database → KV
2. 输入数据库名称（如 `freshchat-sessions`）
3. 点击 Create
4. 连接到你的项目

Vercel 会自动添加环境变量：
- `KV_REST_API_URL`
- `KV_REST_API_TOKEN`
- `KV_REST_API_READ_ONLY_TOKEN`

#### 更新代码（可选实现）

在 `app.py` 中使用 Vercel KV 替代内存缓存：

```python
from vercel_kv import KV

kv = KV.from_env()

# 保存会话映射
kv.set(f"conv:{freshchat_conv_id}", gptbots_conv_id)

# 获取会话映射
gptbots_conv_id = kv.get(f"conv:{freshchat_conv_id}")
```

**费用**: 免费额度（256MB、3000次/天）足够使用

### 2. 超时设置

Vercel 免费版 Function 超时 10秒，Pro 版 60秒。

如果 AI Agent 响应慢：
- 升级到 Vercel Pro
- 或优化 AI Agent 响应时间

---

## 部署验证

### 1. 健康检查

```bash
curl https://你的域名.vercel.app/health
# 预期: {"status": "ok"}
```

### 2. 调试端点

```bash
curl https://你的域名.vercel.app/debug/conversations
# 预期: {"conversation_mappings": {...}, "processed_messages": {...}}
```

### 3. 自动化测试

```bash
cd my-flask-webhook
python3 test_vercel_deployment.py https://你的域名.vercel.app
```

---

## 更新部署

### Vercel 更新

```bash
# 命令行
vercel --prod

# 或 Dashboard
# Deployments → 最新部署 → Redeploy
```

### 本地更新

```bash
git pull  # 如果使用 Git
# 或直接修改代码

# 重启服务
# Ctrl+C 停止
python3 app.py  # 重新启动
```

---

## 配置文件说明

### vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### requirements.txt

```txt
Flask==3.1.2
requests==2.32.5
cryptography==46.0.3
```

### runtime.txt

```txt
python-3.11
```

---

## 环境变量完整列表

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `AGENT_BASE_URL` | ✅ | - | GPTBots API 地址 |
| `AGENT_API_KEY` | ✅ | - | GPTBots API 密钥 |
| `AGENT_CONVERSATION_PATH` | ❌ | `/v1/conversation` | 创建会话路径 |
| `AGENT_SEND_PATH` | ❌ | `/v2/conversation/message` | 发送消息路径 |
| `AGENT_TIMEOUT` | ❌ | `120` | API 超时（秒） |
| `FRESHCHAT_BASE_URL` | ✅ | - | Freshchat API 地址 |
| `FRESHCHAT_TOKEN` | ✅ | - | Freshchat JWT Token |
| `FRESHCHAT_ACTOR_ID` | ✅ | - | Freshchat Agent ID |
| `FRESHCHAT_PUBLIC_KEY_PEM` | ⚠️ | - | Webhook 签名验证公钥 |

---

## 安全建议

1. **启用签名验证**: 配置 `FRESHCHAT_PUBLIC_KEY_PEM`
2. **使用 HTTPS**: Vercel 自动提供，本地使用 ngrok
3. **保护环境变量**: 不要提交到 Git
4. **定期更新 Token**: 定期轮换 API Token
5. **监控日志**: 定期检查 Vercel Function Logs

---

## 故障排除

### 部署失败

**错误**: `Build failed`

**检查**:
- Root Directory 是否设为 `my-flask-webhook`
- `requirements.txt` 格式是否正确
- Python 版本是否支持（3.11）

### 环境变量未生效

**症状**: API 调用失败

**解决**:
1. 检查环境变量拼写
2. 确认已点击 Save
3. 触发 Redeploy

### 502/504 错误

**原因**: Function 超时或崩溃

**解决**:
- 查看 Function Logs 的详细错误
- 检查 AI Agent 是否正常
- 考虑升级 Vercel Pro

---

**更新日期**: 2026-01-23
