#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试投票系统"""
import urllib.request
import json

BASE = 'http://localhost:8900'

print("=" * 50)
print("投票系统测试")
print("=" * 50)

# 测试 1: 提交投票
print("\n[1] 测试提交投票...")
try:
    data = json.dumps({
        'voter': '测试用户1',
        'best_employee': '李明',
        'best_team': '销售团队'
    }).encode('utf-8')
    req = urllib.request.Request(f'{BASE}/api/vote', data=data, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode('utf-8'))
    print(f"✓ 投票成功: {result}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试 2: 检查已投票
print("\n[2] 测试检查已投票...")
try:
    resp = urllib.request.urlopen(f'{BASE}/api/check-voter/测试用户1')
    result = json.loads(resp.read().decode('utf-8'))
    print(f"✓ 检查结果: {result}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试 3: 重复投票（应该失败）
print("\n[3] 测试重复投票（应该失败）...")
try:
    data = json.dumps({
        'voter': '测试用户1',
        'best_employee': '王五',
        'best_team': '技术团队'
    }).encode('utf-8')
    req = urllib.request.Request(f'{BASE}/api/vote', data=data, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode('utf-8'))
    print(f"✗ 不应该成功: {result}")
except urllib.error.HTTPError as e:
    result = json.loads(e.read().decode('utf-8'))
    print(f"✓ 正确拒绝: {result}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试 4: 获取统计
print("\n[4] 测试获取统计...")
try:
    resp = urllib.request.urlopen(f'{BASE}/api/stats')
    result = json.loads(resp.read().decode('utf-8'))
    print(f"✓ 统计数据: {result}")
except Exception as e:
    print(f"✗ 失败: {e}")

print("\n" + "=" * 50)
print("测试完成！如果都显示 ✓，说明服务器正常工作。")
print("=" * 50)
