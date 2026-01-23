# 🚀 Vercel KV 持久化存储设置指南

## 为什么需要 Vercel KV？

Vercel Serverless Functions 是无状态的，内存缓存在不同请求间不共享。
使用 Vercel KV (Redis) 可以持久化存储会话映射，确保会话连续性。

## 📋 步骤

### 1. 在 Vercel Dashboard 创建 KV 数据库

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择你的项目
3. 点击 **Storage** 标签
4. 点击 **Create Database** → 选择 **KV** (Redis)
5. 输入数据库名称，如 `freshchat-sessions`
6. 点击 **Create**

### 2. 连接到项目

1. 在 KV 数据库页面，点击 **Connect to Project**
2. 选择你的项目
3. Vercel 会自动添加环境变量：
   - `KV_REST_API_URL`
   - `KV_REST_API_TOKEN`
   - `KV_REST_API_READ_ONLY_TOKEN`

### 3. 更新代码

安装依赖（已包含在 `requirements.txt`）：
```
vercel-kv==0.1.0
```

### 4. 重新部署

```bash
vercel --prod
```

## 💰 费用

**免费额度：**
- ✅ 256 MB 存储
- ✅ 3,000 次命令/天
- ✅ 100 万次读/写/月

对于你的使用场景，**免费额度完全足够**！

## 🎯 功能对比

| 功能 | 内存缓存 | Vercel KV |
|------|---------|-----------|
| 会话映射持久化 | ❌ 不稳定 | ✅ 稳定 |
| 消息去重 | ⚠️ 部分有效 | ✅ 完全有效 |
| 重启后保留 | ❌ 丢失 | ✅ 保留 |
| 跨实例共享 | ❌ 不共享 | ✅ 共享 |
| 设置难度 | 简单 | 中等 |

## ⚡ 性能影响

- Redis 读写延迟：< 10ms
- 对用户体验几乎无影响

## 🔍 验证

部署后访问：
```
https://你的域名.vercel.app/debug/conversations
```

会话映射应该在多次请求间保持一致。
