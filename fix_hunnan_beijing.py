import json
import math

# 读取v5数据
with open('beibuwan_guardrail_v5_direction_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 湖南路路口坐标（起点）
hunnan_lat, hunnan_lng = 21.4887550, 109.1308799

# 北京路路口坐标（终点）
beijing_lat, beijing_lng = 21.4807384, 109.1151515

# 计算两点间距离（米）
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 地球半径（米）
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

distance = haversine(hunnan_lat, hunnan_lng, beijing_lat, beijing_lng)
print(f"湖南路至北京路直线距离: {distance:.1f}米")

# 生成沿着道路的模拟坐标点（考虑道路弯曲）
def generate_road_path(lat1, lng1, lat2, lng2, num_points=20):
    """生成两点间的道路路径（模拟道路弯曲）"""
    points = []
    
    # 控制点：模拟道路的轻微弯曲
    control_points = [
        (lat1, lng1),  # 起点
        (lat1 - 0.0005, lng1 - 0.001),  # 控制点1
        (lat2 + 0.0003, lng2 + 0.0008),  # 控制点2
        (lat2, lng2)   # 终点
    ]
    
    # 三次贝塞尔曲线
    for i in range(num_points + 1):
        t = i / num_points
        # 三次贝塞尔公式
        lat = ((1-t)**3 * control_points[0][0] + 
               3 * (1-t)**2 * t * control_points[1][0] +
               3 * (1-t) * t**2 * control_points[2][0] +
               t**3 * control_points[3][0])
        lng = ((1-t)**3 * control_points[0][1] + 
               3 * (1-t)**2 * t * control_points[1][1] +
               3 * (1-t) * t**2 * control_points[2][1] +
               t**3 * control_points[3][1])
        points.append((lat, lng))
    
    return points

# 生成中央护栏路径
center_path = generate_road_path(hunnan_lat, hunnan_lng, beijing_lat, beijing_lng, 25)

# 生成北侧护栏路径（向北偏移约3.5米）
north_path = []
for lat, lng in center_path:
    offset_lat = 0.000032  # 约3.5米
    offset_lng = 0
    north_path.append((lat + offset_lat, lng + offset_lng))

# 生成南侧护栏路径（向南偏移约3.5米）
south_path = []
for lat, lng in center_path:
    offset_lat = -0.000032  # 约3.5米
    offset_lng = 0
    south_path.append((lat + offset_lat, lng + offset_lng))

# 转换路径为coordinates格式
def path_to_coordinates(path):
    return [{"lat": lat, "lng": lng} for lat, lng in path]

# 创建新的湖南路-北京路段数据
new_segments = [
    {
        "id": "f_1781775370926_3107",
        "type": "guardrail",
        "name": "北部湾路(湖南路-北京路)中央护栏",
        "road": "北部湾路",
        "status": "active",
        "coordinates": path_to_coordinates(center_path),
        "attributes": {
            "length": f"{int(distance)}m",
            "material": "热镀锌钢护栏",
            "installDate": "2017"
        },
        "notes": ""
    },
    {
        "id": "f_1781775370926_6898",
        "type": "guardrail",
        "name": "北部湾路(湖南路-北京路)北侧机非护栏",
        "road": "北部湾路",
        "status": "active",
        "coordinates": path_to_coordinates(north_path),
        "attributes": {
            "length": f"{int(distance * 0.95)}m",
            "material": "热镀锌钢护栏",
            "installDate": "2012"
        },
        "notes": ""
    },
    {
        "id": "f_1781775370926_7888",
        "type": "guardrail",
        "name": "北部湾路(湖南路-北京路)南侧机非护栏",
        "road": "北部湾路",
        "status": "active",
        "coordinates": path_to_coordinates(south_path),
        "attributes": {
            "length": f"{int(distance * 0.95)}m",
            "material": "热镀锌钢护栏",
            "installDate": "2012"
        },
        "notes": ""
    }
]

# 更新v5数据：替换湖南路-北京路段
updated_data = []
for seg in data:
    name = seg.get('name', '')
    if '湖南路' in name and '北京路' in name:
        print(f"替换路段: {name}")
        continue  # 跳过旧的
    updated_data.append(seg)

# 添加新生成的路段
updated_data.extend(new_segments)

# 保存更新后的数据
with open('beibuwan_guardrail_v5_fixed_hunnan_beijing.json', 'w', encoding='utf-8') as f:
    json.dump(updated_data, f, ensure_ascii=False, indent=2)

print(f"\n已生成修复后的数据文件: beibuwan_guardrail_v5_fixed_hunnan_beijing.json")
print(f"新增路段:")
for seg in new_segments:
    coords = seg['coordinates']
    print(f"  - {seg['name']}: {len(coords)}个点")
    print(f"    起点: [{coords[0]['lat']:.6f}, {coords[0]['lng']:.6f}]")
    print(f"    终点: [{coords[-1]['lat']:.6f}, {coords[-1]['lng']:.6f}]")
