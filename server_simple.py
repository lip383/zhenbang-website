#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

VOTES_FILE = 'votes.json'
vote_lock = threading.Lock()

def load_votes():
    if os.path.exists(VOTES_FILE):
        try:
            with open(VOTES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {}

def save_votes(data):
    with open(VOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/vote':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                voter = data.get('voter', '').strip()
                if not voter:
                    self.send_json(400, {'error': 'voter is empty'}, voted=False)
                    return
                with vote_lock:
                    votes = load_votes()
                    if voter in votes:
                        self.send_json(400, {'error': 'already voted'}, voted=True)
                        return
                    votes[voter] = {'best_employee': data.get('best_employee'), 'best_team': data.get('best_team')}
                    save_votes(votes)
                self.send_json(200, {'message': 'ok'})
            except Exception as e:
                self.send_json(400, {'error': str(e)})
    
    def do_GET(self):
        if self.path.startswith('/api/check-voter/'):
            voter = self.path.replace('/api/check-voter/', '')
            import urllib.parse
            voter = urllib.parse.unquote(voter)
            with vote_lock:
                votes = load_votes()
                self.send_json(200, {'voted': voter in votes})
        elif self.path == '/api/stats':
            with vote_lock:
                votes = load_votes()
                stats = {'best_employee': {}, 'best_team': {}, 'total': len(votes)}
                for voter, v in votes.items():
                    if v.get('best_employee'):
                        stats['best_employee'][v['best_employee']] = stats['best_employee'].get(v['best_employee'], 0) + 1
                    if v.get('best_team'):
                        stats['best_team'][v['best_team']] = stats['best_team'].get(v['best_team'], 0) + 1
                stats['best_employee'] = dict(sorted(stats['best_employee'].items(), key=lambda x: -x[1]))
                stats['best_team'] = dict(sorted(stats['best_team'].items(), key=lambda x: -x[1]))
                self.send_json(200, stats)
    
    def send_json(self, code, data, **kw):
        data.update(kw)
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

httpd = HTTPServer(('', 8900), Handler)
print('Vote server started at http://localhost:8900')
httpd.serve_forever()
