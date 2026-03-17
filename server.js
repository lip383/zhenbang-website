const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// 投票数据存储路径
const VOTES_FILE = path.join(__dirname, 'votes.json');

// 初始化投票数据文件
function initVotesFile() {
  if (!fs.existsSync(VOTES_FILE)) {
    fs.writeFileSync(VOTES_FILE, JSON.stringify({
      votes: [],  // { voter: '张三', best_employee: '李四', best_team: '护栏一队', timestamp: '2024-03-16 10:30:00' }
      stats: {
        best_employee: {},
        best_team: {}
      }
    }, null, 2));
  }
}

// 读取投票数据
function getVotes() {
  initVotesFile();
  const data = fs.readFileSync(VOTES_FILE, 'utf-8');
  return JSON.parse(data);
}

// 保存投票数据
function saveVotes(data) {
  fs.writeFileSync(VOTES_FILE, JSON.stringify(data, null, 2));
}

// 更新统计数据
function updateStats(data) {
  data.stats.best_employee = {};
  data.stats.best_team = {};
  
  data.votes.forEach(vote => {
    if (vote.best_employee) {
      data.stats.best_employee[vote.best_employee] = (data.stats.best_employee[vote.best_employee] || 0) + 1;
    }
    if (vote.best_team) {
      data.stats.best_team[vote.best_team] = (data.stats.best_team[vote.best_team] || 0) + 1;
    }
  });
}

// API：提交投票
app.post('/api/vote', (req, res) => {
  const { voter, best_employee, best_team } = req.body;
  
  if (!voter) {
    return res.status(400).json({ error: '投票人姓名不能为空' });
  }
  
  const data = getVotes();
  
  // 检查该用户是否已投票
  const existingVote = data.votes.find(v => v.voter === voter);
  if (existingVote) {
    return res.status(400).json({ 
      error: '您已经投过票了！每人只能投一次',
      voted: true
    });
  }
  
  // 添加新投票
  const newVote = {
    voter,
    best_employee: best_employee || null,
    best_team: best_team || null,
    timestamp: new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
  };
  
  data.votes.push(newVote);
  updateStats(data);
  saveVotes(data);
  
  res.json({ 
    success: true, 
    message: '投票成功！',
    vote: newVote
  });
});

// API：检查用户是否已投票
app.get('/api/check-voter/:name', (req, res) => {
  const name = decodeURIComponent(req.params.name);
  const data = getVotes();
  const voted = data.votes.some(v => v.voter === name);
  
  res.json({ voted });
});

// API：获取投票统计结果
app.get('/api/stats', (req, res) => {
  const data = getVotes();
  res.json({
    total_votes: data.votes.length,
    stats: data.stats
  });
});

// API：获取所有投票记录（仅管理员）
app.get('/api/votes', (req, res) => {
  const data = getVotes();
  res.json(data.votes);
});

// 启动服务器
const PORT = 8900;
app.listen(PORT, () => {
  console.log(`✅ 投票服务器运行在 http://localhost:${PORT}`);
  console.log(`📊 查看统计结果: http://localhost:${PORT}/stats.html`);
});
