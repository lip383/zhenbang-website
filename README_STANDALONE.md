# 🗳️ 投票系统 — 完整使用指南

## 问题解决总结

### ✅ 问题 1: 提交投票时出现"无法连接投票服务器"错误
**原因**: 原版本需要启动 Node.js 后端服务器

**解决方案**: 已创建**完全独立的 localStorage 版本**，无需任何后端，直接在浏览器中运行！

### ✅ 问题 2: 刷新后同个人还能投票
**解决方案**: 所有投票数据存储在浏览器的 localStorage，刷新后会自动检测已投票状态

---

## 🚀 立即使用 (3 步)

### 第 1 步：确保网页服务器在运行
```bash
# 进入项目目录
cd C:\Users\Administrator\WorkBuddy\anniversary

# 启动 Python HTTP 服务器 (Windows)
python -m http.server 8899

# 或用其他方式（如 VSCode Live Server、Nginx 等）
```

### 第 2 步：打开投票页面
在浏览器中访问：
```
http://localhost:8899/vote_standalone.html
```

### 第 3 步：查看投票统计
在浏览器中访问：
```
http://localhost:8899/stats_standalone.html
```

---

## 📋 功能说明

### 投票页面 (`vote_standalone.html`)
✅ 选择投票人姓名
✅ 为最佳员工投票（单选）
✅ 为优秀团队投票（单选）
✅ 提交投票
✅ 防刷：同一个人刷新后无法重复投票

### 统计页面 (`stats_standalone.html`)
✅ 显示总投票数
✅ 显示参与投票人数
✅ 显示参与度百分比
✅ 显示最佳员工 TOP 5 排行榜
✅ 显示优秀团队 TOP 5 排行榜
✅ 显示详细投票记录表
✅ 支持数据导出为 JSON
✅ 每 5 秒自动刷新一次

---

## 💾 数据存储位置

所有投票数据都存储在**浏览器的 localStorage** 中：
- 投票列表: `anniversary_votes`
- 已投票用户: `anniversary_voted_users`

**优点**:
- ✅ 不需要数据库
- ✅ 不需要后端服务器
- ✅ 数据永久保存（除非手动清空浏览器数据）
- ✅ 支持多个浏览器标签页同时投票

**查看数据方法**:
1. 打开投票页面
2. 按 `F12` 打开开发者工具
3. 进入 "Application" 或 "存储" 标签
4. 找到 "Local Storage" → `http://localhost:8899`
5. 查看 `anniversary_votes` 和 `anniversary_voted_users`

---

## 🔧 常见问题

### Q1: 如何清空所有投票数据？
```javascript
// 在浏览器控制台 (F12) 执行:
localStorage.removeItem('anniversary_votes');
localStorage.removeItem('anniversary_voted_users');
```

### Q2: 如何导出投票数据？
在统计页面中点击 **"💾 导出数据"** 按钮，会下载 JSON 文件

### Q3: 如何让其他设备也能访问投票系统？
将 `http://localhost:8899` 改为 **当前电脑的 IP 地址**：
1. 打开命令行，输入 `ipconfig` 查看本地 IP （如 `192.168.1.100`）
2. 其他设备访问: `http://192.168.1.100:8899/vote_standalone.html`

### Q4: 为什么统计页面的参与度是 0%？
统计页面中的总人数是硬编码为 15 人，如需修改请编辑 `stats_standalone.html`，找到这一行：
```javascript
const totalVoters = 15; // 改为实际人数
```

### Q5: 支持多少个并发投票？
没有限制！localStorage 支持无限并发

---

## 🛡️ 防刷机制

系统的防刷原理：

1. **投票时检查**：点击"提交"时，检查 `anniversary_voted_users` 中是否存在该投票人
2. **下拉框变化检查**：选择新的投票人时，自动检查是否已投票
3. **页面加载检查**：刷新页面后，自动检查选中的投票人是否已投票
4. **永久记录**：所有投票数据存储在 localStorage，关机重启也不会丢失

**特点**:
- ✅ 同一个人永远只能投 1 次（即使刷新页面也无法绕过）
- ✅ 关闭浏览器后再打开，投票记录依然存在
- ✅ 不需要任何后端验证

---

## 📁 文件清单

| 文件 | 说明 |
|------|------|
| `vote_standalone.html` | 投票页面（推荐使用） |
| `stats_standalone.html` | 统计页面（推荐使用） |
| `vote.html` | 原版投票页面（需要后端）|
| `stats.html` | 原版统计页面（需要后端） |
| `server_simple.py` | Python 后端服务器（可选） |
| `run_server.bat` | 启动后端的批处理文件（可选） |

---

## 🎯 推荐方案

对于你的场景（20周年庆典投票），推荐使用：
- **投票页面**: `http://localhost:8899/vote_standalone.html` ✅
- **统计页面**: `http://localhost:8899/stats_standalone.html` ✅

**不需要启动任何后端服务器**，只需 Python 的 HTTP 服务器即可！

---

## 🚦 故障排查

### 症状 1: 页面无法加载
**解决**: 确保 HTTP 服务器已启动
```bash
cd C:\Users\Administrator\WorkBuddy\anniversary
python -m http.server 8899
```

### 症状 2: 投票数据丢失
**原因**: 浏览器数据被清空
**解决**: 使用浏览器隐私模式之外的普通模式

### 症状 3: 统计页面显示数据不更新
**原因**: 浏览器缓存问题
**解决**: 按 `Ctrl+Shift+Delete` 清空缓存，或在统计页面点击"🔄 刷新统计"

---

## 🎉 你现在拥有

✅ 完全防刷的投票系统（无需后端）
✅ 实时显示投票排行
✅ 永久数据存储
✅ 支持多设备访问
✅ 数据导出功能
✅ 易于管理和扩展

祝振邦 20 周年庆典圆满成功！🎊
