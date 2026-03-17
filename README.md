# 投票系统使用指南

## 📋 系统功能

✅ **防刷功能** — 每个人只能投票一次，刷新后系统会记住已投票身份
✅ **实时统计** — 投票结果实时显示在统计页面
✅ **数据持久化** — 所有投票数据永久保存在 `votes.json`

---

## 🚀 启动步骤

### 1️⃣ 安装依赖
```bash
npm install
```

### 2️⃣ 启动后端服务
```bash
node server.js
```

你会看到：
```
✅ 投票服务器运行在 http://localhost:8900
📊 查看统计结果: http://localhost:8900/stats.html
```

### 3️⃣ 启动前端静态服务
在另一个终端窗口运行：
```bash
# 如果已有 Python
python -m http.server 8899

# 或使用 Node.js
npx http-server . -p 8899
```

### 4️⃣ 打开投票页面
- **投票页面**: http://localhost:8899/vote.html
- **统计页面**: http://localhost:8899/stats.html

---

## 🎯 工作流程

### 投票流程
1. 打开 `vote.html`
2. 在下拉框选择您的名字 👤
3. 给"最佳员工"投 1 票 ⭐
4. 给"优秀团队"投 1 票 👥
5. 点击"提交我的投票" ✨
6. 系统检查是否重复投票
7. 投票成功后，界面被禁用，无法再投

### 查看统计
1. 打开 `stats.html`
2. 页面自动每 5 秒刷新一次统计数据
3. 显示各项目的投票排行

---

## 📊 文件说明

| 文件 | 用途 |
|------|------|
| `server.js` | 后端投票服务器（Node.js + Express） |
| `vote.html` | 投票页面（防刷防重复） |
| `stats.html` | 统计结果页面（实时更新） |
| `votes.json` | 投票数据存储文件（自动生成） |
| `package.json` | 项目依赖配置 |

---

## 🔧 API 接口

### 提交投票
```
POST /api/vote
Content-Type: application/json

{
  "voter": "张三",
  "best_employee": "李四",
  "best_team": "护栏一队"
}

响应 (成功):
{ "success": true, "message": "投票成功！", "vote": {...} }

响应 (失败):
{ "error": "您已经投过票了！每人只能投一次", "voted": true }
```

### 检查是否已投票
```
GET /api/check-voter/{名字}

响应:
{ "voted": true/false }
```

### 获取统计结果
```
GET /api/stats

响应:
{
  "total_votes": 10,
  "stats": {
    "best_employee": {
      "张三": 3,
      "李四": 2,
      ...
    },
    "best_team": {
      "护栏一队": 5,
      "标志二队": 3,
      ...
    }
  }
}
```

---

## ⚠️ 常见问题

### Q: 为什么说"无法连接到投票服务器"？
**A:** 说明后端服务未启动。请在另一个终端运行 `node server.js`

### Q: 投票数据存在哪里？
**A:** 存储在 `votes.json` 文件中（自动生成）。这是一个纯 JSON 文件，可以直接编辑或备份

### Q: 如何清空所有投票数据？
**A:** 删除 `votes.json` 文件，系统会自动重新生成

### Q: 可以修改已投票的记录吗？
**A:** 目前不支持修改。如要修改，需要手动编辑 `votes.json` 或删除重新来过

### Q: 支持多人同时投票吗？
**A:** 支持！后端会为每个人独立记录投票状态

---

## 💾 数据备份

投票过程中会自动生成 `votes.json`，格式示例：

```json
{
  "votes": [
    {
      "voter": "张三",
      "best_employee": "李四",
      "best_team": "护栏一队",
      "timestamp": "2024-03-16 10:30:00"
    },
    {
      "voter": "王五",
      "best_employee": "刘六",
      "best_team": "标志二队",
      "timestamp": "2024-03-16 10:31:15"
    }
  ],
  "stats": {
    "best_employee": {
      "李四": 1,
      "刘六": 1
    },
    "best_team": {
      "护栏一队": 1,
      "标志二队": 1
    }
  }
}
```

建议定期备份 `votes.json` 文件！

---

## 🎉 完成！

现在你有一个完整的防刷投票系统：
- ✅ 防止重复投票（同一个人刷新后无法再投）
- ✅ 实时统计结果（自动刷新）
- ✅ 数据永久保存（votes.json）
- ✅ 简洁友好的界面

祝振邦20周年庆典圆满成功！🎊
