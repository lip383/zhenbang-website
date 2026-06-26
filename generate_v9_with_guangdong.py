import json
import math

# ========== 第二步：更新路口列表 ==========
# 广东路大致位置（北部湾路和广东路交叉口）
# 通过推算：湖南路109.1308, 北京路109.1151, 广东路应该在中间
# 广东路经度约 109.122 附近

guangdong_est = (21.4845, 109.122)  # 估算的广东路路口坐标

print("正在估算广东路路口坐标...")
print(f"估算位置: [{guangdong_est[0]}, {guangdong_est[1]}]")

# 通过OSM查询验证（尝试获取广东路道路坐标）
overpass_query = """
[out:json][timeout:25];
way["name"="广东路"](21.470,109.100,21.500,109.140);
out center;
"""

try:
    resp = requests.post("https://overpass.kumi.systems/api/interpreter", 
                       data=overpass_query, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        for elem in data.get('elements', []):
            if elem.get('type') == 'way' and 'center' in elem:
                center = elem['center']
                print(f"OSM广东路中心: [{center['lat']:.6f}, {center['lon']:.6f}]")
                # 北部湾路应该在纬度21.48左右与广东路相交
                guangdong_est = (round(center['lat'], 6), round(center['lon'], 6))
except Exception as e:
    print(f"OSM查询失败，使用估算值: {e}")

# ========== 第二步：更新路口列表 ==========
intersections = {
    "南珠大道": (21.5038062, 109.1653651),
    "河南路":   (21.4986554, 109.1536653),
    "上海路":   (21.4920768, 109.1386449),
    "湖南路":   (21.4887550, 109.1308799),
    "广东路":   (21.4845000, 109.1220000),  # 新增！
    "北京路":   (21.4807384, 109.1151515),
    "四川路":   (21.4746357, 109.1077164),
    "贵州路":   (21.4727787, 109.1018128),
    "西藏路":   (21.4691669, 109.0896839),
}

print(f"\n广东路路口坐标: [{intersections['广东路'][0]}, {intersections['广东路'][1]}]")
print("(如果与实际不符，请告诉我准确坐标)\n")

# ========== 第三步：重新定义路段（现在9个路口，8段路）==========
segments = [
    ("南珠大道", "河南路"),
    ("河南路", "上海路"),
    ("上海路", "湖南路"),
    ("湖南路", "广东路"),    # 新增
    ("广东路", "北京路"),    # 新增
    ("北京路", "四川路"),
    ("四川路", "西藏路"),
]

# ========== 第四步：生成路径（含弯曲）==========

def haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dlam = math.radians(lng2-lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generate_path(start, end, num_points=40, curve_params=None):
    """生成带弯曲的路径"""
    lat1, lng1 = start
    lat2, lng2 = end
    
    path = []
    for i in range(num_points + 1):
        t = i / num_points
        
        # 基础线性插值
        lat = lat1 + (lat2 - lat1) * t
        lng = lng1 + (lng2 - lng1) * t
        
        # 应用弯曲
        if curve_params:
            center = curve_params.get('center', 0.5)
            width = curve_params.get('width', 0.3)
            dist = abs(t - center)
            
            if dist < width:
                sigma = width / 2.5
                factor = math.exp(-(dist**2) / (2*sigma*sigma))
                
                if 'lat_offset' in curve_params:
                    if curve_params.get('direction') == 's':
                        lat -= curve_params['lat_offset'] * factor
                    else:
                        lat += curve_params['lat_offset'] * factor
                
                if 'lng_offset' in curve_params:
                    lng += curve_params['lng_offset'] * factor
        
        path.append((round(lat, 6), round(lng, 6)))
    
    return path

def offset_path(path, meters=3.5, side='north'):
    offset_deg = meters / 111000
    result = []
    for lat, lng in path:
        if side == 'north':
            result.append((round(lat+offset_deg, 6), round(lng, 6)))
        else:
            result.append((round(lat-offset_deg, 6), round(lng, 6)))
    return result

def to_coords(path):
    return [{"lat": lat, "lng": lng} for lat, lng in path]

# 路段弯曲配置（根据地图观察）
curve_configs = {
    ("南珠大道", "河南路"): {"center": 0.45, "width": 0.35, "lat_offset": 0.00012, "lng_offset": 0.00005, "direction": "s"},
    ("河南路", "上海路"): {"center": 0.5, "width": 0.3, "lat_offset": 0.00010, "lng_offset": 0.00004, "direction": "s"},
    ("上海路", "湖南路"): {"center": 0.4, "width": 0.25, "lat_offset": 0.00008, "lng_offset": 0.00003, "direction": "n"},
    ("湖南路", "广东路"): {"center": 0.5, "width": 0.4, "lat_offset": 0.00030, "lng_offset": 0.00015, "direction": "s"},  # 中山公园段
    ("广东路", "北京路"): {"center": 0.5, "width": 0.35, "lat_offset": 0.00020, "lng_offset": 0.00010, "direction": "s"},  # 继续弯曲
    ("北京路", "四川路"): {"center": 0.5, "width": 0.28, "lat_offset": 0.00009, "lng_offset": 0.00004, "direction": "n"},
    ("四川路", "西藏路"): {"center": 0.35, "width": 0.30, "lat_offset": 0.00010, "lng_offset": 0.00005, "direction": "s"},
}

# 生成所有护栏
all_segments = []

for start_name, end_name in segments:
    p1 = intersections[start_name]
    p2 = intersections[end_name]
    dist = haversine(p1[0], p1[1], p2[0], p2[1])
    
    curve = curve_configs.get((start_name, end_name))
    num_pts = 45 if curve and curve.get('lat_offset', 0) > 0.00015 else 35
    
    center_path = generate_path(p1, p2, num_pts, curve)
    north_path = offset_path(center_path, 3.5, 'north')
    south_path = offset_path(center_path, 3.5, 'south')
    
    base_id = f"v9_{start_name}_{end_name}"
    
    for suffix, path, install_year in [
        ("中央护栏", center_path, "2017"),
        ("北侧机非护栏", north_path, "2012"),
        ("南侧机非护栏", south_path, "2012"),
    ]:
        all_segments.append({
            "id": f"{base_id}_{suffix[:2]}",
            "type": "guardrail",
            "name": f"北部湾路({start_name}-{end_name}){suffix}",
            "road": "北部湾路",
            "status": "active",
            "coordinates": to_coords(path),
            "attributes": {
                "length": f"{int(dist) if suffix=='中央护栏' else int(dist*0.95)}m",
                "material": "热镀锌钢护栏",
                "installDate": install_year
            },
            "notes": f"v9: {(len(path))}pts, 广东路已加入"
        })
    
    print(f"{start_name}-{end_name}: {dist:.0f}m, {num_pts}pts")

# 保存
with open('beibuwan_guardrail_v9_with_guangdong.json', 'w', encoding='utf-8') as f:
    json.dump(all_segments, f, ensure_ascii=False, indent=2)

print(f"\n✅ v9已生成（含广东路）: beibuwan_guardrail_v9_with_guangdong.json")
print(f"共 {len(all_segments)} 条护栏记录")
print(f"\n⚠️ 注意：广东路路口坐标是估算的！")
print(f"   如果位置不对，请告诉我准确的GPS坐标（纬度,经度）")
