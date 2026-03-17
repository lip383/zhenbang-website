#!/usr/bin/env python3
"""
投票系统后端服务器 (Python 版本)
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

VOTES_FILE = 'votes.json'
PORT = 8900

# 读写锁，防止并发问题
import threading
vote_lock = threading.Lock()

def load_votes():
    """读取投票数据"""
    if os.path.exists(VOTES_FILE):
        try:
            with open(VOTES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_votes(data):
    """保存投票数据"""
    with open(VOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_stats():
    """计算统计数据"""
    votes = load_votes()
    stats = {
        'best_employee': {},
        'best_team': {},
        'total_voters': len(votes)
    }
    
    for voter, vote_data in votes.items():
        # 统计最佳员工
        if vote_data.get('best_employee'):
            name = vote_data['best_employee']
            stats['best_employee'][name] = stats['best_employee'].get(name, 0) + 1
        
        # 统计优秀团队
        if vote_data.get('best_team'):
            name = vote_data['best_team']
            stats['best_team'][name] = stats['best_team'].get(name, 0) + 1
    
    # 排序
    stats['best_employee'] = dict(sorted(stats['best_employee'].items(), key=lambda x: x[1], reverse=True))
    stats['best_team'] = dict(sorted(stats['best_team'].items(), key=lambda x: x[1], reverse=True))
    
    return stats

class VoteHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """处理 POST 请求 (提交投票)"""
        if self.path == '/api/vote':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                voter = data.get('voter', '').strip()
                
                if not voter:
                    self.send_json(400, {'error': '投票者名字不能为空'}, voted=False)
                    return
                
                with vote_lock:
                    votes = load_votes()
                    
                    # 检查是否已投票
                    if voter in votes:
                        self.send_json(400, {'error': f'❌ 抱歉，您已经投过票了，无法重复投票'}, voted=True)
                        return
                    
                    # 保存投票
                    votes[voter] = {
                        'best_employee': data.get('best_employee'),
                        'best_team': data.get('best_team')
                    }
                    save_votes(votes)
                    
                    self.send_json(200, {'message': '投票成功', 'voter': voter})
            except Exception as e:
                self.send_json(400, {'error': f'服务器错误: {str(e)}'}, voted=False)
        else:
            self.send_json(404, {'error': '路径不存在'})
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 检查投票者是否已投票
        if path.startswith('/api/check-voter/'):
            voter = path.replace('/api/check-voter/', '')
            voter = voter.strip('/')
            
            try:
                # URL 解码
                import urllib.parse
                voter = urllib.parse.unquote(voter)
                
                with vote_lock:
                    votes = load_votes()
                    voted = voter in votes
                    self.send_json(200, {'voted': voted, 'voter': voter})
            except Exception as e:
                self.send_json(400, {'error': str(e)})
        
        # 获取统计数据
        elif path == '/api/stats':
            try:
                stats = get_stats()
                self.send_json(200, stats)
            except Exception as e:
                self.send_json(400, {'error': str(e)})
        
        else:
            self.send_json(404, {'error': '路径不存在'})
    
    def send_json(self, status_code, data, **kwargs):
        """发送 JSON 响应"""
        # 合并 kwargs 到 data
        data.update(kwargs)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.wfile.write(response)
    
    def log_message(self, format, *args):
        """简化日志输出"""
        print(f'[{self.address_string()}] {format % args}')

def run_server():
    """启动服务器"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, VoteHandler)
    print("""
====================================================
  投票系统后端服务器已启动
====================================================
  服务地址: http://localhost:8900
  投票页面: http://localhost:8899/vote.html
  统计页面: http://localhost:8899/stats.html
  
  数据存储: votes.json
  按 Ctrl+C 停止服务器
====================================================
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n[OK] 服务器已停止')
        httpd.server_close()

if __name__ == '__main__':
    run_server()
