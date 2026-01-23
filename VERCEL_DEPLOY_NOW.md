# 🚀 快速部署到 Vercel

## 当前代码已经可以在 Vercel 上自动运行！

### ✅ 已配置好的内容

1. **`vercel.json`** - Vercel 配置
2. **`requirements.txt`** - Python 依赖
3. **`runtime.txt`** - Python 版本
4. **`.vercelignore`** - 忽略文件

### 📋 部署步骤

#### 方式 1：通过 Vercel Dashboard（推荐）

1. 访问 [vercel.com](https://vercel.com)
2. 点击 **Import Project**
3. 导入你的 GitHub 仓库（或直接上传文件夹）
4. **Root Directory** 设置为：`my-flask-webhook`
5. 点击 **Deploy**

#### 方式 2：通过命令行

```bash
cd /Users/jiaqi/Desktop/GPTBots/apiwebhooktester
vercel --prod
```

### 🔧 必须设置的环境变量

在 Vercel Dashboard → Settings → Environment Variables 添加：

```bash
# GPTBots 配置
AGENT_BASE_URL=https://api-sg.gptbots.ai
AGENT_API_KEY=app-hhnASRDrU1qZZfSfQJICsXd1

# Freshchat 配置
FRESHCHAT_BASE_URL=https://zego-933915710582838602-cf5ef642f0f082017690489.freshchat.com/v2
FRESHCHAT_TOKEN=你的完整Token
FRESHCHAT_ACTOR_ID=2e6a98aa-5155-4b3e-9745-96a784e79eb2
FRESHCHAT_PUBLIC_KEY_PEM=你的Public Key（可选）
```

### 🎉 部署后自动执行

**部署完成后，系统会自动执行：**

1. ✅ Freshchat 发送 webhook → Vercel 自动启动 Function → 处理请求
2. ✅ 无需手动启动服务
3. ✅ 无需保持终端运行
4. ✅ 全球自动分发
5. ✅ 自动扩展

### 🔗 获取 Webhook URL

部署后，你的 webhook 地址是：

```
https://你的域名.vercel.app/freshchat-webhook
```

在 Freshchat 后台配置这个地址。

### ⚠️ 当前限制

**使用内存缓存的限制：**
- ⚠️ 会话映射可能在不同请求间丢失
- ⚠️ 同一用户可能创建多个 GPTBots 会话

**这不影响基本功能**，但会话连续性不稳定。

### 🎯 如果需要完美的会话连续性

参考 `VERCEL_KV_SETUP.md` 设置 Vercel KV (Redis)。

---

## ✅ 总结

**立即可以部署，会自动执行！** 🚀

基本功能完全正常：
- ✅ 接收 Freshchat 消息
- ✅ 调用 GPTBots AI
- ✅ 回复到 Freshchat

只是会话连续性可能不完美（可以后续优化）。
