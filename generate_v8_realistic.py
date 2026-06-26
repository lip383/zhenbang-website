import json
import math

# 8个路口真实GPS坐标 (WGS-84)
intersections = {
    "南珠大道": (21.5038062, 109.1653651),
    "河南路":   (21.4986554, 109.1536653),
    "上海路":   (21.4920768, 109.1386449),
    "湖南路":   (21.4887550, 109.1308799),
    "北京路":   (21.4807384, 109.1151515),
    "四川路":   (21.4746357, 109.1077164),
    "贵州路":   (21.4727787, 109.1018128),
    "西藏路":   (21.4691669, 109.0896839),
}

def haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dlam = math.radians(lng2-lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generate_realistic_path(start, end, num_points=40, bend_config=None):
    """
    生成贴近真实道路的路径
    
    bend_config: None 或 dict {
        'center': 0.0~1.0,      # 弯曲中心位置(比例)
        'width': 0.0~1.0,       # 弯曲宽度(比例)
        'max_lat_offset': float,# 最大纬度偏移(度)
        'max_lng_offset': float,# 最大经度偏移(度)  
        'direction': 's' or 'n' # 向南或向北弯
    }
    """
    lat1, lng1 = start
    lat2, lng2 = end
    
    path = []
    for i in range(num_points + 1):
        t = i / num_points
        
        # 基础插值
        lat = lat1 + (lat2 - lat1) * t
        lng = lng1 + (lng2 - lng1) * t
        
        # 应用弯曲
        if bend_config:
            center = bend_config['center']
            width = bend_config['width']
            dist = abs(t - center)
            
            if dist < width:
                # 高斯弯曲曲线
                sigma = width / 2.5
                factor = math.exp(-(dist**2)/(2*sigma*sigma))
                
                ml = bend_config.get('max_lat_offset', 0)
                mg = bend_config.get('max_lng_offset', 0)
                d = bend_config.get('direction', 's')
                
                if d == 's':
                    lat -= ml * factor
                else:
                    lat += ml * factor
                lng += mg * factor
        
        path.append((round(lat, 6), round(lng, 6)))
    
    return path

def offset_path(path, meters=3.5, side='north'):
    offset_deg = meters / 111000
    result = []
    for lat, lng in path:
        if side == 'north':
            result.append((round(lat+offset_deg,6), round(lng,6)))
        else:
            result.append((round(lat-offset_deg,6), round(lng,6)))
    return result

def to_coords(path):
    return [{"lat": lat, "lng": lng} for lat, lng in path]

# ========== 核心配置：每段路的弯曲参数（根据地图观察精细调整）==========
# 
# 从截图观察到的北部湾路特征：
# 1. 整体走向：西北→东南倾斜（非纯正东西）
# 2. 湖南路-北京路：经过中山公园北侧，有明显的向南大弧形弯曲
# 3. 弯曲中心约在路段55%处（靠近公园中心），弯曲幅度很大

segment_configs = [
    {
        "start": "南珠大道", "end": "河南路",
        "bend": {"center": 0.45, "width": 0.35, "max_lat_offset": 0.00012, 
                 "max_lng_offset": 0.00005, "direction": "s"},
        "points": 35,
        "desc": "轻微S弯"
    },
    {
        "start": "河南路", "end": "上海路",
        "bend": {"center": 0.5, "width": 0.3, "max_lat_offset": 0.00010,
                 "max_lng_offset": 0.00004, "direction": "s"},
        "points": 38,
        "desc": "轻微弯曲"
    },
    {
        "start": "上海路", "end": "湖南路",  
        "bend": {"center": 0.4, "width": 0.25, "max_lat_offset": 0.00008,
                 "max_lng_offset": 0.00003, "direction": "n"},
        "points": 28,
        "desc": "轻微北弯"
    },
    {
        "start": "湖南路", "end": "北京路",
        # 关键路段！中山公园南侧有大弧形弯曲
        "bend": {"center": 0.52, "width": 0.45, 
                 "max_lat_offset": 0.00042,   # 约46米南偏（加大弯曲幅度！）
                 "max_lng_offset": 0.00018,   # 约15米东偏
                 "direction": "s"},
        "points": 45,  # 更多点以平滑大弯曲
        "desc": "★中山公园大弧形弯（向南）"
    },
    {
        "start": "北京路", "end": "四川路",
        "bend": {"center": 0.5, "width": 0.28, "max_lat_offset": 0.00009,
                 "max_lng_offset": 0.00004, "direction": "n"},
        "points": 32,
        "desc": "轻微北弯"
    },
    {
        "start": "四川路", "end": "西藏路",
        "bend": {"center": 0.35, "width": 0.30, "max_lat_offset": 0.00010,
                 "max_lng_offset": 0.00005, "direction": "s"},
        "points": 40,
        "desc": "S形弯曲"
    },
]

# 生成护栏数据
all_segments = []

for cfg in segment_configs:
    s_name = cfg["start"]
    e_name = cfg["end"]
    p1 = intersections[s_name]
    p2 = intersections[e_name]
    
    dist = haversine(p1[0], p1[1], p2[0], p2[1])
    n_pts = cfg["points"]
    
    # 中央护栏
    center_path = generate_realistic_path(p1, p2, n_pts, cfg["bend"])
    north_path = offset_path(center_path, 3.5, 'north')
    south_path = offset_path(center_path, 3.5, 'south')
    
    bid = f"v8_{s_name}_{e_name}"
    
    all_segments.append({
        "id": f"{bid}_center",
        "type": "guardrail",
        "name": f"北部湾路({s_name}-{e_name})中央护栏",
        "road": "北部湾路",
        "status": "active",
        "coordinates": to_coords(center_path),
        "attributes": {"length": f"{int(dist)}m", "material": "热镀锌钢护栏", "installDate": "2017"},
        "notes": f"v8: {cfg['desc']}, {len(center_path)}pts"
    })
    all_segments.append({
        "id": f"{bid}_north",
        "type": "guardrail",
        "name": f"北部湾路({s_name}-{e_name})北侧机非护栏",
        "road": "北部湾路",
        "status": "active",
        "coordinates": to_coords(north_path),
        "attributes": {"length": f"{int(dist*0.95)}m", "material": "热镀锌钢护栏", "installDate": "2012"},
        "notes": f"v8: {cfg['desc']}, {len(north_path)}pts"
    })
    all_segments.append({
        "id": f"{bid}_south",
        "type": "guardrail",
        "name": f"北部湾路({s_name}-{e_name})南侧机非护栏",
        "road": "北部湾路",
        "status": "active",
        "coordinates": to_coords(south_path),
        "attributes": {"length": f"{int(dist*0.95)}m", "material": "热镀锌钢护栏", "installDate": "2012"},
        "notes": f"v8: {cfg['desc']}, {len(south_path)}pts"
    })
    
    print(f"{s_name}-{e_name}: {dist:.0f}m, {n_pts}pts → {cfg['desc']}")

with open('beibuwan_guardrail_v8_realistic.json', 'w', encoding='utf-8') as f:
    json.dump(all_segments, f, ensure_ascii=False, indent=2)

print(f"\n✅ v8已生成: beibuwan_guardrail_v8_realistic.json")
print(f"共 {len(all_segments)} 条记录")
print(f"\n关键改进：")
print(f"  - 湖南路-北京路: 45个坐标点, 大幅向南弯曲(46米)")
print(f"  - 所有路段: 28-45个坐标点, 高斯曲线平滑过渡")
