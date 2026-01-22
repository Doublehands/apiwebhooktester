# Vercel 部署指南

## 🚀 部署步骤

### 1. 准备工作
确保你已经：
- ✅ 创建了 Vercel 账号
- ✅ 安装了 Vercel CLI（可选）
- ✅ 准备好所有环境变量

### 2. Vercel 项目配置

#### Root Directory（根目录）
选择：**`my-flask-webhook`**

#### Framework Preset
选择：**Other** 或 **Python**

#### Build Settings
- Build Command: (留空)
- Output Directory: (留空)
- Install Command: `pip install -r requirements.txt`

### 3. 配置环境变量

在 Vercel 项目设置中添加以下环境变量：

#### GPTBots Agent API
```
AGENT_BASE_URL = https://api-sg.gptbots.ai
AGENT_API_KEY = app-hhnASRDrU1qZZfSfQJICsXd1
AGENT_CONVERSATION_PATH = /v1/conversation
AGENT_SEND_PATH = /v2/conversation/message
AGENT_TIMEOUT = 120
```

#### Freshchat API
```
FRESHCHAT_BASE_URL = https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2
FRESHCHAT_TOKEN = <你的完整JWT Token>
FRESHCHAT_ACTOR_ID = <你的Agent UUID>
FRESHCHAT_PUBLIC_KEY_PEM = <可选: PEM格式的Public Key>
```

**⚠️ 重要：**
- 环境变量名必须完全匹配
- Token 和 Key 不要加引号
- 如果 Public Key 是多行的，在 Vercel 中直接粘贴（包含换行符）

### 4. 部署

#### 方式 A：通过 Vercel Dashboard（推荐）
1. 登录 [vercel.com](https://vercel.com)
2. 点击 "Add New Project"
3. 导入你的 GitHub 仓库（或上传代码）
4. Root Directory 选择：`my-flask-webhook`
5. 添加环境变量（见上面）
6. 点击 "Deploy"

#### 方式 B：通过 Vercel CLI
```bash
# 安装 Vercel CLI
npm install -g vercel

# 在项目目录中
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester/my-flask-webhook

# 登录
vercel login

# 部署
vercel
```

### 5. 部署后获取 Webhook URL

部署成功后，Vercel 会提供一个 URL，例如：
```
https://your-project-name.vercel.app
```

#### Webhook 地址

你需要在对应平台配置以下 Webhook URL：

**Freshchat Webhook:**
```
https://your-project-name.vercel.app/freshchat-webhook
```

**Agent Webhook:**
```
https://your-project-name.vercel.app/agent/webhook
```

**测试页面:**
- 首页: `https://your-project-name.vercel.app/`
- Agent 测试: `https://your-project-name.vercel.app/agent`
- Live Chat: `https://your-project-name.vercel.app/chat`
- Webhook 日志: `https://your-project-name.vercel.app/webhooks`

---

## 🔧 配置 Freshchat Webhook

### 步骤

1. **登录 Freshchat 后台**

2. **进入 Webhook 设置**
   - 路径：Settings → Webhooks → Add Webhook

3. **配置 Webhook**
   ```
   Webhook URL: https://your-project-name.vercel.app/freshchat-webhook
   Events: message_create (或 message.created)
   Method: POST
   Content-Type: application/json
   ```

4. **保存并测试**
   - 在 Freshchat 中发送一条测试消息
   - 访问 `https://your-project-name.vercel.app/webhooks` 查看日志
   - 检查是否收到 webhook 请求

---

## 🔧 配置 GPTBots Agent Webhook（可选）

如果你需要 Agent 主动推送消息到你的服务：

1. **登录 GPTBots 后台**

2. **进入 Webhook 设置**
   - 路径：Agent → Integration → API → Webhook

3. **配置 Webhook**
   ```
   Webhook URL: https://your-project-name.vercel.app/agent/webhook
   Events: 勾选需要的事件
   Method: POST
   ```

---

## ✅ 部署检查清单

部署完成后，检查以下项目：

### 1. 服务可访问性
- [ ] 访问 `https://your-project-name.vercel.app/` 显示首页
- [ ] 访问 `/health` 返回 `{"status": "ok"}`

### 2. 环境变量
- [ ] 在首页查看 Agent API 配置状态（应显示 Ready）
- [ ] 在 `/freshchat` 页面查看 Freshchat 配置状态

### 3. API 功能
- [ ] 在 `/agent` 页面测试发送消息
- [ ] 检查是否能成功创建会话
- [ ] 检查是否能收到 Agent 回复

### 4. Webhook 功能
- [ ] 在 Freshchat 发送测试消息
- [ ] 在 `/webhooks` 页面查看是否收到 webhook
- [ ] 检查是否有 AI 回复发送到 Freshchat

---

## 🐛 常见问题

### 1. 部署失败："No Python version specified"
**解决：** 创建 `runtime.txt` 文件
```bash
echo "python-3.11" > runtime.txt
```

### 2. 部署成功但访问 404
**解决：** 检查 `vercel.json` 配置和 Root Directory 设置

### 3. 环境变量不生效
**解决：**
- 确保在 Vercel Dashboard 中正确添加了环境变量
- 重新部署项目（环境变量更改后需要重新部署）

### 4. Webhook 收不到请求
**解决：**
- 确认 Webhook URL 正确（必须是 HTTPS）
- 检查 Freshchat 后台的 Webhook 配置
- 查看 Vercel 日志：Dashboard → Deployments → Logs

### 5. 函数超时
**解决：**
- Vercel Hobby 计划函数超时时间为 10 秒
- Pro 计划可以设置更长的超时时间
- 对于 AI 响应，确保 `blocking` 模式能在超时前完成

---

## 📊 监控和日志

### 查看 Vercel 日志
1. 进入 Vercel Dashboard
2. 选择项目
3. 点击 "Deployments"
4. 选择一个部署
5. 点击 "View Function Logs"

### 查看应用内日志
访问 `/webhooks` 页面查看所有 webhook 请求日志（最多保留 200 条）

---

## 🔒 安全建议

1. **启用 Freshchat 签名验证**
   - 配置 `FRESHCHAT_PUBLIC_KEY_PEM` 环境变量
   - 确保 webhook 请求来自 Freshchat

2. **不要在代码中硬编码敏感信息**
   - 所有 Token 和 Key 都应通过环境变量配置

3. **定期更新依赖**
   ```bash
   pip list --outdated
   ```

---

## 📝 文件清单

确保以下文件存在于 `my-flask-webhook` 目录：

- ✅ `app.py` - 主应用文件
- ✅ `vercel.json` - Vercel 配置
- ✅ `requirements.txt` - Python 依赖
- ✅ `.vercelignore` - 忽略文件配置
- ✅ `templates/` - HTML 模板文件夹

---

## 🎯 下一步

1. **完成部署**
   - 按照上面的步骤部署到 Vercel

2. **获取 Webhook URL**
   - 记录 Vercel 提供的项目 URL

3. **配置 Freshchat**
   - 在 Freshchat 后台添加 Webhook URL

4. **测试完整流程**
   - 在 Freshchat 发送消息
   - 检查是否收到 AI 回复
   - 查看 webhook 日志

5. **监控和优化**
   - 定期查看 Vercel 日志
   - 根据实际使用情况优化超时设置
