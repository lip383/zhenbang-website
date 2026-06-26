import json
import requests
import time

# 湖南路路口坐标（起点）
hunnan_lat, hunnan_lng = 21.4887550, 109.1308799

# 北京路路口坐标（终点）
beijing_lat, beijing_lng = 21.4807384, 109.1151515

# 构造Overpass API查询：获取北部湾路在湖南路和北京路之间的路段
# 使用bbox限定区域
min_lat = min(hunnan_lat, beijing_lat) - 0.005
min_lng = min(hunnan_lng, beijing_lng) - 0.005
max_lat = max(hunnan_lat, beijing_lat) + 0.005
max_lng = max(hunnan_lng, beijing_lng) + 0.005

overpass_query = f"""
[out:json][timeout:25];
(
  way["name"="北部湾路"]({min_lat},{min_lng},{max_lat},{max_lng});
);
out geom;
"""

print("正在查询OSM Overpass API...")
print(f"查询区域: [{min_lat:.4f}, {min_lng:.4f}] to [{max_lat:.4f}, {max_lng:.4f}]")

try:
    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data=overpass_query,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    
    print(f"OSM返回了 {len(data.get('elements', []))} 个元素")
    
    # 保存原始OSM数据
    with open('osm_hunnan_beijing.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("已保存OSM原始数据到 osm_hunnan_beijing.json")
    
    # 提取道路几何
    ways = []
    for elem in data.get('elements', []):
        if elem.get('type') == 'way' and 'geometry' in elem:
            ways.append(elem)
    
    print(f"找到 {len(ways)} 条道路路段")
    
    if ways:
        # 合并所有路段的坐标
        all_coords = []
        for way in ways:
            for point in way.get('geometry', []):
                all_coords.append((point['lat'], point['lon']))
        
        # 去重并排序（简单处理：按纬度排序，因为北部湾路是东西向）
        unique_coords = list(set(all_coords))
        unique_coords.sort(key=lambda x: x[1])  # 按经度排序
        
        print(f"合并后共有 {len(unique_coords)} 个唯一坐标点")
        print(f"起点附近: {unique_coords[0]}")
        print(f"终点附近: {unique_coords[-1]}")
        
        # 保存路径数据
        path_data = {
            "start": (hunnan_lat, hunnan_lng),
            "end": (beijing_lat, beijing_lng),
            "path": unique_coords
        }
        
        with open('hunnan_beijing_path.json', 'w', encoding='utf-8') as f:
            json.dump(path_data, f, ensure_ascii=False, indent=2)
        
        print("已保存路径数据到 hunnan_beijing_path.json")
    else:
        print("未找到道路数据，将使用模拟路径")
        
except Exception as e:
    print(f"查询OSM失败: {e}")
    print("将使用模拟路径生成数据")
