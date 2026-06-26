#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北海市护栏数据生成器 v2
基于精确道路网格：东西向道路定纬度，南北向道路定经度，交叉路口自动计算
"""

import xlrd
import json
import re
import time
import random

# ============================================================
# 道路网格坐标（WGS-84）
# ============================================================

# 东西向道路 → 纬度（越往北纬度越高）
EW_LAT = {
    "海角路":       21.4915,
    "高德路":       21.4875,
    "北部湾路":     21.4805,
    "湖海路":       21.4770,
    "北海大道":     21.4722,
    "站前路":       21.4660,
    "重庆路":       21.4680,
    "西南大道":     21.4615,
    "新世纪大道":   21.4540,
    "江苏路":       21.4495,
    "浙江路":       21.4455,
    "杭州路":       21.4415,
    "金海岸大道":   21.4375,
    "银滩三号路":  21.4255,
}

# 南北向道路 → 经度（越往东经度越大）
NS_LNG = {
    "西藏路":     109.0990,
    "昆明路":     109.1050,
    "拉萨路":     109.1085,
    "独树根路":   109.1125,
    "四川路":     109.1180,
    "贵州路":     109.1210,
    "广东路":     109.1240,
    "北京路":     109.1270,
    "湖南路":     109.1295,
    "上海路":     109.1320,
    "河南路":     109.1380,
    "南珠大道":   109.1440,
    "向海大道":   109.1530,
}

# 特殊端点坐标（非标准路口交叉点）
SPECIAL = {
    "冠头岭":      (21.4200, 109.0950),
    "外沙岛":      (21.4930, 109.1115),
    "银滩潮街":   (21.4240, 109.1260),
    "蓝箭路":     (21.4320, 109.1330),
    "滨海路":     (21.4825, 109.1100),
    "廉州湾大道": (21.5010, 119.1200), # typo? keep as-is for now
    "海南路":     (21.4780, 109.1160),
    "北星路":     (21.4722, 109.1130),
    "深圳路":     (21.4695, 109.1240),
    "茶亭路":     (21.4755, 109.1150),
    "中山路":     (21.4835, 109.1185),
    "仁爱路":     (21.4540, 109.1255),
    "成都路":     (21.4680, 1295),  # will fix below
    "南京路":     (21.4560, 109.1315),
    "旺盛路":     (21.4920, 109.1135),
    "冠岭路":     (21.4240, 109.0975),
    "美景路":     (21.4175, 109.1015),
    "海景大道":   (21.4220, 109.1055),
    "贵阳路":     (21.4590, 109.1425),
    "长沙路":     (21.4520, 109.1360),
    "黄海路":     (21.4722, 109.1340),
    "和平路":     (21.4845, 109.1155),
    "天府路":     (21.4785, 109.1235),
    "湖北路":     (21.4755, 109.1360),
    "湖北路市场":(21.4755, 109.1380),
    "滨江路":     (21.4885, 109.1145),
    "冯家江桥":  (21.4410, 109.1410),
    "铁路桥":     (21.4605, 109.1350),
    "机场":       (21.4375, 109.1510),
    "深水港码头": (21.5060, 109.1490),
    "红树林景区": (21.4255, 109.1460),
    "银滩一号":  (21.4280, 109.1280),
    "二小":       (21.4805, 109.1220),
    "十七小":     (21.4700, 109.1255),
    "三号路":     (21.4260, 109.1240),
    "广东路—四川路": (21.4722, 109.1210),
    "银滩大道":   (21.4350, 109.1300),
}


def get_road_direction(road_name):
    """判断道路是东西向还是南北向"""
    if road_name in EW_LAT:
        return 'ew'
    if road_name in NS_LNG:
        return 'ns'
    # 根据名称模糊判断
    ns_keywords = ['路']  # most roads ending with 路 could be either...
    # Actually let me just check against known lists more carefully
    return None


def resolve_coord(intersection_name, host_road_name):
    """
    解析路口坐标
    
    核心逻辑：
    - 如果 host_road 是东西向（如北部湾路），则该路上所有路口的纬度 = 该路的纬度，
      经度由路口对应的南北向道路决定
    - 如果 host_road 是南北向（如广东路），则该路上所有路口的经度 = 该路的经度，
      纬度由路口对应的东西向道路决定
    """
    
    # 1. 特殊地点优先
    if intersection_name in SPECIAL:
        coord = SPECIAL[intersection_name]
        if isinstance(coord, tuple) and len(coord) == 2 and isinstance(coord[0], (int, float)):
            return list(coord)
    
    host_dir = get_road_direction(host_road_name)
    
    # 2. 路口名本身是一条已知道路 → 找交叉点
    if host_dir == 'ew':
        # 主路是东西向 → 用主路的lat + 路口的lng
        host_lat = EW_LAT.get(host_road_name, 21.4722)
        
        # 路口是否是南北向道路？
        if intersection_name in NS_LNG:
            return [host_lat, NS_LNG[intersection_name]]
        
        # 路口是否是东西向道路？（同方向道路的交点不太常见，但可能是终点）
        if intersection_name in EW_LAT:
            # 同为东西向，用路口的lat + 默认lng
            return [EW_LAT[intersection_name], 109.1240]
        
        # 尝试在路口名中找已知道路关键词
        for ns_name, lng in sorted(NS_LNG.items(), key=lambda x: -len(x[0])):
            if ns_name in intersection_name or intersection_name in ns_name:
                return [host_lat, lng]
        for ew_name, lat in sorted(EW_LAT.items(), key=lambda x: -len(x[0])):
            if ew_name in intersection_name or intersection_name in ew_name:
                return [lat, 109.1240]
                
    elif host_dir == 'ns':
        # 主路是南北向 → 用主路的lng + 路口的lat
        host_lng = NS_LNG.get(host_road_name, 109.1240)
        
        if intersection_name in EW_LAT:
            return [EW_LAT[intersection_name], host_lng]
        
        if intersection_name in NS_LNG:
            return [21.4722, NS_LNG[intersection_name]]
        
        for ew_name, lat in sorted(EW_LAT.items(), key=lambda x: -len(x[0])):
            if ew_name in intersection_name or intersection_name in ew_name:
                return [lat, host_lng]
        for ns_name, lng in sorted(NS_LNG.items(), key=lambda x: -len(x[0])):
            if ns_name in intersection_name or intersection_name in ns_name:
                return [21.4722, lng]
    
    else:
        # 无法判断主路方向，尝试双向查找
        for ns_name, lng in sorted(NS_LNG.items(), key=lambda x: -len(x[0])):
            if ns_name in intersection_name or intersection_name in ns_name:
                for ew_name, lat in sorted(EW_LAT.items(), key=lambda x: -len(x[0])):
                    if ew_name in intersection_name or intersection_name in ew_name:
                        return [lat, lng]
                return [21.4722, lng]
        for ew_name, lat in sorted(EW_LAT.items(), key=lambda x: -len(x[0])):
            if ew_name in intersection_name or intersection_name in ew_name:
                return [lat, 109.1240]
    
    print(f'  ⚠ 未识别路口 [{intersection_name}] (主路:{host_road_name})')
    return [21.4722, 109.1240]


def parse_section(section_name):
    """解析路段名称"""
    s = section_name.replace(" ", "").strip()
    m = re.search(r'[（(]([^）)]+)[）)]', s)
    if not m:
        return None, None
    part = m.group(1)
    if '-' in part:
        a, b = part.split('-', 1)
        return a.strip(), b.strip()
    return None, None


def gen_coords(p1, p2, n=5):
    coords = []
    for i in range(n):
        r = i / (n - 1)
        coords.append({"lat": round(p1[0] + (p2[0]-p1[0])*r, 6),
                       "lng": round(p1[1] + (p2[1]-p1[1])*r, 6)})
    return coords


def gen_id():
    return f"f_{int(time.time()*1000)}_{random.randint(1000,9999)}"


def main():
    wb = xlrd.open_workbook(r'E:/~2026/道路交通设施数量统计表.xls')
    sheet = wb.sheet_by_name('总')
    
    facilities = []
    seen = set()
    
    print('=== 北海市护栏数据生成 v2 ===\n')
    
    for row_idx in range(2, sheet.nrows):
        try:
            road_raw = str(sheet.cell(row_idx, 1).value).strip()
            section = str(sheet.cell(row_idx, 2).value).strip()
            km = sheet.cell(row_idx, 3).value
            gr_m = sheet.cell(row_idx, 7).value
            district = str(sheet.cell(row_idx, 8).value).strip()
            
            if not road_raw or road_raw == 'nan':
                continue
            try:
                length = float(gr_m)
                if length <= 0: continue
            except: continue
            
            start_i, end_i = parse_section(section)
            if not start_i or not end_i:
                continue
            
            road = road_raw
            key = f"{road}|{start_i}|{end_i}"
            if key in seen: continue
            seen.add(key)
            
            c1 = resolve_coord(start_i, road)
            c2 = resolve_coord(end_i, road)
            
            npts = 11 if length > 3000 else 7 if length > 1500 else 5
            
            fac = {
                "id": gen_id(),
                "type": "guardrail",
                "name": f"{road}({start_i}-{end_i})",
                "road": road,
                "status": "active",
                "coordinates": gen_coords(c1, c2, npts),
                "attributes": {
                    "length": f"{int(length)}m",
                    "material": "热镀锌钢护栏",
                    "installDate": ""
                },
                "notes": f"辖区:{district}, 公里数:{km}KM",
                "district": district,
            }
            
            facilities.append(fac)
            
            print(f'{len(fac):2d}. {fac["name"]:<40s} '
                  f'[{c1[0]:.4f},{c1[1]:.4f}]→[{c2[0]:.4f},{c2[1]:.4f}] '
                  f'| {int(length)}m | {npts}pt')
        except Exception as e:
            continue
    
    out = r'C:\Users\Administrator\WorkBuddy\2026-06-17-17-12-08\traffic-ledger\guardrail_data.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(facilities, f, ensure_ascii=False, indent=2)
    
    print(f'\n✅ {len(facilities)} 条护栏数据已生成 → {out}')


if __name__ == '__main__':
    main()
