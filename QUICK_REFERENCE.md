# 🚀 快速参考

## 立即开始（GitHub + Vercel）

```bash
# 1. 推送代码到 GitHub
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester
git init
git add .
git commit -m "Initial commit"
git remote add origin <你的GitHub仓库地址>
git push -u origin main

# 2. 在 Vercel 导入 GitHub 仓库
# 访问: https://vercel.com/new
# - Import Git Repository
# - 选择你的仓库
# - Root Directory: my-flask-webhook
# - Deploy

# 3. 配置环境变量（Vercel Dashboard）
# Settings → Environment Variables → 添加以下变量：

AGENT_BASE_URL=https://api-sg.gptbots.ai
AGENT_API_KEY=app-hhnASRDrU1qZZfSfQJICsXd1
FRESHCHAT_BASE_URL=https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2
FRESHCHAT_TOKEN=你的完整Token
FRESHCHAT_ACTOR_ID=2e6a98aa-5155-4b3e-9745-96a784e79eb2

# 4. 重新部署
# Deployments → Redeploy

# 5. 配置 Freshchat Webhook
# URL: https://你的域名.vercel.app/freshchat-webhook
# Events: message_create
```

## 常用命令

```bash
# 本地测试（需要先启动服务: python3 app.py）
cd my-flask-webhook
python3 test_full_flow.py

# Freshchat 诊断
python3 diagnose_freshchat.py

# 获取 Agent ID
python3 get_agents.py

# 查看 Vercel 日志
vercel logs https://你的域名.vercel.app --follow

# 测试 Vercel 部署（curl）
curl https://你的域名.vercel.app/health
curl https://你的域名.vercel.app/debug/conversations
```

## 可用端点

- `/health` - 健康检查
- `/freshchat-webhook` - Webhook 接收
- `/debug/conversations` - 会话映射状态
- `/webhooks` - Webhook 日志（Web界面）
- `/` - 主页
- `/agent` - Agent 测试页面
- `/chat` - 聊天测试页面

## 故障排查

| 问题 | 命令/方法 |
|------|----------|
| Token 验证 | `python3 diagnose_freshchat.py` |
| 本地完整测试 | `python3 test_full_flow.py` |
| Vercel 健康检查 | `curl https://你的域名.vercel.app/health` |
| 查看会话映射 | 访问 `/debug/conversations` |
| 获取 Agent ID | `python3 get_agents.py` |
| 查看 Vercel 日志 | Dashboard → Function Logs |

## 文档

- **README.md** - 项目概述、快速开始
- **DEPLOYMENT.md** - 详细部署指南（Vercel/本地）
- **TESTING.md** - 测试工具和流程
- **QUICK_REFERENCE.md** - 本文档
